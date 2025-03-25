import modal

stub = modal.Stub("chatbot_prototype")

# Images for each microservice (ensure these images are available on Docker Hub)
api_gateway_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_api_gateway:latest")
auth_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_auth_service:latest")
data_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_data_service:latest")
general_chat_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_general_chat_service:latest")
study_support_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_study_support_service:latest")
response_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_response_service:latest")
system_prompt_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_system_prompt_service:latest")
training_service_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_training_service:latest")
ui_image = modal.Image.from_dockerhub("amidu/chatbot_prototype_ui:latest")

@stub.function(image=api_gateway_image, web=True, port=5000)
def run_api_gateway():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=auth_service_image, web=True, port=5001)
def run_auth_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=data_service_image, web=True, port=5004)
def run_data_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=general_chat_service_image, web=True, port=5002)
def run_general_chat_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=study_support_service_image, web=True, port=5003)
def run_study_support_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=response_service_image, web=True, port=5005)
def run_response_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=system_prompt_service_image, web=True, port=5006)
def run_system_prompt_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=training_service_image, web=True, port=5007)
def run_training_service():
    import subprocess
    subprocess.run(["python", "app.py"], check=True)

@stub.function(image=ui_image, web=True, port=7860)
def run_ui():
    import subprocess
    subprocess.run(["python", "gradio_app.py"], check=True)

if __name__ == "__main__":
    stub.deploy("chatbot_prototype")
