# services/system_prompts_service.py

from system_prompts.prompts_manager import get_system_prompt

class SystemPromptsService:
    def __init__(self):
        self.general_prompt = (
            get_system_prompt(model_type="general")
        )
        self.study_prompt = (
            get_system_prompt(model_type="study")
        )
    
    def get_prompt(self):
            return [self.general_prompt, self.study_prompt]
