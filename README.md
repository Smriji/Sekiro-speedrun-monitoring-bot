# Sekiro-speedrun-monitoring-bot
This tool monitors Speedrun.com for new World Records (WR) in SEKIRO and notifies a Discord channel via Webhook. It is designed to run as a Google Cloud Run Job, using Google Cloud Storage (GCS) to persist the current record state.

## Features
- **Automated Monitoring**: Fetches the latest verified runs from the Speedrun.com API.
- **Sub-category Support**: Handles hardware-specific (PC/Console) and custom sub-category variables.
- **Serverless Execution**: Optimized for Google Cloud Run Jobs, minimizing costs by running only when needed.
- **Persistent State**: Stores the WR list in GCS to compare against new runs.

## Prerequisites
- A Google Cloud Project with Cloud Run and Cloud Storage enabled.
- A Discord Webhook URL.
- subcategories.json file defining the categories and variables to monitor.

## Configuration
### Environment Variables
|Variable|Description|
|----|----|
|BUCKET_NAME|The name of the GCS bucket to store wr_list.json.|
|DISCORD_WEBHOOK_URL|Your Discord Webhook URL for notifications.|

### Local Files
- `subcategories.json`: Should be bundled in the container. It contains the category IDs and variable IDs you want to track.
