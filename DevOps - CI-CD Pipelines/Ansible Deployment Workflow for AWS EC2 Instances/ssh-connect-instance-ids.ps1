# Install AWSPowerShell module if not already installed
# Install-Module -Name AWSPowerShell -Force -Verbose

# Import AWSPowerShell module
Import-Module AWSPowerShell

# List EC2 instances
$instances = (Get-EC2Instance).instances

# Function to create SSH private key file from GitHub Secrets
function CreateSSHKeyFile {
    param (
        [string]$sshKeyFilePath
    )

    # Fetch SSH key from GitHub Secrets
    $sshPrivateKey = $env:GITHUB_ANSIBLE_SSH_KEY

    # Write SSH key to a temporary file
    Set-Content -Path $sshKeyFilePath -Value $sshPrivateKey
    Set-ItemProperty -Path $sshKeyFilePath -Name IsReadOnly -Value $true

    # Set correct permissions for the SSH key file
    chmod 600 $sshKeyFilePath
}

# Function to establish SSH connection to an instance
function ConnectToInstance {
    param (
        [string]$publicIpAddress,
        [string]$sshKeyFilePath,
        [string]$ansiblePlaybookPath
    )

    try {
        # Perform SSH connection using the SSH key file
        $sshCommand = "ssh -i `"$sshKeyFilePath`" -o StrictHostKeyChecking=no ubuntu@$publicIpAddress 'echo `"SSH connection established`"'"
        Invoke-Expression -Command $sshCommand

        # Run Ansible playbook using the SSH key file
        $ansibleCommand = "ansible-playbook --become --inventory my_inventory.aws_ec2.yml --private-key `"$sshKeyFilePath`" $ansiblePlaybookPath"
        Invoke-Expression -Command $ansibleCommand
    }
    finally {
        # Remove read-only attribute and clean up the SSH key file
        Set-ItemProperty -Path $sshKeyFilePath -Name IsReadOnly -Value $false
        Remove-Item $sshKeyFilePath -Force
    }
}

# Main script logic
foreach ($instance in $instances) {
    $instanceId = $instance.InstanceId
    $publicIpAddress = $instance.PublicIpAddress
    $sshKeyFilePath = "temp-ssh-key.pem"  # Temporary path for SSH key file

    Write-Output "Instance ID: $instanceId"
    Write-Output "Public IP Address: $publicIpAddress"

    # Check if instance has a public IP address
    if (![string]::IsNullOrEmpty($publicIpAddress)) {
        Write-Output "Connecting to instance: $publicIpAddress"

        # Call function to create SSH key file from GitHub Secrets
        CreateSSHKeyFile -sshKeyFilePath $sshKeyFilePath

        # Call function to establish SSH connection and run Ansible playbook
        ConnectToInstance -publicIpAddress $publicIpAddress -sshKeyFilePath $sshKeyFilePath -ansiblePlaybookPath "ansible-playbook.yml"
    } else {
        Write-Output "Instance $instanceId does not have a public IP address."
    }

    Write-Output "------------------------------------------------"
}
