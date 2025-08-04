# Terraform Deployment Workflow

This GitHub Actions workflow automates the deployment of Terraform configurations, providing a seamless process to initialize, plan, and apply Terraform changes while maintaining the state file in the repository.

---

## Purpose

1. **Clone Source Code**:
   - Ensures the latest code is checked out from the GitHub repository.

2. **Configure AWS Credentials**:
   - Assumes the specified IAM role for secure interaction with AWS resources.

3. **Run Terraform Commands**:
   - Initializes the Terraform configuration.
   - Plans infrastructure changes.
   - Applies changes to deploy or update the infrastructure.

4. **Commit Terraform State File**:
   - Automatically commits the updated state file back to the repository for version control.

---

## Workflow Triggers

This workflow is triggered by:
- **Push Events**: Runs automatically on changes pushed to the repository.
- **Manual Dispatch**: Can be triggered manually via the `workflow_dispatch` event.

---

## Permissions

The workflow requires the following permissions:
- **id-token: write**: For requesting the JWT.
- **contents: write**: For committing the updated state file to the repository.

---

## Required Secrets

Add the following secrets to your repository's **Settings > Secrets and variables > Actions**:

- **AWS_ROLE_TO_ASSUME**: The ARN of the IAM role to assume.
- **AWS_REGION**: The AWS region for deploying resources.

---

## Key Steps

### 1. Clone Source Code
- Uses the `actions/checkout@v4` action to clone the repository's code.

### 2. Configure AWS Credentials
- Configures AWS credentials using the `aws-actions/configure-aws-credentials@v4` action.
- Assumes the specified IAM role and sets the region for the deployment.

### 3. Run Terraform Commands
- **Terraform Init**:
  - Initializes the Terraform configuration.
- **Terraform Plan**:
  - Generates and displays the execution plan for the changes.
- **Terraform Apply**:
  - Applies the changes and deploys the infrastructure.

### 4. Commit Terraform State File
- Uses the `stefanzweifel/git-auto-commit-action@v5` action to commit the updated `terraform.tfstate` file back to the repository.
- Ensures the state file is versioned and synchronized.

---

## Usage

### 1. Update the Workflow File
- Place the `.yml` file under `.github/workflows/` in your repository.
- Adjust the AWS region, IAM role ARN, and any Terraform configurations as needed.

### 2. Add Secrets
- Navigate to **Settings > Secrets and variables > Actions** in your GitHub repository.
- Add the required secrets (`AWS_ROLE_TO_ASSUME`, `AWS_REGION`).

### 3. Trigger the Workflow
- Push changes to the repository to trigger the workflow automatically, or
- Manually trigger the workflow in the **Actions** tab by selecting “Run workflow”.

### 4. Monitor Workflow Logs
- View the logs of each step in the Actions tab to ensure successful deployment.

---

## Security Considerations

1. **AWS IAM Role**:
   - Use least privilege permissions for the IAM role being assumed.

2. **GitHub Secrets**:
   - Keep all sensitive information secure by storing them as secrets.

3. **State File Management**:
   - Ensure the Terraform state file is committed only to private repositories to avoid exposing infrastructure details.

---

By implementing this workflow, you can automate and standardize the deployment process for your Terraform-managed infrastructure, ensuring efficiency and accuracy in managing cloud resources.
