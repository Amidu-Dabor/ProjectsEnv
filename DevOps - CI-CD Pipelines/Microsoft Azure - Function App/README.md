# Flask on Azure Functions

A small Flask app hosted on **Azure Functions**: an HTTP-triggered function passes every request to Flask through Azure's WSGI middleware.

## How it works

- `main/function.json`: an anonymous HTTP trigger for GET and POST on any route (`{*route}`).
- `main/function_app.py`: wraps the Flask app with `func.WsgiMiddleware`. The `/` route redirects to an external site (an exercise in routing and redirects).
- `host.json`: the Functions host settings, with no route prefix and request limits.
- `requirements.txt`: `azure-functions` and `flask`.

## Run locally

```bash
pip install -r requirements.txt
func start      # needs Azure Functions Core Tools
```

Deploy with the workflow in [Azure Functions Deploy](../Azure%20Functions%20Deploy).

## Other files

- `setup.py`: packaging settings from a separate Azure Storage SDK exercise.
- `Testing_the_Model_Exercise_.ipynb`: an unrelated logistic-regression exercise on bank data.

> Deployment credentials (publish profiles) and SSH keys must never be committed. Store them as GitHub secrets.

## Tech

Python · Flask · Azure Functions
