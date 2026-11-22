# AWS Access from GitHub Actions with OIDC

A GitHub Actions workflow (`aws-oidc.yml`) that signs in to AWS **without stored access keys**. GitHub issues a short-lived OpenID Connect (OIDC) token, which the workflow exchanges for temporary credentials by assuming an IAM role. It then lists the account's VPCs with AWS Tools for PowerShell to prove access works.

## How it works

- `permissions: id-token: write` lets the job request an OIDC token.
- `aws-actions/configure-aws-credentials@v4` assumes the IAM role named in `role-to-assume`, in `us-west-2`.
- A PowerShell step installs `AWS.Tools.EC2` and runs `Get-EC2Vpc`.

It runs on every push, or manually from the **Actions** tab.

## Use

1. In AWS IAM, add `token.actions.githubusercontent.com` as an OIDC identity provider.
2. Create a role whose trust policy allows your repository, then put its ARN in `role-to-assume`.
3. Copy `aws-oidc.yml` into `.github/workflows/`.

See also [AWS Setup Credentials - Github Actions](../AWS%20Setup%20Credentials%20-%20Github%20Actions), which compares this with access keys.

## Tech

GitHub Actions · AWS IAM (OIDC) · AWS Tools for PowerShell
