# Intervals.icu Readiness Scorer

This script calculates a daily "readiness" score based on your wellness data from [Intervals.icu](https://intervals.icu) and pushes it back to your calendar. It's designed to provide a single, actionable metric to help guide your training decisions.

The script is designed to be run automatically, for example, using a GitHub Action.

## Features

-   Fetches wellness data from the Intervals.icu API.
-   Calculates a readiness score based on HRV, sleep, stress, and training load (TSB).
-   Pushes the calculated score and a descriptive label back to Intervals.icu as a custom wellness field.
-   Includes robust error handling and diagnostic modes to debug API key permissions.
-   Handles missing data by interpolation and provides warnings.

## How it Works

The script performs the following steps:

1.  **Fetch Data**: It retrieves the last 60 days of your wellness data from the Intervals.icu API.
2.  **Calculate Metrics**:
    -   It calculates a 60-day rolling baseline and standard deviation for your HRV (log-transformed).
    -   It uses this baseline to calculate a z-score for today's HRV, which indicates how your current HRV compares to your recent norm.
3.  **Determine Readiness**: A readiness score (from 1 to 10) and a corresponding label (e.g., "GO_HARD", "REST_LIFESTYLE") are determined based on a series of logic gates that evaluate:
    -   Sleep score
    -   Stress score
    -   Training Stress Balance (TSB)
    -   HRV z-score
4.  **Push Result**: The final score and label are pushed back to Intervals.icu for the current day.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/intervalicu.git
    cd intervalicu
    ```

2.  **Install dependencies:**
    The script requires Python 3 and the following libraries: `requests`, `pandas`, and `numpy`. You can install them using pip:
    ```bash
    pip install requests pandas numpy
    ```

3.  **Set up environment variables:**
    You need to provide your Intervals.icu Athlete ID and an API Key as environment variables.
    -   `INTERVALS_API_KEY`: Your API key from the "Settings" page in Intervals.icu. **Make sure the key has "Wellness" permissions.**
    -   `INTERVALS_ATHLETE_ID`: Your athlete ID (the `i` number, e.g., `i12345`).

    You can set these in your operating system, or if you are using the included GitHub Action, as secrets in your repository.

## Usage

To run the script manually:

```bash
python readiness.py
```

### Automation with GitHub Actions

This repository includes a GitHub Actions workflow in `.github/workflows/daily_readiness.yml` that runs the script automatically every day. To use it:

1.  **Fork this repository.**
2.  **Add your API Key and Athlete ID as repository secrets:**
    -   Go to your repository's "Settings" > "Secrets and variables" > "Actions".
    -   Create a new secret named `INTERVALS_API_KEY` with your API key.
    -   Create a new secret named `INTERVALS_ATHLETE_ID` with your athlete ID.
3.  The action will now run daily at the scheduled time. You can also trigger it manually from the "Actions" tab in your repository.

