"""
Vector store management for AgenticAds RAG system
Handles ChromaDB operations for knowledge storage and retrieval
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .config import RAGConfig

class VectorStoreManager:
    """Manages vector database operations for RAG system"""

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize()

    def _initialize(self):
        """Initialize the vector store and embedding model"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.config.vector_store_path,
                settings=Settings(anonymized_telemetry=False)
            )

            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.config.embedding_model)

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.config.collection_name,
                metadata={"description": "AgenticAds knowledge base for ad generation"}
            )

        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector store

        Args:
            documents: List of documents with 'content', 'metadata', and optional 'id'
        """
        try:
            # Extract content and metadata
            contents = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            ids = [doc.get("id", f"doc_{i}") for i, doc in enumerate(documents)]

            # Generate embeddings
            embeddings = self.embedding_model.encode(contents).tolist()

            # Add to collection
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )

            print(f"Added {len(documents)} documents to vector store")
            return True

        except Exception as e:
            print(f"Error adding documents: {e}")
            return False

    def query(self, query_texts: List[str], n_results: int = 5, where: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Query the vector store for relevant documents

        Args:
            query_texts: List of query strings
            n_results: Number of results to return
            where: Metadata filters
        """
        try:
            # Generate query embeddings
            query_embeddings = self.embedding_model.encode(query_texts).tolist()

            # Query the collection
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )

            return results

        except Exception as e:
            print(f"Error querying vector store: {e}")
            return {"documents": [[] for _ in query_texts], "metadatas": [[] for _ in query_texts]}

    def retrieve(self, platform: str, tone: str, content_type: str = "all") -> List[str]:
        """
        Retrieve relevant context for ad generation

        Args:
            platform: Target platform (instagram, facebook, etc.)
            tone: Desired tone (professional, casual, etc.)
            content_type: Type of content to retrieve
        """
        try:
            # Create contextual queries
            queries = [
                f"successful {platform} ads {tone} tone",
                f"high performing {platform} content",
                f"{tone} marketing copy examples for {platform}",
                f"viral {platform} campaigns"
            ]

            all_results = []
            for query in queries:
                results = self.query([query], n_results=3, where={"platform": platform})
                if results["documents"] and results["documents"][0]:
                    all_results.extend(results["documents"][0])

            # Remove duplicates and return top results
            unique_results = list(set(all_results))[:self.config.max_context_docs]
            return unique_results

        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    def seed_initial_knowledge(self):
        """Seed the vector store with initial knowledge base"""
        initial_documents = [
            {
                "content": "Instagram ads perform best with visually striking images, short compelling copy, and 5-10 relevant hashtags. Focus on lifestyle and aspirational content.",
                "metadata": {"platform": "instagram", "tone": "aspirational", "category": "best_practices"},
                "id": "instagram_best_practices_1"
            },
            {
                "content": "Facebook ads work well with detailed product descriptions, customer testimonials, and clear call-to-action buttons. Use longer copy that tells a story.",
                "metadata": {"platform": "facebook", "tone": "informative", "category": "best_practices"},
                "id": "facebook_best_practices_1"
            },
            {
                "content": "Twitter ads should be concise, use trending hashtags, and encourage engagement through questions or polls. Keep copy under 100 characters when possible.",
                "metadata": {"platform": "twitter", "tone": "concise", "category": "best_practices"},
                "id": "twitter_best_practices_1"
            },
            {
                "content": "LinkedIn ads perform best with professional tone, industry insights, and thought leadership content. Focus on business value and expertise.",
                "metadata": {"platform": "linkedin", "tone": "professional", "category": "best_practices"},
                "id": "linkedin_best_practices_1"
            },
            {
                "content": "Professional tone: Use formal language, focus on expertise, credibility, and business value. Avoid slang and casual expressions.",
                "metadata": {"tone": "professional", "category": "tone_guidelines"},
                "id": "professional_tone_guide"
            },
            {
                "content": "Casual tone: Use conversational language, contractions, and friendly expressions. Be approachable and relatable to the audience.",
                "metadata": {"tone": "casual", "category": "tone_guidelines"},
                "id": "casual_tone_guide"
            },
            {
                "content": "Urgent tone: Create sense of scarcity, use time-sensitive language, strong calls-to-action, and words like 'now', 'limited time', 'today only'.",
                "metadata": {"tone": "urgent", "category": "tone_guidelines"},
                "id": "urgent_tone_guide"
            },
            {
                "content": "Luxury tone: Emphasize exclusivity, quality, sophistication, and premium experience. Use elegant language and focus on craftsmanship.",
                "metadata": {"tone": "luxury", "category": "tone_guidelines"},
                "id": "luxury_tone_guide"
            }
        ]

        self.add_documents(initial_documents)
        print("Seeded initial knowledge base")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.config.collection_name,
                "embedding_model": self.config.embedding_model
            }
        except Exception as e:
            return {"error": str(e)}

    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(self.config.collection_name)
            self.collection = self.client.create_collection(
                name=self.config.collection_name,
                metadata={"description": "AgenticAds knowledge base for ad generation"}
            )
            print("Cleared vector store collection")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

# Global vector store instance
vector_store_manager = None

def get_vector_store(config: Optional[RAGConfig] = None) -> VectorStoreManager:
    """Get or create global vector store instance"""
    global vector_store_manager
    if vector_store_manager is None:
        vector_store_manager = VectorStoreManager(config)
    return vector_store_manager

# Async wrapper functions for the vector store operations
async def initialize_vector_store(config: Optional[RAGConfig] = None) -> VectorStoreManager:
    """Async initialization of vector store"""
    def _init():
        return VectorStoreManager(config)

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _init)

async def add_knowledge_documents(documents: List[Dict[str, Any]], config: Optional[RAGConfig] = None) -> bool:
    """Async wrapper for adding documents"""
    vector_store = get_vector_store(config)

    def _add():
        return vector_store.add_documents(documents)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _add)

async def retrieve_context(platform: str, tone: str, content_type: str = "all", config: Optional[RAGConfig] = None) -> List[str]:
    """Async wrapper for retrieving context"""
    vector_store = get_vector_store(config)

    def _retrieve():
        return vector_store.retrieve(platform, tone, content_type)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _retrieve)
