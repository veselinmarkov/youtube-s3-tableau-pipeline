"""Lambda entry point: pull YouTube data and write CSVs to S3."""
import csv
import io
import json
import os
from datetime import datetime, timezone

import boto3

import youtube_client as yt

CHANNEL_COLS = ["snapshot_ts", "channel_id", "title", "subscribers", "views", "video_count"]
VIDEO_COLS = [
    "snapshot_ts", "video_id", "title", "published_at", "duration",
    "views", "likes", "comments",
]
DAILY_COLS = ["video_id", "day"] + yt.ANALYTICS_METRICS.split(",")


def to_csv(cols: list[str], rows: list[list]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def channel_rows(ch: dict, ts: str) -> list[list]:
    s = ch["statistics"]
    return [[ts, ch["id"], ch["snippet"]["title"], s.get("subscriberCount"),
             s.get("viewCount"), s.get("videoCount")]]


def video_rows(videos: list[dict], ts: str) -> list[list]:
    rows = []
    for v in videos:
        s = v["statistics"]
        rows.append([ts, v["id"], v["snippet"]["title"], v["snippet"]["publishedAt"],
                     v["contentDetails"]["duration"], s.get("viewCount"),
                     s.get("likeCount"), s.get("commentCount")])
    return rows


def put(s3, bucket: str, dataset: str, day: str, body: bytes):
    s3.put_object(
        Bucket=bucket,
        Key=f"youtube/{dataset}/dt={day}/{dataset}.csv",
        Body=body,
        ContentType="text/csv",
    )


def handler(event, context):
    bucket = os.environ["BUCKET"]
    secret_id = os.environ["SECRET_ID"]
    days = int(os.environ.get("ANALYTICS_DAYS", "30"))

    secret = json.loads(
        boto3.client("secretsmanager").get_secret_value(SecretId=secret_id)["SecretString"]
    )
    data, analytics = yt.build_clients(secret)

    now = datetime.now(timezone.utc)
    ts, day = now.isoformat(timespec="seconds"), now.date().isoformat()

    ch = yt.get_channel(data)
    ids = yt.list_video_ids(data, ch["contentDetails"]["relatedPlaylists"]["uploads"])
    videos = yt.get_videos(data, ids)

    daily = []
    for vid in ids:
        for row in yt.get_video_daily(analytics, vid, days):
            daily.append([vid] + row)

    s3 = boto3.client("s3")
    put(s3, bucket, "channel", day, to_csv(CHANNEL_COLS, channel_rows(ch, ts)))
    put(s3, bucket, "videos", day, to_csv(VIDEO_COLS, video_rows(videos, ts)))
    put(s3, bucket, "video_daily_analytics", day, to_csv(DAILY_COLS, daily))

    return {"videos": len(videos), "daily_rows": len(daily)}
