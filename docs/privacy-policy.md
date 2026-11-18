# Privacy Policy

**App:** youtube-s3-pipeline
**Last updated:** 2026-11-18

## Who this app is for
This app is a private tool built and used by a single person, the owner of the YouTube channel it reads. It is **not open to the public**, and no other users are invited to sign in.

## What data the app accesses
With the channel owner's own consent, the app reads, in read-only mode:
- YouTube channel and video information (titles, publish dates, view, like and comment counts), via the YouTube Data API
- YouTube Analytics metrics for the owner's channel (such as views, watch time and subscriber changes), via the YouTube Analytics API

The app requests only these read-only scopes:
- `https://www.googleapis.com/auth/youtube.readonly`
- `https://www.googleapis.com/auth/yt-analytics.readonly`

## How the data is used and stored
The data is copied on a schedule into the channel owner's own private Amazon Web Services (AWS) account as CSV files, and is used only by the owner for personal analysis (for example, in Tableau). The OAuth credentials are stored in the owner's AWS Secrets Manager.

## Sharing
The data is **not** shared, sold, or disclosed to any third party, and is not used for advertising or to train models.

## Retention and revocation
The data stays in the owner's AWS account until the owner deletes it. Access can be revoked at any time at https://myaccount.google.com/permissions.

## Google API Services User Data Policy
The app's use of information received from Google APIs adheres to the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including the Limited Use requirements.

## Contact
audiovogel@gmail.com
