"""Thin wrappers around the YouTube Data and Analytics APIs (channel-owner OAuth)."""
from datetime import date, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def build_clients(secret: dict):
    creds = Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    data = build("youtube", "v3", credentials=creds, cache_discovery=False)
    analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    return data, analytics


def get_channel(data) -> dict:
    resp = data.channels().list(
        part="snippet,statistics,contentDetails", mine=True
    ).execute()
    return resp["items"][0]


def list_video_ids(data, uploads_playlist: str) -> list[str]:
    ids, token = [], None
    while True:
        resp = data.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist,
            maxResults=50,
            pageToken=token,
        ).execute()
        ids += [i["contentDetails"]["videoId"] for i in resp["items"]]
        token = resp.get("nextPageToken")
        if not token:
            return ids


def get_videos(data, ids: list[str]) -> list[dict]:
    out = []
    for i in range(0, len(ids), 50):
        resp = data.videos().list(
            part="snippet,statistics,contentDetails", id=",".join(ids[i : i + 50])
        ).execute()
        out += resp["items"]
    return out


ANALYTICS_METRICS = (
    "views,estimatedMinutesWatched,averageViewDuration,"
    "likes,comments,subscribersGained,subscribersLost"
)


def get_video_daily(analytics, video_id: str, days: int) -> list[list]:
    """Daily metrics for one video over the last `days` days."""
    end = date.today()
    start = end - timedelta(days=days)
    resp = analytics.reports().query(
        ids="channel==MINE",
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        metrics=ANALYTICS_METRICS,
        dimensions="day",
        filters=f"video=={video_id}",
        sort="day",
    ).execute()
    return resp.get("rows", [])
