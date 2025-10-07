"""
Configuration for AgenticAds RAG system
Settings for models, vector store, and agent parameters
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RAGConfig:
    """Configuration for the RAG system"""

    # Model configurations
    text_model: str = "gpt2"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    image_model: str = "CompVis/stable-diffusion-v1-4"

    # Vector store configuration
    vector_store_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
    collection_name: str = "agentic_ads_knowledge"

    # Agent parameters
    max_context_docs: int = 10
    generation_temperature: float = 0.7
    max_retries: int = 2

    # Quality thresholds
    min_quality_score: float = 7.0
    min_retrieval_similarity: float = 0.7

    # Platform-specific settings
    platform_configs: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.platform_configs is None:
            self.platform_configs = {
                "instagram": {
                    "max_chars": 2200,
                    "hashtags_per_post": 10,
                    "visual_focus": "high"
                },
                "facebook": {
                    "max_chars": 63206,
                    "hashtags_per_post": 5,
                    "visual_focus": "medium"
                },
                "twitter": {
                    "max_chars": 280,
                    "hashtags_per_post": 3,
                    "visual_focus": "low"
                },
                "linkedin": {
                    "max_chars": 3000,
                    "hashtags_per_post": 3,
                    "visual_focus": "medium"
                }
            }

    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """Create config from environment variables"""
        return cls(
            text_model=os.getenv("RAG_TEXT_MODEL", "gpt2"),
            embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            image_model=os.getenv("RAG_IMAGE_MODEL", "CompVis/stable-diffusion-v1-4"),
            vector_store_path=os.getenv("VECTOR_STORE_PATH", "./chroma_db"),
            collection_name=os.getenv("COLLECTION_NAME", "agentic_ads_knowledge"),
            max_context_docs=int(os.getenv("MAX_CONTEXT_DOCS", "10")),
            generation_temperature=float(os.getenv("GENERATION_TEMPERATURE", "0.7")),
            max_retries=int(os.getenv("MAX_RETRIES", "2")),
            min_quality_score=float(os.getenv("MIN_QUALITY_SCORE", "7.0")),
            min_retrieval_similarity=float(os.getenv("RETRIEVAL_SIMILARITY", "0.7"))
        )

# Global configuration instance
config = RAGConfig.from_env()
