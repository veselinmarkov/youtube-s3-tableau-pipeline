#!/bin/bash
# Sync the YouTube CSVs from S3 to a local folder for Tableau (macOS).
# Prereq: AWS CLI installed (brew install awscli) and a profile with the ReaderUser keys:
#   aws configure --profile youtube-reader
# Usage: mac/sync.sh <bucket> [dest-folder]
# Schedule (optional): see the cron/launchd note in README.md.
set -euo pipefail

BUCKET="${1:?Usage: $0 <bucket> [dest-folder]}"
DEST="${2:-$HOME/youtube_data}"

mkdir -p "$DEST"
aws s3 sync "s3://$BUCKET/youtube" "$DEST" \
  --profile youtube-reader --region eu-central-1
echo "Synced to $DEST"
