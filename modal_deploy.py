import modal

app = modal.App("chatbot_prototype")

# Load images from Docker Hub using from_registry.
auth_service_image = modal.Image.from_registry("amidu/chatbot_prototype_auth_service:latest")
data_service_image = modal.Image.from_registry("amidu/chatbot_prototype_data_service:latest")
general_chat_service_image = modal.Image.from_registry("amidu/chatbot_prototype_general_chat_service:latest")
study_support_service_image = modal.Image.from_registry("amidu/chatbot_prototype_study_support_service:latest")
response_service_image = modal.Image.from_registry("amidu/chatbot_prototype_response_service:latest")
system_prompt_service_image = modal.Image.from_registry("amidu/chatbot_prototype_system_prompt_service:latest")
training_service_image = modal.Image.from_registry("amidu/chatbot_prototype_training_service:latest")
api_gateway_image = modal.Image.from_registry("amidu/chatbot_prototype_api_gateway:latest")
ui_image = modal.Image.from_registry("amidu/chatbot_prototype_ui:latest")

# Each function is deployed with a web_endpoint() (with no arguments)
# and the desired port is provided via an environment variable.
@app.function(image=auth_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5001"})
def run_auth_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@app.function(image=data_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5004"})
def run_data_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@app.function(image=general_chat_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5002"})
def run_general_chat_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@app.function(image=study_support_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5003"})
def run_study_support_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@app.function(image=response_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5005"})
def run_response_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@app.function(image=system_prompt_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5006"})
def run_system_prompt_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@app.function(image=training_service_image, web_endpoint=modal.web_endpoint(), env={"PORT": "5007"})
def run_training_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

# For API gateway, we override service endpoints via environment variables.
@app.function(image=api_gateway_image, web_endpoint=modal.web_endpoint(), env={
    "PORT": "5000",
    "AUTH_SERVICE_URL": "http://run_auth_service",
    "GENERAL_CHAT_SERVICE_URL": "http://run_general_chat_service",
    "STUDY_SUPPORT_SERVICE_URL": "http://run_study_support_service"
})
def run_api_gateway():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

# For UI, we override the API gateway URL.
@app.function(image=ui_image, web_endpoint=modal.web_endpoint(), env={
    "PORT": "7860",
    "API_GATEWAY_URL": "http://run_api_gateway/query"
})
def run_ui():
    import subprocess
    subprocess.run(["python", "gradio_app.py"], check=True)

if __name__ == "__main__":
    app.deploy("chatbot_prototype")
