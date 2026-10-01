import os
import time
import requests
from typing import Dict, Optional, List

class AISynthesizer:
    """
    AI Synthesizer for generating launch copy and pitches using OpenRouter free models.
    """
    
    DEFAULT_FALLBACKS = [
        'google/gemma-4-31b-it:free',
        'nvidia/nemotron-3.5-lightning:free',
        'google/gemma-4-26b-a4b-it:free',
        'nvidia/nemotron-3-super-120b-a12b:free',
        'qwen/qwen3.8-27b:free',
        'inclusionai/ling-3.0-flash-sante:free'
    ]

    def __init__(self, api_key: Optional[str] = None, model: str = 'google/gemma-4-31b-it:free'):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        self.model = model

    def _call_openrouter(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048) -> Dict:
        if not self.api_key:
            return {"error": "No OPENROUTER_API_KEY provided."}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/github-seo-agent", 
            "X-Title": "GitHub SEO Agent",
            "Content-Type": "application/json"
        }
        
        models_to_try = [self.model] + [m for m in self.DEFAULT_FALLBACKS if m != self.model]
        
        for model in models_to_try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            retries = 3
            for attempt in range(retries):
                try:
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                    if response.status_code == 200:
                        return {"result": response.json()['choices'][0]['message']['content']}
                    elif response.status_code in [429, 502, 503]:
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        break # Other errors, try next model
                except requests.exceptions.RequestException:
                    time.sleep(2 ** attempt)
                    continue
                    
        return {"error": "All models failed or timed out."}

    def synthesize_launch_copy(self, repo_url: str, project_name: str, features: List[str], channel: str, angle: str = '') -> Dict:
        """Generates launch copy for a specific channel."""
        prompt = f"Write a launch post for {project_name} on {channel}. URL: {repo_url}. Features: {', '.join(features)}. Angle: {angle}"
        messages = [{"role": "user", "content": prompt}]
        return self._call_openrouter(messages)

    def synthesize_readme_pitch(self, project_name: str, tagline: str, focus_area: str) -> Dict:
        """Generates hero pitch copy for the README."""
        prompt = f"Write a catchy hero pitch for a GitHub README. Project: {project_name}. Tagline: {tagline}. Focus area: {focus_area}."
        messages = [{"role": "user", "content": prompt}]
        return self._call_openrouter(messages)
