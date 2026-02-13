# GitHub Actions deployment

## IAM user setup (AWS CLI)

1) Create the user.

```bash
aws iam create-user --user-name github-actions-deployer
```

2) Create a minimal policy document.

```bash
cat > deploy-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Sync",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME"
    },
    {
      "Sid": "S3ObjectWrite",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    },
    {
      "Sid": "CloudFrontInvalidate",
      "Effect": "Allow",
      "Action": "cloudfront:CreateInvalidation",
      "Resource": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
    }
  ]
}
EOF
```

3) Attach as an inline policy.

```bash
aws iam put-user-policy \
  --user-name github-actions-deployer \
  --policy-name github-actions-inline-deploy \
  --policy-document file://deploy-policy.json
```

4) Create access keys (save the output for GitHub secrets).

```bash
aws iam create-access-key --user-name github-actions-deployer
```

Notes:
- Remove `s3:PutObjectAcl` if you do not use ACLs.
- Remove `s3:DeleteObject` if you never delete objects in sync.

## GitHub secrets

Run this to create access keys for the user (save the output for secrets):

```bash
aws iam create-access-key --user-name github-actions-deployer
```

Add these repository secrets (Settings -> Secrets and variables -> Actions):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `CLOUDFRONT_DISTRIBUTION_ID`
