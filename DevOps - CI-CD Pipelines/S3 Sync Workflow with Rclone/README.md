# S3 Sync Workflow with Rclone

This GitHub Actions workflow automates the synchronization of files between an AWS S3 bucket and a Filebase S3 bucket using [Rclone](https://rclone.org/). It ensures that the contents of the source bucket are regularly and securely synced to the destination bucket.

---

## Purpose

1. **Automated Synchronization**:
   - Syncs data from the AWS S3 bucket (`awss3source`) to the Filebase S3 bucket (`filebases3destination`) hourly.

2. **Secure Configuration**:
   - Leverages GitHub Secrets for securely managing sensitive credentials.

3. **Customizable and Scalable**:
   - Allows users to easily adjust configuration and schedule based on their requirements.

---

## Workflow Trigger

This workflow is triggered by:
- **Manual Execution**: Via the `workflow_dispatch` option.
- **Scheduled Runs**: Executes hourly as defined by the cron schedule `0 * * * *`.

---

## Prerequisites

1. **GitHub Secrets**:
   Ensure the following secrets are added to your repository under **Settings > Secrets and variables > Actions**:
   - `AWS_ACCESS_KEY_ID`: Access key ID for the AWS S3 bucket.
   - `AWS_SECRET_ACCESS_KEY`: Secret access key for the AWS S3 bucket.
   - `FILEBASE_ACCESS_KEY_ID`: Access key ID for the Filebase S3 bucket.
   - `FILEBASE_SECRET_ACCESS_KEY`: Secret access key for the Filebase S3 bucket.

2. **S3 Buckets**:
   - Source Bucket: AWS S3 bucket (e.g., `dabsawss3bucket`).
   - Destination Bucket: Filebase S3 bucket (e.g., `dabsfilebases3bucket`).

---

## Key Workflow Steps

### 1. Install Rclone
- Installs the Rclone tool using the official installation script to enable S3 synchronization.

### 2. Configure Rclone
- Uses the [Jinja2 Action](https://github.com/cuchi/jinja2-action) to generate an Rclone configuration file (`rclone.prod.conf`) based on the provided template and GitHub Secrets.
- Variables in the `rclone.template.conf` file are dynamically replaced with secrets.

### 3. Sync S3 Buckets
- Executes the Rclone command to securely sync data:
  ```bash
  rclone --config=rclone.prod.conf sync awss3source:dabsawss3bucket filebases3destination:dabsfilebases3bucket
  ```
  - **Source**: `awss3source` bucket on AWS.
  - **Destination**: `filebases3destination` bucket on Filebase.

---

## File Descriptions

### 1. **s3sync.yml**
Defines the workflow steps to:
- Install Rclone.
- Generate the Rclone configuration file.
- Sync data between S3 buckets.

### 2. **rclone.template.conf**
Template for the Rclone configuration file with placeholders for secrets:
```plaintext
[awss3source]
type = s3
provider = AWS
env_auth = false
access_key_id = {{ RCLONE_CONFIG_AWS_ACCESS_KEY_ID }}
secret_access_key = {{ RCLONE_CONFIG_AWS_SECRET_ACCESS_KEY }}
region = us-east-1

[filebases3destination]
type = s3
provider = Other
env_auth = false
access_key_id = {{ RCLONE_CONFIG_FILEBASE_ACCESS_KEY_ID }}
secret_access_key = {{ RCLONE_CONFIG_FILEBASE_SECRET_ACCESS_KEY }}
region = us-east-1
endpoint = https://s3.filebase.com
```

---

## Usage

1. **Set Up the Workflow**:
   - Add the `s3sync.yml` file to your repository under `.github/workflows/`.

2. **Add Secrets**:
   - Add the required secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `FILEBASE_ACCESS_KEY_ID`, `FILEBASE_SECRET_ACCESS_KEY`) to your repository settings.

3. **Run the Workflow**:
   - Trigger the workflow manually from the **Actions** tab or wait for the scheduled run.

4. **Monitor Logs**:
   - View detailed logs in the Actions tab to verify the sync operation.

---

## Security Considerations

1. **Credentials Management**:
   - Store sensitive credentials (e.g., S3 keys) securely as GitHub Secrets.

2. **Access Control**:
   - Ensure appropriate IAM policies for the AWS S3 bucket and Filebase bucket.

3. **Data Integrity**:
   - Regularly verify that the synchronization process is accurate and complete.

---

By leveraging this workflow, you can automate and secure data synchronization between AWS and Filebase S3 buckets efficiently.
