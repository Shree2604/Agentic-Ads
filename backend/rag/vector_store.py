"""
Vector store management for AgenticAds RAG system
Handles ChromaDB operations for knowledge storage and retrieval
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .config import RAGConfig

class VectorStoreManager:
    """Manages vector database operations for RAG system"""
    _instance = None
    _initialized = False

    def __new__(cls, config: Optional[RAGConfig] = None):
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._instance.config = config or RAGConfig()
            cls._instance.client = None
            cls._instance.collection = None
            cls._instance.embedding_model = None
            cls._instance._collection_id = None
            cls._instance._is_temp_db = False
        return cls._instance

    def __init__(self, config: Optional[RAGConfig] = None):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def __del__(self):
        """Cleanup resources when the instance is destroyed"""
        self.cleanup()

    def cleanup(self):
        """Clean up resources and connections"""
        try:
            if self.client:
                # Reset the client's connection
                self.client.reset()
                self.client = None
            if self.collection:
                self.collection = None
            if self._is_temp_db and os.path.exists(self.config.vector_store_path):
                import shutil
                try:
                    shutil.rmtree(self.config.vector_store_path)
                except:
                    pass
        except Exception as e:
            print(f"Warning during cleanup: {str(e)}")

    def _initialize(self):
        """Initialize the vector store and embedding model"""
        import tempfile
        import time
        from pathlib import Path

        def try_initialize_client(db_path):
            Path(db_path).mkdir(parents=True, exist_ok=True)
            return chromadb.PersistentClient(
                path=db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )

        try:
            print("🔧 Initializing vector store...")
            
            # Try to use the default path first
            try:
                # Clean up any existing client
                if self.client:
                    self.cleanup()

                # Try to initialize with the default path
                self.client = try_initialize_client(self.config.vector_store_path)
                self._is_temp_db = False
            except Exception as e:
                if "process cannot access the file" in str(e):
                    print("⚠️ Main database is locked, using temporary database...")
                    # Create a temporary directory for ChromaDB
                    temp_dir = tempfile.mkdtemp(prefix="chromadb_temp_")
                    self.config.vector_store_path = temp_dir
                    self.client = try_initialize_client(temp_dir)
                    self._is_temp_db = True
                else:
                    raise
            
            # Initialize the collection
            try:
                self.collection = self.client.get_or_create_collection(
                    name=self.config.collection_name,
                    metadata={"description": "AgenticAds knowledge base"}
                )
            except Exception as e:
                print(f"⚠️ Error creating collection: {str(e)}")
                # Try to get existing collection
                self.collection = self.client.get_collection(self.config.collection_name)

            # Initialize embedding model
            print("🔧 Loading embedding model...")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)

            # Create or get collection
            print(f"🔧 Setting up collection: {self.config.collection_name}")
            try:
                # Try to get existing collection
                self.collection = self.client.get_collection(name=self.config.collection_name)
                print("Found existing collection")
            except:
                # Create new collection if it doesn't exist
                self.collection = self.client.create_collection(
                    name=self.config.collection_name,
                    metadata={
                        "description": "AgenticAds knowledge base for ad generation",
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                print("Created new collection")
            
            # Store the collection ID
            self._collection_id = self.collection.id
            print(f"✅ Vector store initialized with collection ID: {self._collection_id}")
            if self._is_temp_db:
                print("⚠️ Using temporary database - data will not persist!")

        except Exception as e:
            print(f"❌ Error initializing vector store: {str(e)}")
            # Try cleanup on error
            self.cleanup()
            raise

    def _flatten_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested metadata and convert to ChromaDB compatible format"""
        flattened = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            elif isinstance(value, dict):
                # Convert nested dict to string
                flattened[key] = json.dumps(value)
            elif isinstance(value, (list, tuple)):
                # Convert lists to string
                flattened[key] = json.dumps(value)
            elif value is None:
                flattened[key] = ""
            else:
                # Convert other types to string
                flattened[key] = str(value)
        return flattened

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector store

        Args:
            documents: List of documents with 'content', 'metadata', and optional 'id'
        """
        if not documents:
            return True

        try:
            # Process documents in smaller batches
            batch_size = 50
            success = True

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Extract content and metadata for batch
                contents = [str(doc["content"]) for doc in batch]
                metadatas = [self._flatten_metadata(doc.get("metadata", {})) for doc in batch]
                ids = [str(doc.get("id", f"doc_{j}")) for j, doc in enumerate(batch, start=i)]

                # Generate embeddings
                embeddings = self.embedding_model.encode(contents).tolist()

                # Add documents with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.collection.add(
                            documents=contents,
                            embeddings=embeddings,
                            metadatas=metadatas,
                            ids=ids
                        )
                        print(f"✅ Added batch {i//batch_size + 1} ({len(batch)} documents)")
                        break
                    except Exception as e:
                        if "Collection does not exist" in str(e):
                            print("Collection lost, reinitializing...")
                            self._initialize()
                            continue
                        if attempt == max_retries - 1:
                            print(f"❌ Failed to add batch after {max_retries} attempts")
                            success = False
                            break
                        print(f"Retrying batch {i//batch_size + 1}... ({attempt + 1}/{max_retries})")

            return success

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
