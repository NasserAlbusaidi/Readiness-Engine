import requests
import pandas as pd
import numpy as np
import os
import sys
from datetime import date, timedelta
import base64

# --- CONFIGURATION ---
API_KEY = os.environ.get("INTERVALS_API_KEY", "").strip()
ATHLETE_ID = os.environ.get("INTERVALS_ATHLETE_ID", "").strip()

if not API_KEY or not ATHLETE_ID:
    print("ERROR: Environment variables INTERVALS_API_KEY or INTERVALS_ATHLETE_ID are missing.")
    sys.exit(1)

BASE_URL = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}"

def get_auth_methods():
    return [
        ('API_KEY', API_KEY),           
        (f'u{ATHLETE_ID}', API_KEY)     
    ]

def fetch_with_retry(url):
    auth_methods = get_auth_methods()
    last_error = None
    
    print(f"Requesting: {url}")

    for i, auth in enumerate(auth_methods):
        method_name = "Standard" if auth[0] == 'API_KEY' else "JS-Legacy"
        print(f"Attempt {i+1} ({method_name} Auth)... ", end="")
        
        try:
            r = requests.get(url, auth=auth)
            
            if r.status_code == 200:
                print("✅ Success!")
                return r.json()
            
            elif r.status_code == 403:
                print("❌ 403 Forbidden.")
                last_error = r
                if i == len(auth_methods) - 1:
                    diagnose_403(auth)
            else:
                print(f"❌ Status {r.status_code}")
                last_error = r
                
        except Exception as e:
            print(f"Error: {e}")

    if last_error:
        raise Exception(f"API Failed with {last_error.status_code}: {last_error.text}")
    return None

def diagnose_403(auth):
    print("\n--- 🔍 DIAGNOSTIC MODE ---")
    test_url = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities?limit=1"
    try:
        r = requests.get(test_url, auth=auth)
        if r.status_code == 200:
            print("CRITICAL: API Key works for Activities but FAILS for Wellness.")
            print("ACTION: Generate new Key with 'Wellness' permission checked.")
        else:
            print(f"CRITICAL: Key failed everywhere (Status {r.status_code}). Check Secrets.")
    except:
        print("Diagnostic connection failed.")
    sys.exit(1)

def get_data():
    end_date_str = date.today().isoformat()
    start_date_str = (date.today() - timedelta(days=60)).isoformat()
    
    url = f"{BASE_URL}/wellness?oldest={start_date_str}&newest={end_date_str}"
    
    data = fetch_with_retry(url)

    if isinstance(data, dict):
        data = [data]

    if not data:
        print(f"⚠️ No data found for {start_date_str} to {end_date_str}.")
        return pd.DataFrame(columns=['id', 'ctl', 'atl', 'tsb', 'hrv', 'sleepScore', 'stress'])

    df_well = pd.DataFrame(data)
    
    required_cols = ['ctl', 'atl', 'tsb', 'hrv', 'sleepScore', 'stress']
    for col in required_cols:
        if col not in df_well.columns:
            df_well[col] = np.nan

    df_well['tsb'] = df_well['tsb'].fillna(df_well['ctl'].fillna(0) - df_well['atl'].fillna(0))

    return df_well

def calculate_metrics(df):
    if df.empty: return df

    df['date'] = pd.to_datetime(df['id'])
    df = df.sort_values('date')
    
    # Ironman Context: Interpolate missing HRV
    df['hrv'] = df['hrv'].interpolate(method='linear', limit=3)
    df['hrv_log'] = np.log(df['hrv'])
    
    df['hrv_baseline'] = df['hrv_log'].rolling(window=60, min_periods=20).mean().shift(1)
    df['hrv_std'] = df['hrv_log'].rolling(window=60, min_periods=20).std().shift(1)
    
    return df

def determine_readiness(df):
    if df.empty: return None, None

    today_date = date.today()
    last_entry_date = df.iloc[-1]['date'].date()
    
    if last_entry_date != today_date:
        print(f"⚠️ Data for TODAY ({today_date}) is missing. Last sync was {last_entry_date}.")
        print("Proceeding with latest available data for testing...")

    today = df.iloc[-1]
    
    if pd.isna(today['hrv_std']) or today['hrv_std'] == 0:
        z_score = 0
    else:
        z_score = (today['hrv_log'] - today['hrv_baseline']) / today['hrv_std']

    score = 5
    label = "HOLD"
    
    def safe_get(series, key, default=0):
        val = series.get(key)
        if pd.isna(val): return default
        return val

    sleep_score = safe_get(today, 'sleepScore')
    stress_score = safe_get(today, 'stress')
    tsb = safe_get(today, 'tsb')

    # LOGIC GATES
    if sleep_score > 0 and sleep_score < 40:
        score = 2
        label = "REST_LIFESTYLE"
        print(f"Logic: Sleep Fail (Sleep: {sleep_score})")
    elif stress_score > 85:
        score = 2
        label = "REST_LIFESTYLE"
        print(f"Logic: Stress Fail (Stress: {stress_score})")
    elif tsb < -35: 
        score = 3
        label = "HIGH_RISK_LOAD"
        print(f"Logic: TSB too low ({tsb})")
    elif z_score < -1.5:
        score = 1
        label = "REST_SYMPATHETIC"
        print(f"Logic: Sympathetic Stress (Z: {z_score:.2f})")
    elif z_score > 1.5:
        score = 6
        label = "CAUTION_PARASYMPATHETIC"
        print(f"Logic: Parasympathetic Saturation (Z: {z_score:.2f})")
    elif -1.5 <= z_score <= -0.5:
        score = 7
        label = "TRAIN_EASY"
        print(f"Logic: Slight Fatigue (Z: {z_score:.2f})")
    else:
        score = 10
        label = "GO_HARD"
        print(f"Logic: All Systems Go (Z: {z_score:.2f})")

    return score, label

def push_result(score, label):
    if score is None: return

    today_str = date.today().isoformat()
    url = f"{BASE_URL}/wellness/{today_str}"
    
    # Use standard auth for write as well
    auth = ('API_KEY', API_KEY)
    
    payload = { "HybridScore": score, "ReadinessLabel": label }
    
    print(f"Pushing result to {url}...")
    try:
        r = requests.put(url, json=payload, auth=auth)
        r.raise_for_status()
        print(f"✅ SUCCESS: Intervals.icu updated with Score {score}.")
    except requests.exceptions.HTTPError as e:
        # --- DEBUGGING 422 ERRORS ---
        print(f"❌ ERROR: {e}")
        print(f"Server Response: {e.response.text}") # This prints the exact reason!
        print("TIP: Check 'Settings > Custom Item Fields'. Ensure codes match payload keys.")

if __name__ == "__main__":
    try:
        data = get_data()
        processed_data = calculate_metrics(data)
        score, label = determine_readiness(processed_data)
        push_result(score, label)
    except Exception as e:
        print(f"Execution Failed: {e}")
        sys.exit(1)