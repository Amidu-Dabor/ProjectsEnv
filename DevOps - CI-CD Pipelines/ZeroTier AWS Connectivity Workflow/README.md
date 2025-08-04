# ZeroTier AWS Connectivity Workflow

This GitHub Actions workflow configures a ZeroTier client on the runner, joins a specified ZeroTier network, and verifies connectivity to AWS VPC resources. It performs key network checks such as pinging private EC2 instances, testing DNS resolution, and connecting to an Amazon RDS instance.

---

## Purpose

1. **Install and Authorize ZeroTier Client**:
   - Ensures the GitHub Actions runner securely joins the ZeroTier network.

2. **Validate Network Connectivity**:
   - Ping ZeroTier-connected EC2 instances and private AWS VPC resources.

3. **Test DNS Resolution**:
   - Verify name resolution using Route 53 resolvers.

4. **Connect to Amazon RDS**:
   - Confirm MySQL database connectivity over the private network.

---

## Workflow Trigger

This workflow is triggered by:
- **Push Events**: Automatically runs upon repository updates.
- **Manual Runs**: Triggered via the `workflow_dispatch` option in the Actions tab.

---

## Required Secrets

To run this workflow, add the following secrets in your repository’s **Settings > Secrets and variables > Actions**:

- **ZEROTIER_NETWORKID**: The ID of the ZeroTier network to join.
- **ZEROTIER_API_KEY**: API key with permissions to authorize new members in the ZeroTier network.
- **MYSQL_PASSWORD**: Password for your Amazon RDS MySQL instance.

---

## Key Steps

### 1. Install ZeroTier Client
- Uses the official ZeroTier installer script to set up the client on the GitHub Actions runner.

### 2. Authorize ZeroTier Client
- Retrieves the runner’s ZeroTier ID using `zerotier-cli info`.
- Verifies membership in the specified network and authorizes the runner via the ZeroTier API.

### 3. Gather Network Information
- Logs the runner’s public IP address for debugging purposes using `ipinfo.io`.

### 4. Network Connectivity Tests
- Pings:
  - A ZeroTier-connected EC2 instance (acting as the VPC Router).
  - A private IP within the AWS VPC to ensure connectivity via ZeroTier.

### 5. DNS Resolution Checks
- Performs `nslookup` queries against specified Route 53 resolver endpoints.

### 6. Amazon RDS Connection
- Connects to the RDS MySQL instance using the MySQL CLI to run basic commands (e.g., creating a database, listing databases).

---

## Usage

### 1. Update the Workflow File
- Place the `.yml` file in your repository under `.github/workflows/`.
- Modify IP addresses, hostnames, and commands to match your environment.

### 2. Add Secrets
- Navigate to **Settings > Secrets and variables > Actions** in your GitHub repository.
- Add the secrets `ZEROTIER_NETWORKID`, `ZEROTIER_API_KEY`, and `MYSQL_PASSWORD`.

### 3. Run the Workflow
- Trigger the workflow by:
  - Pushing changes to the repository, or
  - Manually running it from the Actions tab.

### 4. View Logs
- Check the workflow logs for detailed output of each step, including installation, network join, ping results, DNS resolution, and MySQL queries.

---

## Security Considerations

1. **ZeroTier Credentials**:
   - Keep your API key private and secure by using GitHub Actions secrets.

2. **AWS Credentials**:
   - While this workflow doesn’t directly require AWS credentials, ensure private endpoints are appropriately secured.

3. **Network Access**:
   - Verify that your IP addresses and ports allow inbound/outbound traffic as per your security group or firewall rules.

---

By leveraging this workflow, you can streamline and validate connectivity between your GitHub Actions runner, ZeroTier network, and AWS resources, ensuring secure and efficient operations.
