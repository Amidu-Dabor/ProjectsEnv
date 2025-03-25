import os
import modal
from modal import App, Image, Secret

# Create our Modal app (this replaces the old Stub)
app = App("chatbot_prototype")

# For model-based services, you might use a slim Debian image with necessary packages installed.
# Here we mimic the pricer sample by installing dependencies like huggingface, torch, transformers, bitsandbytes, accelerate, and peft.
# Adjust the pip_install list as needed for your chatbot-prototype.
base_image = Image.debian_slim().pip_install(
    "flask", "requests", "python-dotenv", "openai", "anthropic",
    "transformers", "torch", "bitsandbytes", "accelerate", "peft", "langchain", "modal"
)

# (Optional) Attach secrets if needed, for example, Hugging Face API keys.
secrets = [Secret.from_name("huggingface-secret")]

# Load container images for each service from Docker Hub.
# Replace the image names with your repository names.
AuthImage = Image.from_registry("amidu/chatbot_prototype_auth_service:latest")
DataImage = Image.from_registry("amidu/chatbot_prototype_data_service:latest")
GeneralChatImage = Image.from_registry("amidu/chatbot_prototype_general_chat_service:latest")
StudySupportImage = Image.from_registry("amidu/chatbot_prototype_study_support_service:latest")
ResponseImage = Image.from_registry("amidu/chatbot_prototype_response_service:latest")
SystemPromptImage = Image.from_registry("amidu/chatbot_prototype_system_prompt_service:latest")
TrainingImage = Image.from_registry("amidu/chatbot_prototype_training_service:latest")
ApiGatewayImage = Image.from_registry("amidu/chatbot_prototype_api_gateway:latest")
UiImage = Image.from_registry("amidu/chatbot_prototype_ui:latest")

# Deploy each microservice as a class.
# We remove any 'env' parameters from the decorators; instead, each service's code should load
# its configuration from environment variables (e.g. using python-dotenv or os.environ.get).
# If you need to pass extra configuration to Modal, consider setting it via the container image or secrets.
@app.cls(image=AuthImage)
class AuthService:
    @modal.web_endpoint(method="POST")
    def handle_request(self, request):
        # This function will run the auth service (it runs the container's app.py)
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=DataImage)
class DataService:
    @modal.web_endpoint()
    def fetch_data(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=GeneralChatImage)
class GeneralChatService:
    @modal.web_endpoint()
    def general_query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=StudySupportImage)
class StudySupportService:
    @modal.web_endpoint()
    def study_query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=ResponseImage)
class ResponseService:
    @modal.web_endpoint()
    def generate_response(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=SystemPromptImage)
class SystemPromptService:
    @modal.web_endpoint()
    def get_prompt(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=TrainingImage)
class TrainingService:
    @modal.web_endpoint()
    def train(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=ApiGatewayImage)
class ApiGateway:
    @modal.web_endpoint()
    def query(self, request):
        import subprocess
        subprocess.run(["python", "app.py"], check=True)


@app.cls(image=UiImage)
class UI:
    @modal.web_endpoint()
    def serve(self, request):
        import subprocess
        subprocess.run(["python", "gradio_app.py"], check=True)

# Publish the app. In the latest Modal SDK, use publish() instead of deploy().
if __name__ == "__main__":
    app.publish()
