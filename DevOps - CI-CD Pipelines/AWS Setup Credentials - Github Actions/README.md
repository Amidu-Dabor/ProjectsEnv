# AWS Credentials in GitHub Actions: Access Keys vs OIDC

Three GitHub Actions workflows that sign in to AWS and list the account's VPCs with PowerShell, showing two ways of authenticating.

| Workflow | Authentication |
|---|---|
| `aws-creds.yml` | **Long-lived access keys** stored as repository secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) |
| `aws-creds-oidc.yml` | **OIDC:** GitHub gets a short-lived token and assumes an IAM role, so no keys are stored |
| `aws-creds-oidc-practice.yml` | The OIDC version with `configure-aws-credentials@v4` and a separate practice role |

OIDC is the recommended approach: there are no stored secrets to leak, and credentials expire automatically.

## Use

1. In AWS IAM, add GitHub (`token.actions.githubusercontent.com`) as an OIDC identity provider.
2. Create a role that trusts your repository, and put its ARN in `role-to-assume`.
3. Copy the workflow into `.github/workflows/` and run it from the **Actions** tab, or on push.

## Tech

GitHub Actions · AWS IAM (OIDC) · `aws-actions/configure-aws-credentials` · AWS Tools for PowerShell
