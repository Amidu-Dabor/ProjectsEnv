param (
    [string]$StackName = 'awsvpcstack',
    [string]$TemplateFilePath = 'cloudformation-vpc.yml'
)

function New-OrUpdate-CFNStack {
    param (
        [string]$StackName,
        [string]$TemplateBody
    )

    $stackExists = (Get-CFNStack -StackName $StackName -ErrorAction SilentlyContinue) -ne $null

    if ($stackExists) {
        Write-Host "Stack [$StackName] already exists. Updating the stack..."
        try {
            Update-CFNStack -StackName $StackName -TemplateBody $TemplateBody -ErrorAction Stop
            Write-Host "Stack [$StackName] updated successfully."
        } catch {
            if ($_.Exception.Message -like "*No updates are to be performed*") {
                Write-Host "No updates are to be performed on stack [$StackName]."
            } else {
                Write-Host "Failed to update stack [$StackName]: $_"
                exit 1
            }
        }
    } else {
        Write-Host "Creating new stack [$StackName]..."
        try {
            New-CFNStack -StackName $StackName -TemplateBody $TemplateBody -ErrorAction Stop
            Write-Host "Stack [$StackName] created successfully."
        } catch {
            Write-Host "Failed to create stack [$StackName]: $_"
            exit 1
        }
    }
}

# Read the template file content as a single string
$TemplateBody = Get-Content -Path $TemplateFilePath -Raw

# Validate the template
Write-Host "Validating CloudFormation template..."
try {
    Test-CFNTemplate -TemplateBody $TemplateBody -ErrorAction Stop
    Write-Host "Template validation succeeded."
} catch {
    Write-Host "Template validation failed: $_"
    exit 1
}

# Debug: Print the template body to verify its content
Write-Host "TemplateBody content:"
Write-Host $TemplateBody

# Execute the function with provided parameters
New-OrUpdate-CFNStack -StackName $StackName -TemplateBody $TemplateBody

# Verify stack creation
try {
    $stackStatus = Get-CFNStack -StackName $StackName -ErrorAction Stop
    if ($stackStatus -ne $null) {
        Write-Host "Stack [$StackName] exists and has the following status: $($stackStatus.StackStatus)"
    } else {
        Write-Host "Stack [$StackName] does not exist."
    }
} catch {
    Write-Host "Failed to retrieve stack status for [$StackName]: $_"
}
