"""One-off: obtain a refresh token as the channel owner.

Usage: python scripts/get_refresh_token.py client_secret.json
Prints the JSON to store in Secrets Manager (keys: client_id, client_secret, refresh_token).
"""
import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print(json.dumps({
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "refresh_token": creds.refresh_token,
}))
