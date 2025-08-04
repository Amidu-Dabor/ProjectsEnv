import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from configs.config import GPT4O_MODEL, LLAMA_MODEL

class QuantizedModelLoader:
    """
    This class loads a quantized model (either GPT-4.0 or Llama) at initialization.
    The model is loaded in memory once and can be accessed via the `model` and `tokenizer` attributes.
    
    Parameters:
        model_type (str): A string indicating which model to load.
                          Expected values: "gpt4o" or "llama".
        quant_4_bit (bool): If True, loads the model in 4-bit mode; otherwise, in 8-bit mode.
    """
    def __init__(self, model_type: str, quant_4_bit: bool = False):
        self.quant_4_bit = quant_4_bit

        # Select the model name from configuration.
        if model_type.lower() == "gpt4o":
            self.model_name = GPT4O_MODEL
        elif model_type.lower() == "llama":
            self.model_name = LLAMA_MODEL
        else:
            raise ValueError("Invalid model_type. Expected 'gpt4o' or 'llama'.")

        self._initialize_model()

    def _initialize_model(self):
        # Set up quantization configuration.
        if self.quant_4_bit:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quant_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.bfloat16
            )

        # Load the tokenizer.
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        # Load the base model in quantized mode.
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=quant_config,
            device_map="auto"
        )
        # Update the tokenizer with the quantized model's pad token.
        self.model.generation_config.pad_token_id = self.tokenizer.pad_token_id

        print(f"Quantized model '{self.model_name}' loaded. Memory footprint: {self.model.get_memory_footprint() / 1e6:.1f} MB")

# Expose the class for import.
__all__ = ["QuantizedModelLoader"]

if __name__ == "__main__":
    # Initialization of the models.
    print("Initializing GPT-4.0 quantized model loader:")
    gpt_loader = QuantizedModelLoader("gpt4o", quant_4_bit=False)
    print("Initializing Llama quantized model loader:")
    llama_loader = QuantizedModelLoader("llama", quant_4_bit=False)
