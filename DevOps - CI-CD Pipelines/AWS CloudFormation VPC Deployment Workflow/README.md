# AWS CloudFormation VPC Deployment Workflow

This GitHub Actions workflow automates the deployment and management of AWS CloudFormation stacks to provision and update resources such as VPCs and subnets. It is designed to streamline infrastructure as code (IaC) practices, ensuring reliable and consistent AWS resource deployment.

---

## Purpose

1. **Automated CloudFormation Deployment**:
   - Provisions AWS resources using CloudFormation templates.
   - Updates existing stacks seamlessly.

2. **Infrastructure as Code**:
   - Ensures consistent and repeatable deployments.
   - Simplifies resource management and scaling.

3. **On-Demand Execution**:
   - Can be triggered manually or on push events.

---

## Workflow Trigger

This workflow is triggered by:
- **Manual Execution**: Via the `workflow_dispatch` option.
- **Push Events**: Automatically runs when changes are pushed to the repository.

---

## Required Secrets

To run this workflow, add the following secrets in your repository under **Settings > Secrets and variables > Actions**:

- **AWS_ACCESS_KEY_ID**: Access key ID for AWS authentication.
- **AWS_SECRET_ACCESS_KEY**: Secret access key for AWS authentication.

---

## Key Workflow Steps

### 1. Clone Repository
- Uses the `actions/checkout` action to clone the repository containing the CloudFormation templates and deployment scripts.

### 2. Configure AWS Credentials
- Authenticates with AWS using the `aws-actions/configure-aws-credentials` action.

### 3. Install AWS CloudFormation Tools
- Installs the necessary PowerShell modules for interacting with AWS CloudFormation.

### 4. Deploy CloudFormation Stack
- Executes the `deploy.ps1` script to:
  - Validate the CloudFormation template.
  - Create or update the specified CloudFormation stack.
  - Provision resources defined in the template (e.g., VPCs and subnets).

---

## File Descriptions

### 1. **aws-cloudformation.yml**
Defines the workflow steps to:
- Authenticate with AWS.
- Install required AWS tools.
- Execute the CloudFormation deployment script.

### 2. **cloudformation-vpc.yml**
CloudFormation template that defines the resources to be provisioned:
- **VPC**: A Virtual Private Cloud with DNS support and hostnames enabled.
- **Subnet**: A public subnet within the VPC.

### 3. **deploy.ps1**
PowerShell script that:
- Validates the CloudFormation template.
- Creates or updates the CloudFormation stack based on the provided template.
- Verifies the status of the deployed stack.

---

## Usage

1. **Set Up the Workflow**:
   - Add the `aws-cloudformation.yml` file to your repository under `.github/workflows/`.

2. **Add Secrets**:
   - Add the required secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) to your repository settings.

3. **Run the Workflow**:
   - Trigger the workflow manually from the **Actions** tab or push changes to the repository.

4. **Monitor Logs**:
   - View detailed logs in the Actions tab to verify the deployment process.

---

## Security Considerations

1. **IAM Role Permissions**:
   - Ensure the IAM role used by the workflow has permissions to manage CloudFormation stacks and the resources defined in the templates.

2. **Secrets Management**:
   - Store sensitive credentials (e.g., AWS keys) securely as GitHub Secrets.

3. **Template Validation**:
   - Regularly validate CloudFormation templates to ensure they meet your infrastructure requirements and compliance standards.

---

By using this workflow, you can simplify and automate the deployment of AWS infrastructure, ensuring efficiency and scalability for your cloud resources.
