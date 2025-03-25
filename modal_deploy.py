import modal
import os

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

@app.cls(image=auth_service_image)
class AuthService:
    @modal.web_endpoint(method="POST")
    def handle_request(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=data_service_image)
class DataService:
    @modal.web_endpoint()
    def fetch_data(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=general_chat_service_image)
class GeneralChatService:
    @modal.web_endpoint()
    def general_query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=study_support_service_image)
class StudySupportService:
    @modal.web_endpoint()
    def study_query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=response_service_image)
class ResponseService:
    @modal.web_endpoint()
    def generate_response(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=system_prompt_service_image)
class SystemPromptService:
    @modal.web_endpoint()
    def get_prompt(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=training_service_image)
class TrainingService:
    @modal.web_endpoint()
    def train(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=api_gateway_image)
class ApiGateway:
    @modal.web_endpoint()
    def query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=ui_image)
class UI:
    @modal.web_endpoint()
    def serve(self, request):
        import subprocess
        subprocess.run(["python", "gradio_app.py"], check=True)
