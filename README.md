# Intervals.icu Readiness Scorer

![Python](https://img.shields.io/badge/python-3.x-blue.svg)


A Python script that calculates a daily "readiness" score based on your wellness data from [Intervals.icu](https://intervals.icu) and pushes it back to your calendar. Designed to provide a single, actionable metric to help guide your training decisions.

---

## 🚀 Features

*   **Automated Data Fetching**: Retrieves the last 60 days of wellness data from the Intervals.icu API.
*   **Advanced Metrics**: Calculates a readiness score based on:
    *   Heart Rate Variability (HRV)
    *   Sleep Score
    *   Stress Score
    *   Training Stress Balance (TSB)
*   **Smart Analysis**: Uses a 60-day rolling baseline and standard deviation for HRV to calculate z-scores.
*   **Actionable Insights**: Pushes a score (1-10) and a descriptive label (e.g., `GO_HARD`, `REST_LIFESTYLE`) back to Intervals.icu.
*   **Robust**: Includes error handling, missing data interpolation, and diagnostic modes.

## 🛠️ How it Works

1.  **Fetch Data**: Pulls historical wellness data.
2.  **Calculate Metrics**: Computes rolling baselines and z-scores for HRV.
3.  **Determine Readiness**: Evaluates logic gates based on Sleep, Stress, TSB, and HRV to assign a score.
4.  **Push Result**: Updates your Intervals.icu calendar with the calculated readiness.

## 📋 Prerequisites

*   Python 3.x
*   `pip` (Python package installer)
*   An [Intervals.icu](https://intervals.icu) account

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/intervalicu.git
    cd intervalicu
    ```

2.  **Install dependencies**
    ```bash
    pip install requests pandas numpy
    ```

3.  **Set up Environment Variables**
    You need to provide your credentials.

    | Variable | Description |
    | :--- | :--- |
    | `INTERVALS_API_KEY` | Your API key from Intervals.icu "Settings". **Must have "Wellness" permissions.** |
    | `INTERVALS_ATHLETE_ID` | Your athlete ID (e.g., `i12345`). |

## 🏃 Usage

### Manual Run
Run the script directly from your terminal:

```bash
python readiness.py
```

### 🤖 Automation (GitHub Actions)
This repository includes a workflow in `.github/workflows/daily_readiness.yml` to run the script daily.

1.  **Fork** this repository.
2.  Go to **Settings > Secrets and variables > Actions**.
3.  Add `INTERVALS_API_KEY` and `INTERVALS_ATHLETE_ID` as repository secrets.
4.  The action will run automatically every day.

## 📂 Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── daily_readiness.yml  # GitHub Actions workflow
├── readiness.py                 # Main script
└── README.md                    # This file
```



