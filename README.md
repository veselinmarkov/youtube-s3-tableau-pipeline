# YouTube → S3 → Tableau

EventBridge schedule (hourly by default) → Lambda → CSVs in S3 (`youtube/<dataset>/dt=YYYY-MM-DD/<dataset>.csv`), region eu-central-1.

## One-time setup
1. Google Cloud: enable YouTube Data API v3 + YouTube Analytics API, create a **Desktop** OAuth client, set the consent screen to **In production** (otherwise the refresh token expires after 7 days).
2. `pip install google-auth-oauthlib && python scripts/get_refresh_token.py client_secret.json` (sign in as the channel owner).
3. Store the printed JSON:
   `aws secretsmanager create-secret --region eu-central-1 --name youtube-pipeline/oauth --secret-string '<json>'`
4. AWS OIDC for GitHub: create the GitHub OIDC identity provider and a role trusted for `repo:<owner>/<repo>:ref:refs/heads/main` with deploy permissions (CloudFormation, Lambda, S3, IAM, Events, SAM artifacts bucket). Set the repo variable `AWS_DEPLOY_ROLE_ARN`.
5. Push to `main` → Actions tests and deploys. To go daily, set repo variable `SCHEDULE_EXPRESSION` to `rate(1 day)` and re-run.

## Laptop (Windows)
Create an access key for the `ReaderUser` (see stack outputs), `aws configure --profile youtube-reader`, then schedule `windows/sync.ps1 -Bucket <bucket>` in Task Scheduler. In Tableau connect to the text files in `C:\youtube_data` and use a wildcard union over `dt=*`. Since each day's files are overwritten by later runs, `videos` rows carry `snapshot_ts`.
