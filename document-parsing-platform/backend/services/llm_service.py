from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod
import requests
import time
from functools import wraps
import os
import json
from enum import Enum

class LLMProvider(Enum):
    GOOGLE_AI = "google-ai"
    AWAN = "awan"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    TOGETHER_AI = "togetherai"
    LITELLM = "litellm"
    LMSTUDIO = "lmstudio"

class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validate_config()
        
    @abstractmethod
    def validate_config(self) -> None:
        """Validate the configuration for this provider"""
        pass
        
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        pass
        
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embeddings for text"""
        pass

class GoogleAIService(BaseLLMService):
    def validate_config(self) -> None:
        required = ['api_key', 'model_name']
        if not all(k in self.config for k in required):
            raise ValueError(f"Missing required config keys: {required}")
            
    def generate(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            params = {
                "prompt": prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "maxOutputTokens": kwargs.get('max_tokens', 2048)
            }
            
            def retry_request(url, headers, params, max_retries=3):
                for attempt in range(max_retries):
                    try:
                        response = requests.post(
                            url,
                            headers=headers,
                            json=params,
                            timeout=10
                        )
                        response.raise_for_status()
                        return response
                    except requests.exceptions.RequestException as e:
                        if attempt == max_retries - 1:
                            raise
                        wait_time = 2 ** (attempt + 1)
                        self.logger.warning(f"Attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)

            response = retry_request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['model_name']}:generateText",
                headers=headers,
                json=params
            )
            response.raise_for_status()
            return response.json()['candidates'][0]['output']
            
        except Exception as e:
            self.logger.error(f"Google AI generation failed: {str(e)}")
            raise

    def embed(self, text: str) -> list[float]:
        try:
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = retry_request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['model_name']}:embedText",
                headers=headers,
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()['embedding']['value']
            
        except Exception as e:
            self.logger.error(f"Google AI embedding failed: {str(e)}")
            raise

class OllamaService(BaseLLMService):
    def validate_config(self) -> None:
        required = ['model_name']
        if not all(k in self.config for k in required):
            raise ValueError(f"Missing required config keys: {required}")
            
    def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.config['model_name'],
                    "prompt": prompt,
                    "options": {
                        "temperature": kwargs.get('temperature', 0.7),
                        "num_ctx": kwargs.get('max_tokens', 2048)
                    }
                }
            )
            response.raise_for_status()
            
            # Ollama streams the response, so we need to collect it
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    full_response += chunk.get("response", "")
                    
            return full_response
            
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {str(e)}")
            raise

    def embed(self, text: str) -> list[float]:
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": self.config['model_name'],
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()['embedding']
            
        except Exception as e:
            self.logger.error(f"Ollama embedding failed: {str(e)}")
            raise

class LLMServiceFactory:
    """Factory class for creating LLM service instances"""
    
    @staticmethod
    def create_service(provider: str, config: Dict[str, Any]) -> BaseLLMService:
        provider_enum = LLMProvider(provider.lower())
        
        if provider_enum == LLMProvider.GOOGLE_AI:
            return GoogleAIService(config)
        elif provider_enum == LLMProvider.OLLAMA:
            return OllamaService(config)
        # Add other providers here...
        else:
            raise ValueError(f"Unsupported provider: {provider}")

class LLMServiceManager:
    """Manages multiple LLM service instances"""
    
    def __init__(self):
        self.services: Dict[str, BaseLLMService] = {}
        self.default_provider: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
    def add_provider(self, provider: str, config: Dict[str, Any]) -> None:
        """Add a new LLM provider"""
        try:
            service = LLMServiceFactory.create_service(provider, config)
            self.services[provider] = service
            if not self.default_provider:
                self.default_provider = provider
            self.logger.info(f"Added LLM provider: {provider}")
        except Exception as e:
            self.logger.error(f"Failed to add provider {provider}: {str(e)}")
            raise
            
    def set_default_provider(self, provider: str) -> None:
        """Set the default provider"""
        if provider not in self.services:
            raise ValueError(f"Provider not configured: {provider}")
        self.default_provider = provider
        self.logger.info(f"Set default LLM provider to: {provider}")
        
    def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate text using the specified or default provider"""
        provider = provider or self.default_provider
        if not provider:
            raise ValueError("No LLM provider configured")
            
        try:
            return self.services[provider].generate(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Generation failed with provider {provider}: {str(e)}")
            raise
            
    def embed(self, text: str, provider: Optional[str] = None) -> list[float]:
        """Generate embeddings using the specified or default provider"""
        provider = provider or self.default_provider
        if not provider:
            raise ValueError("No LLM provider configured")
            
        try:
            return self.services[provider].embed(text)
        except Exception as e:
            self.logger.error(f"Embedding failed with provider {provider}: {str(e)}")
            raise

# Example usage
if __name__ == '__main__':
    # Initialize with Google AI
    manager = LLMServiceManager()
    manager.add_provider("google-ai", {
        "api_key": os.getenv("GOOGLE_AI_KEY"),
        "model_name": "text-bison-001"
    })
    
    # Generate text
    try:
        response = manager.generate("Explain quantum computing in simple terms")
        print(response)
    except Exception as e:
        print(f"Error: {str(e)}")