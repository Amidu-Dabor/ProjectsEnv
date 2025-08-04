# Ansible Deployment Workflow for AWS EC2 Instances

This repository contains a GitHub Actions workflow and supporting scripts for automating the deployment and configuration of AWS EC2 instances using Ansible. The workflow integrates AWS and Ansible to streamline infrastructure setup, package installations, and configuration management.

---

## Features

- **Automated EC2 Instance Management**:
  - Provision EC2 instances dynamically using Ansible and AWS inventory.
  - Install and configure required packages (e.g., Python, Nginx).

- **GitHub Actions Workflow**:
  - Automates Ansible playbook execution using a CI/CD pipeline.
  - Supports caching of Ansible dependencies for faster execution.

- **AWS Integration**:
  - Leverages OpenID Connect (OIDC) for secure authentication to AWS.
  - Automatically discovers EC2 instances in specific AWS regions.

- **Secure SSH Access**:
  - Uses a private SSH key stored in GitHub Secrets for secure access to EC2 instances.

---

## Workflow Trigger

The workflow is triggered by:

1. **Push Events**: Automatically runs when changes are pushed to the repository.
2. **Manual Runs**: Triggered via the `workflow_dispatch` option from the GitHub Actions tab.

---

## Workflow Overview

### Workflow File: `ansible.yml`

1. **Environment Configuration**:
   - Disables host key checking for SSH.
   - Sets the default Ansible remote user to `ubuntu`.

2. **Steps**:
   - **Clone Source Code**: Checks out the repository.
   - **Cache Dependencies**: Speeds up workflow execution by caching Ansible dependencies.
   - **Install Dependencies**:
     - Installs Ansible and required Python libraries (e.g., AWS SDKs).
     - Downloads the `amazon.aws` Ansible Galaxy collection.
   - **Authenticate to AWS**: Configures AWS credentials using OIDC.
   - **Debugging**:
     - Lists files in the runner environment for verification.
     - Displays the contents of the dynamic inventory file.
   - **Run PowerShell Script**:
     - Connects to EC2 instances via SSH and executes Ansible playbooks.

### Ansible Playbook File: `ansible-playbook.yml`

- **Tasks**:
  - Installs `python3-pip` for Python package management.
  - Installs and configures Nginx for web serving.

### Dynamic Inventory File: `my_inventory.aws_ec2.yml`

- Uses the `amazon.aws.aws_ec2` plugin to dynamically discover EC2 instances in the specified AWS regions.
- Groups instances by their key name for targeted configuration.

### PowerShell Script: `ssh-connect-instance-ids.ps1`

- Connects to EC2 instances via SSH.
- Executes Ansible playbooks for automated configuration.
- Ensures secure handling of SSH private keys.

---

## Prerequisites

1. **AWS Setup**:
   - Ensure EC2 instances are up and running.
   - Configure proper IAM roles and permissions for accessing AWS resources.

2. **GitHub Secrets**:
   Add the following secrets in your repository:
   - **`ANSIBLE_SSH_KEY`**: SSH private key for EC2 access.
   - **`AWS_REGION`**: AWS region for EC2 discovery.
   - **`AWS_OIDC_ROLE`**: IAM role ARN for OIDC authentication.

---

## Usage

### 1. Setup the Repository
- Clone this repository to your local machine.
- Place the workflow file (`ansible.yml`) in `.github/workflows/`.
- Update the inventory file (`my_inventory.aws_ec2.yml`) to match your AWS configuration.

### 2. Configure GitHub Secrets
- Go to **Settings > Secrets and variables > Actions**.
- Add the required secrets listed above.

### 3. Trigger the Workflow
- **Push Changes**: Push updates to the repository to automatically trigger the workflow.
- **Manual Execution**: Navigate to the Actions tab, select the workflow, and click **Run workflow**.

### 4. Verify Logs
- Monitor the GitHub Actions logs to confirm successful execution.
- Check for any errors or warnings during Ansible playbook execution.

---

## Security Considerations

1. **Secrets Management**:
   - Store sensitive data (e.g., SSH keys, AWS credentials) in GitHub Secrets.

2. **IAM Role Configuration**:
   - Use least privilege principles when creating IAM roles for this workflow.

3. **Network Security**:
   - Ensure EC2 instances have proper security group configurations to allow SSH and other required traffic.

---

## Troubleshooting

1. **Cache Issues**:
   - If dependencies are not cached, ensure the `requirements.yml` file is correctly specified.

2. **SSH Key Errors**:
   - Verify that the SSH private key in GitHub Secrets matches the public key on the EC2 instances.

3. **AWS Authentication**:
   - Check the OIDC role ARN and associated permissions.
     
---

By automating EC2 configuration and deployment, this workflow ensures efficient, secure, and scalable infrastructure management. Happy deploying!
