from enum import Enum
from typing import Dict

class GrokModel(Enum):
    """Available Grok model variants for comparison"""
    GROK_4_LATEST = "grok-4-latest"
    GROK_VISION_BETA = "grok-vision-beta"
    
    @property
    def display_name(self) -> str:
        names = {
            "grok-4-latest": "Grok 4 Latest",
            "grok-vision-beta": "Grok Vision Beta"
        }
        return names.get(self.value, self.value)
    
    @property
    def max_tokens(self) -> int:
        """Maximum context window for each model"""
        return 131072  # 128K tokens for Grok models
    
    @property
    def temperature_range(self) -> tuple:
        """Recommended temperature range"""
        return (0.0, 2.0)

def get_model_config(model: GrokModel) -> Dict:
    """Get configuration for a specific Grok model"""
    return {
        "model": model.value,
        "max_tokens": model.max_tokens,
        "temperature": 0.7,  # Default for reasoning tasks
        "top_p": 0.9,
        "stream": False
    }

