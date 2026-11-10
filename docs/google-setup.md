# Google Cloud setup for the YouTube pipeline

The console menus change from time to time, so some labels may differ slightly.

## 1. Create a project
1. Go to https://console.cloud.google.com and sign in with the Google account that **owns or manages the YouTube channel**.
2. Click the project picker at the top, then **New Project**.
3. Name it `youtube-s3-pipeline` and click **Create**. Make sure it's selected afterwards.

## 2. Enable the two APIs
1. Open **APIs & Services → Library**.
2. Search for **YouTube Data API v3** and click **Enable**.
3. Search for **YouTube Analytics API** and click **Enable**.

The "YouTube Reporting API" isn't needed. Add it only if you later want bulk reports.

## 3. Configure the OAuth consent screen
This is under **APIs & Services → OAuth consent screen**. Newer consoles call it **Google Auth Platform**.
1. Click **Get started** (or **Configure consent screen**).
2. **App name:** `youtube-s3-pipeline`. **User support email:** your Gmail.
3. **Audience / User type:** choose **External**. A personal Gmail account can't use Internal.
4. **Contact email:** your Gmail. Accept the terms and click **Create**.
5. **Data Access (Scopes):** click **Add or remove scopes** and add:
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/yt-analytics.readonly`
   - Optional, for revenue data: `https://www.googleapis.com/auth/yt-analytics-monetary.readonly`

   If the scopes don't appear in the list, paste them in the "manually add scopes" box.
6. **Test users:** add your own Gmail. This is needed for the first sign-in.

## 4. Publish the app (important)
Under **Audience** (or the consent screen page), click **Publish app** so the status becomes **In production**.
- While the status is **Testing**, refresh tokens **expire after 7 days**, and the pipeline would stop working every week.
- Google verification isn't needed for personal use. Sign-in shows an "unverified app" warning; click **Advanced → Go to youtube-s3-pipeline (unsafe)**. It's your own app. An unverified app is limited to 100 users, which doesn't matter here.

## 5. Create the OAuth client
1. Go to **APIs & Services → Credentials** (or **Clients**).
2. Click **Create credentials → OAuth client ID**.
3. **Application type: Desktop app.** Name it `pipeline-desktop`.
4. Click **Create**, then **Download JSON**.
5. Save it as `client_secret.json` in the repo root. It's already in `.gitignore`. **Never commit or share this file.**

## 6. Get the refresh token
Run from the repo root:
```
pip install google-auth-oauthlib
python scripts/get_refresh_token.py client_secret.json
```
1. A browser opens. Sign in as the channel owner.
2. If your account manages several channels (brand accounts), **pick the channel you want** when prompted.
3. Click through the unverified-app warning, and approve both read-only scopes.
4. The script prints JSON with `client_id`, `client_secret` and `refresh_token`. Copy it for the next step.

## 7. Store it in AWS
```
aws secretsmanager create-secret --region eu-central-1 \
  --name youtube-pipeline/oauth \
  --secret-string '<paste the JSON>'
```

## Gotchas
- **No refresh token printed (`null`):** revoke the app at https://myaccount.google.com/permissions and run the script again. The script already forces consent.
- **`invalid_grant` after about 7 days:** the app is still in Testing. Publish it and redo step 6.
- **`access_denied` / app not verified:** your Gmail isn't in the test users, or you skipped the "Advanced" click-through.
- **Analytics returns 403 or empty results:** the account you signed in with isn't the channel owner, or you picked the wrong brand channel.
- **Quota:** the Data API default is 10,000 units/day, which is plenty for hourly runs. Check it under **APIs & Services → YouTube Data API v3 → Quotas**.
- **Revenue metrics** need the monetary scope and a monetized channel. The current code doesn't request revenue metrics.
