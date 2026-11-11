# AWS OIDC setup for GitHub Actions deploys

This lets the workflow in `.github/workflows/deploy.yml` deploy without stored AWS keys. Do this once in the AWS console. Any region works, because IAM is global.

## 1. Create the OIDC identity provider
1. Open **IAM → Identity providers → Add provider**.
2. Provider type: **OpenID Connect**.
3. Provider URL: `https://token.actions.githubusercontent.com`
4. Audience: `sts.amazonaws.com`
5. Click **Add provider**. (If it already exists in the account, skip this step.)

## 2. Create the deploy role
1. Open **IAM → Roles → Create role**.
2. Trusted entity type: **Web identity**.
3. Identity provider: `token.actions.githubusercontent.com`. Audience: `sts.amazonaws.com`.
4. GitHub organization: `veselinmarkov`. Repository: `youtube-s3-tableau-pipeline`. Branch: `main`.
5. Click **Next**, skip the permissions for now, name the role `youtube-pipeline-deploy`, and click **Create role**.
6. Open the role and check **Trust relationships**. The condition should look like this:
   ```json
   "Condition": {
     "StringEquals": {
       "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
       "token.actions.githubusercontent.com:sub": "repo:veselinmarkov/youtube-s3-tableau-pipeline:ref:refs/heads/main"
     }
   }
   ```
   Only pushes to `main` of this repo can assume the role.

   **Check the real `sub` format.** If the repo or account uses ID-based OIDC claims, the token's subject looks like `repo:<owner>@<owner-id>/<repo>@<repo-id>:ref:refs/heads/main` (for this repo: `repo:veselinmarkov@48570558/youtube-s3-tableau-pipeline@1450243215:ref:refs/heads/main`), and the console wizard's name-based value will not match. If assuming the role fails with `Not authorized to perform sts:AssumeRoleWithWebIdentity`, edit the trust policy to use the ID-based value above. Pinning to IDs is also safer, since it survives renames and can't be taken over by a new repo with the old name.

## 3. Give the role permissions
`sam deploy` creates a CloudFormation stack containing a Lambda, an S3 bucket, an IAM role and an IAM user, plus a schedule.

**Simple option for a personal account:** attach **AdministratorAccess** to the role. It's the least effort and the most powerful, so use it only if this account is yours alone.

**Narrower option:** add an inline policy that allows these services:
`cloudformation:*`, `lambda:*`, `s3:*`, `events:*`, `iam:*`, `secretsmanager:GetSecretValue` (and `logs:*` for the function's log group).
This is still very broad, because `iam:*` can be used to gain admin rights. To tighten it, restrict `Resource` to the `youtube-pipeline-*` ARNs after the first successful deploy.

## 4. Tell GitHub which role to use
1. Copy the role ARN from the role page, for example `arn:aws:iam::<account-id>:role/youtube-pipeline-deploy`.
2. In the GitHub repo open **Settings → Secrets and variables → Actions → Variables → New repository variable**.
3. Name: `AWS_DEPLOY_ROLE_ARN`. Value: the role ARN.
4. Optional: add the variable `SCHEDULE_EXPRESSION`. The default is `rate(1 hour)`. Set it to `rate(1 day)` to switch to daily.

## 5. Run it
Re-run the failed workflow under the **Actions** tab, or push a new commit to `main`. The `deploy` job should assume the role and deploy the stack `youtube-pipeline` in eu-central-1.

## Troubleshooting
- **`Not authorized to perform sts:AssumeRoleWithWebIdentity`:** the `sub` condition doesn't match the repo or branch exactly, or the workflow is running from a different branch or a pull request.
- **`Could not assume role` with a missing variable:** `AWS_DEPLOY_ROLE_ARN` isn't set as a repository variable (a secret won't work with `vars.`).
- **`AccessDenied` during `sam deploy`:** the role is missing a permission from step 3. The error names the action.
- **Secret not found at runtime:** deploy works without the secret, but the Lambda fails until `youtube-pipeline/oauth` exists in eu-central-1 (see `docs/google-setup.md`, step 7).
