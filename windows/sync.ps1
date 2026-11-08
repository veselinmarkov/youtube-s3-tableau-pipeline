# Sync the YouTube CSVs from S3 to a local folder for Tableau.
# Prereq: AWS CLI installed; `aws configure --profile youtube-reader` with the ReaderUser keys.
# Schedule: Task Scheduler -> powershell.exe -File C:\path\sync.ps1 (hourly/daily).
param(
    [Parameter(Mandatory = $true)][string]$Bucket,
    [string]$Dest = "C:\youtube_data"
)
aws s3 sync "s3://$Bucket/youtube" $Dest --profile youtube-reader --region eu-central-1
