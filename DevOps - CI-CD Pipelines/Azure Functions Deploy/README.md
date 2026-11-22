# Deploy a Python App to Azure Functions (GitHub Actions)

A GitHub Actions workflow (`deploy.yml`) that builds a Python project and deploys it to an **Azure Function App**.

## Steps

1. Checks out the code and sets up Python 3.11.
2. Installs `requirements.txt` into `.python_packages/lib/site-packages`, the folder Azure Functions expects.
3. Deploys with `Azure/functions-action@v1`, authenticating with a publish profile stored as the repository secret `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`, with a remote (Oryx) build enabled.

It runs manually from the **Actions** tab (`workflow_dispatch`), in the `dev` environment.

## Use

1. In the Azure portal, download your Function App's publish profile and save it as the secret `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`. Never commit it.
2. Set `AZURE_FUNCTIONAPP_NAME` (and `AZURE_FUNCTIONAPP_PACKAGE_PATH` if needed) in `deploy.yml`.
3. Copy the file into `.github/workflows/` and run it.

## Tech

GitHub Actions · Azure Functions · Python
