from typing import Dict, Any, Optional, List
import logging
from abc import ABC, abstractmethod
import requests
import os
import numpy as np
from enum import Enum

class EmbeddingProvider(Enum):
    GOOGLE_AI = "google-ai"
    AWAN = "awan"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    TOGETHER_AI = "togetherai"
    LITELLM = "litellm"
    LMSTUDIO = "lmstudio"

class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validate_config()
        self.dimension = self.get_embedding_dimension()
        
    @abstractmethod
    def validate_config(self) -> None:
        """Validate the configuration for this provider"""
        pass
        
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        pass
        
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        pass
        
    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (default implementation)"""
        return [self.embed(text) for text in texts]
        
    def normalize(self, embedding: List[float]) -> List[float]:
        """Normalize embedding to unit vector"""
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return (embedding / norm).tolist()

class GoogleAIEmbeddingService(BaseEmbeddingService):
    def validate_config(self) -> None:
        required = ['api_key', 'model_name']
        if not all(k in self.config for k in required):
            raise ValueError(f"Missing required config keys: {required}")
            
    def get_embedding_dimension(self) -> int:
        # Google AI embeddings are typically 768-dimensional
        return 768
            
    def embed(self, text: str) -> List[float]:
        try:
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['model_name']}:embedText",
                headers=headers,
                json={"text": text}
            )
            response.raise_for_status()
            embedding = response.json()['embedding']['value']
            return self.normalize(embedding)
            
        except Exception as e:
            self.logger.error(f"Google AI embedding failed: {str(e)}")
            raise

    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        try:
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['model_name']}:batchEmbedText",
                headers=headers,
                json={"texts": texts}
            )
            response.raise_for_status()
            embeddings = [e['value'] for e in response.json()['embeddings']]
            return [self.normalize(embedding) for embedding in embeddings]
            
        except Exception as e:
            self.logger.error(f"Google AI batch embedding failed: {str(e)}")
            raise

class OllamaEmbeddingService(BaseEmbeddingService):
    def validate_config(self) -> None:
        required = ['model_name']
        if not all(k in self.config for k in required):
            raise ValueError(f"Missing required config keys: {required}")
            
    def get_embedding_dimension(self) -> int:
        # Ollama embeddings are typically 4096-dimensional
        return 4096
            
    def embed(self, text: str) -> List[float]:
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": self.config['model_name'],
                    "prompt": text
                }
            )
            response.raise_for_status()
            embedding = response.json()['embedding']
            return self.normalize(embedding)
            
        except Exception as e:
            self.logger.error(f"Ollama embedding failed: {str(e)}")
            raise

class EmbeddingServiceFactory:
    """Factory class for creating embedding service instances"""
    
    @staticmethod
    def create_service(provider: str, config: Dict[str, Any]) -> BaseEmbeddingService:
        provider_enum = EmbeddingProvider(provider.lower())
        
        if provider_enum == EmbeddingProvider.GOOGLE_AI:
            return GoogleAIEmbeddingService(config)
        elif provider_enum == EmbeddingProvider.OLLAMA:
            return OllamaEmbeddingService(config)
        # Add other providers here...
        else:
            raise ValueError(f"Unsupported provider: {provider}")

class EmbeddingServiceManager:
    """Manages multiple embedding service instances"""
    
    def __init__(self):
        self.services: Dict[str, BaseEmbeddingService] = {}
        self.default_provider: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
    def add_provider(self, provider: str, config: Dict[str, Any]) -> None:
        """Add a new embedding provider"""
        try:
            service = EmbeddingServiceFactory.create_service(provider, config)
            self.services[provider] = service
            if not self.default_provider:
                self.default_provider = provider
            self.logger.info(f"Added embedding provider: {provider}")
        except Exception as e:
            self.logger.error(f"Failed to add provider {provider}: {str(e)}")
            raise
            
    def set_default_provider(self, provider: str) -> None:
        """Set the default provider"""
        if provider not in self.services:
            raise ValueError(f"Provider not configured: {provider}")
        self.default_provider = provider
        self.logger.info(f"Set default embedding provider to: {provider}")
        
    def embed(self, text: str, provider: Optional[str] = None) -> List[float]:
        """Generate embeddings using the specified or default provider"""
        provider = provider or self.default_provider
        if not provider:
            raise ValueError("No embedding provider configured")
            
        try:
            return self.services[provider].embed(text)
        except Exception as e:
            self.logger.error(f"Embedding failed with provider {provider}: {str(e)}")
            raise
            
    def batch_embed(self, texts: List[str], provider: Optional[str] = None) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        provider = provider or self.default_provider
        if not provider:
            raise ValueError("No embedding provider configured")
            
        try:
            return self.services[provider].batch_embed(texts)
        except Exception as e:
            self.logger.error(f"Batch embedding failed with provider {provider}: {str(e)}")
            raise

# Example usage
if __name__ == '__main__':
    # Initialize with Google AI
    manager = EmbeddingServiceManager()
    manager.add_provider("google-ai", {
        "api_key": os.getenv("GOOGLE_AI_KEY"),
        "model_name": "embedding-001"
    })
    
    # Generate embeddings
    try:
        embedding = manager.embed("This is a sample text to embed")
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"Error: {str(e)}")