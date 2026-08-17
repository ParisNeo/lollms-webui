import requests
import yaml
from typing import List, Dict
from pathlib import Path

class RequestyModelFetcher:
    API_URL = "https://router.requesty.ai/v1/models"

    def fetch_models(self) -> List[Dict]:
        """Fetches the model data from the Requesty API"""
        try:
            response = requests.get(self.API_URL)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            return data.get('data', [])
        except requests.RequestException as e:
            print(f"Error fetching models: {e}")
            return []

    def format_models(self, models_data: List[Dict]) -> List[Dict]:
        """Formats the raw API data into the desired structure.

        Mirrors the OpenRouter scraper output structure. Requesty's /v1/models is
        OpenAI-shaped (a 'data' array) but its model objects expose 'context_window'
        and capability flags rather than OpenRouter's 'architecture'/'pricing'
        objects, so every field is read defensively with .get() and sensible
        fallbacks.
        """
        formatted_models = []
        for model in models_data:
            model_id = model.get('id', '')
            if not model_id:
                continue
            # Requesty uses 'context_window'; fall back to OpenAI-style 'context_length'.
            context_length = model.get('context_window', model.get('context_length', 0)) or 0
            architecture = model.get('architecture') or {}
            pricing = model.get('pricing') or {}
            formatted_model = {
                "category": "generic",
                "datasets": "unknown",
                "icon": "",
                "last_commit_time": "",
                "license": "commercial",
                "model_creator": model_id.split('/')[0] if '/' in model_id else "",
                "model_creator_link": f"/models/{model_id}",
                "name": model_id,
                "provider": None,
                "rank": 0.0,
                "type": "api",
                "context_length": context_length,
                "architecture": {
                    "modality": architecture.get('modality', ''),
                    "tokenizer": architecture.get('tokenizer', ''),
                    "instruct_type": architecture.get('instruct_type', '')
                },
                "per_request_limits": model.get('per_request_limits'),
                "variants": [{
                    "name": model.get('name', model_id),
                    "size": f"Context length: {context_length}",
                    "input_cost": float(pricing.get('prompt', 0.0) or 0.0),
                    "output_cost": float(pricing.get('completion', 0.0) or 0.0)
                }]
            }
            formatted_models.append(formatted_model)
        return formatted_models

    def save_models_yaml(self, output_path: str = None):
        """Fetches models, formats them, and saves to a YAML file"""
        if not output_path:
            output_path = str(Path(__file__).parent/"models.yaml")
        models_data = self.fetch_models()
        formatted_models = self.format_models(models_data)

        with open(output_path, 'w') as file:
            yaml.dump(formatted_models, file, default_flow_style=False)

        print(f"Models data saved to {output_path}")

# Usage
if __name__ == "__main__":
    fetcher = RequestyModelFetcher()
    fetcher.save_models_yaml()
