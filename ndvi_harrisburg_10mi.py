name: Daily Harrisburg NDVI Alerts

on:
  schedule:
    # 16:00 UTC = 8:00 AM PST (adjust to 15:00 UTC during PDT / daylight saving)
    - cron: "0 16 * * *"
  workflow_dispatch: # Adds a "Run workflow" button so you can test manually anytime

jobs:
  run-ndvi-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Authenticate Google Earth Engine
        env:
          EE_SERVICE_ACCOUNT_JSON: ${{ secrets.EE_SERVICE_ACCOUNT_JSON }}
        run: |
          echo "$EE_SERVICE_ACCOUNT_JSON" > ee-key.json
          python -c '
          import ee, json
          info = json.load(open("ee-key.json"))
          creds = ee.ServiceAccountCredentials(info["client_email"], "ee-key.json")
          ee.Initialize(creds, project="${{ secrets.GCP_PROJECT_ID }}")
          '

      - name: Run NDVI field triage
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          SEND_EMAIL: "true"
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          ALERT_TO: "andrewbrant34@gmail.com"
        run: python ndvi_harrisburg_10mi.py

      - name: Upload CSV report artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ndvi-alerts-csv
          path: alerts_out/*.csv
name: Test Harrisburg NDVI Alert (9:30 AM PST)

on:
  schedule:
    # 9:30 AM PST = 17:30 UTC (Note: GitHub cron can start a few minutes after the minute)
    - cron: "30 17 * * *"
  workflow_dispatch:
    inputs:
      force_test_email:
        description: "Send test email to andrewbrant34@gmail.com even if 0 fields trigger"
        required: false
        default: "true"
        type: string

jobs:
  test-field-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install earthengine-api geopandas pandas

      - name: Authenticate Google Earth Engine
        env:
          EE_SERVICE_ACCOUNT_JSON: ${{ secrets.EE_SERVICE_ACCOUNT_JSON }}
        run: |
          echo "$EE_SERVICE_ACCOUNT_JSON" > ee-key.json
          python -c '
          import ee, json
          info = json.load(open("ee-key.json"))
          creds = ee.ServiceAccountCredentials(info["client_email"], "ee-key.json")
          ee.Initialize(creds, project="${{ secrets.GCP_PROJECT_ID }}")
          '

      - name: Run immediate field check & alert test
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          SEND_EMAIL: "true"
          FORCE_TEST_EMAIL: ${{ github.event.inputs.force_test_email || 'true' }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          ALERT_TO: "andrewbrant34@gmail.com"
        run: python ndvi_harrisburg_10mi.py

      - name: Upload test CSV output
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: harrisburg-930am-test-csv
          path: alerts_out/*.csv
FORCE_TEST_EMAIL = os.getenv("FORCE_TEST_EMAIL", "false").lower() == "true"
