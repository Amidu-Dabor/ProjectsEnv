import os
import modal

app = modal.App("chatbot_prototype")

# For simplicity, we assume all required secrets (if any) are set via Modal or environment.
# Load images from Docker Hub using from_registry.
AuthImage = modal.Image.from_registry("amidu/chatbot_prototype_auth_service:latest")
DataImage = modal.Image.from_registry("amidu/chatbot_prototype_data_service:latest")
GeneralChatImage = modal.Image.from_registry("amidu/chatbot_prototype_general_chat_service:latest")
StudySupportImage = modal.Image.from_registry("amidu/chatbot_prototype_study_support_service:latest")
ResponseImage = modal.Image.from_registry("amidu/chatbot_prototype_response_service:latest")
SystemPromptImage = modal.Image.from_registry("amidu/chatbot_prototype_system_prompt_service:latest")
TrainingImage = modal.Image.from_registry("amidu/chatbot_prototype_training_service:latest")
ApiGatewayImage = modal.Image.from_registry("amidu/chatbot_prototype_api_gateway:latest")
UiImage = modal.Image.from_registry("amidu/chatbot_prototype_ui:latest")

@app.cls(image=AuthImage, env={"PORT": "5001"})
class AuthService:
    @modal.web_endpoint(method="POST")
    def handle_request(self, request):
        # Call the actual auth logic inside the container.
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=DataImage, env={"PORT": "5004"})
class DataService:
    @modal.web_endpoint()
    def fetch_data(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=GeneralChatImage, env={"PORT": "5002"})
class GeneralChatService:
    @modal.web_endpoint()
    def general_query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=StudySupportImage, env={"PORT": "5003"})
class StudySupportService:
    @modal.web_endpoint()
    def study_query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=ResponseImage, env={
    "PORT": "5005",
    "BASE_MODEL": os.environ.get("BASE_MODEL", "huggyllama/llama-7b"),
    "FINETUNED_MODEL_PATH": os.environ.get("FINETUNED_MODEL_PATH", ""),
    "BASE_MODEL_STUDY": os.environ.get("BASE_MODEL_STUDY", "tiiuae/falcon-7b"),
    "FINETUNED_MODEL_PATH_STUDY": os.environ.get("FINETUNED_MODEL_PATH_STUDY", "")
})
class ResponseService:
    @modal.web_endpoint()
    def generate_response(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=SystemPromptImage, env={"PORT": "5006"})
class SystemPromptService:
    @modal.web_endpoint()
    def get_prompt(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=TrainingImage, env={"PORT": "5007"})
class TrainingService:
    @modal.web_endpoint()
    def train(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=ApiGatewayImage, env={
    "PORT": "5000",
    # Use Modal's internal DNS: functions can be referenced by their class and method names.
    "AUTH_SERVICE_URL": "http://AuthService.handle_request",
    "GENERAL_CHAT_SERVICE_URL": "http://GeneralChatService.general_query",
    "STUDY_SUPPORT_SERVICE_URL": "http://StudySupportService.study_query"
})
class ApiGateway:
    @modal.web_endpoint()
    def query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)

@app.cls(image=UiImage, env={
    "PORT": "7860",
    "API_GATEWAY_URL": "http://ApiGateway.query"
})
class UI:
    @modal.web_endpoint()
    def serve(self, request):
        import subprocess
        subprocess.run(["python", "gradio_app.py"], check=True)

if __name__ == "__main__":
    app.deploy("chatbot_prototype")
