"""
Enhanced vector store with knowledge base integration
Advanced retrieval and ingestion capabilities
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .config import RAGConfig
from .vector_store import VectorStoreManager, get_vector_store    
from .knowledge_base import KnowledgeBaseManager, get_knowledge_manager
from .chunking import AdaptiveChunker, Chunk, create_chunks_for_documents

class EnhancedVectorStore:
    """Enhanced vector store with knowledge base integration"""

    def __init__(self, config: Optional[RAGConfig] = None):
        # Use the same vector store instance as the knowledge manager
        self.vector_store = get_vector_store(config)
        self.config = config or RAGConfig()
        self.knowledge_manager = get_knowledge_manager(config)
        self.chunker = AdaptiveChunker()
        self.embedding_model = self.vector_store.embedding_model

    def add_knowledge_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add knowledge documents with chunking"""
        try:
            # Chunk documents for better retrieval
            chunked_docs = create_chunks_for_documents(documents)

            # Add chunks to vector store
            return self.vector_store.add_documents(chunked_docs)

        except Exception as e:
            print(f"Error adding knowledge documents: {e}")
            return False

    def retrieve_with_context(self, query: str, platform: str = None,
                            tone: str = None, content_type: str = "all",
                            n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve context with platform and tone filtering"""

        try:
            # Build query embeddings
            query_embedding = self.embedding_model.encode([query]).tolist()

            # Build where clause for filtering
            where_clause = {}
            if platform:
                where_clause["platform"] = platform
            if tone:
                where_clause["tone"] = tone
            if content_type != "all":
                where_clause["content_type"] = content_type

            # Query vector store
            results = self.vector_store.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results * 2,  # Get more results for reranking
                where=where_clause if where_clause else None
            )

            if not results["documents"] or not results["documents"][0]:
                return []

            # Rerank results based on relevance and diversity
            reranked_results = self._rerank_results(query, results, n_results)

            if not reranked_results:
                return []

        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    def _rerank_results(self, query: str, results: Dict[str, Any],
                       n_results: int) -> List[Dict[str, Any]]:
        """Rerank search results for better relevance"""

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        # Calculate query-document similarity scores
        query_embedding = self.embedding_model.encode([query])
        doc_embeddings = self.embedding_model.encode(documents)

        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]

        # Combine distance and similarity scores
        combined_scores = []
        for i, (doc, metadata, distance, similarity) in enumerate(zip(documents, metadatas, distances, similarities)):
            # Normalize scores (lower distance is better, higher similarity is better)
            normalized_distance = 1 / (1 + distance)
            combined_score = (normalized_distance + similarity) / 2

            # Boost score for exact platform/tone matches
            if metadata.get("platform") == metadata.get("platform"):  # This is a placeholder
                combined_score *= 1.2

            combined_scores.append((combined_score, i))

        # Sort by combined score and return top results
        combined_scores.sort(reverse=True)
        top_indices = [idx for _, idx in combined_scores[:n_results]]

        reranked_results = []
        for idx in top_indices:
            reranked_results.append({
                "content": documents[idx],
                "metadata": metadatas[idx],
                "similarity_score": similarities[idx],
                "distance": distances[idx]
            })

        return reranked_results

    def get_relevant_templates(self, platform: str, tone: str,
                              n_results: int = 3) -> List[Dict[str, Any]]:
        """Get relevant ad templates for specific platform and tone"""

        query = f"successful {platform} ads {tone} tone template"
        return self.retrieve_with_context(
            query=query,
            platform=platform,
            tone=tone,
            content_type="template",
            n_results=n_results
        )

    def get_brand_guidelines(self, brand_name: str = "AgenticAds") -> List[Dict[str, Any]]:
        """Get brand guidelines for content generation"""

        query = f"{brand_name} brand guidelines content style"
        return self.retrieve_with_context(
            query=query,
            content_type="guideline",
            n_results=5
        )

    def get_successful_examples(self, platform: str, tone: str,
                               n_results: int = 3) -> List[Dict[str, Any]]:
        """Get successful examples for inspiration"""

        query = f"successful {platform} {tone} ad examples"
        return self.retrieve_with_context(
            query=query,
            platform=platform,
            tone=tone,
            content_type="example",
            n_results=n_results
        )

    def ingest_historical_data(self, mongodb_url: str = "mongodb://localhost:27017",
                              db_name: str = "agentic_ads") -> int:
        """Ingest historical data from MongoDB"""

        async def _ingest():
            return await self.knowledge_manager.ingest_from_mongodb(mongodb_url, db_name)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                task = asyncio.create_task(_ingest())
                return task.result()
            else:
                return asyncio.run(_ingest())
        except Exception as e:
            print(f"Error ingesting historical data: {e}")
            return 0

    def seed_comprehensive_knowledge(self) -> bool:
        """Seed comprehensive knowledge base"""
        try:
            print("🌱 Starting to seed knowledge base...")
            success = self.knowledge_manager.seed_initial_knowledge_base()

            if success:
                print("✅ Comprehensive knowledge base seeded successfully")
                stats = self.knowledge_manager.get_knowledge_stats()
                print(f"📊 Knowledge base stats: {stats}")
                
                # Verify documents are in vector store
                try:
                    count = self.vector_store.collection.count()
                    print(f"📚 Vector store contains {count} documents")
                except Exception as e:
                    print(f"⚠️  Could not verify vector store count: {e}")
            else:
                print("❌ Failed to seed knowledge base")

            return success
        except Exception as e:
            print(f"❌ Error seeding knowledge base: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return self.vector_store.get_stats()

    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data for monitoring"""

        stats = self.knowledge_manager.get_knowledge_stats()
        vector_stats = self.get_stats()

        return {
            "knowledge_base": stats,
            "vector_store": vector_stats,
            "total_chunks": sum(stats["by_content_type"].values()),
            "platforms_covered": len(stats["by_platform"]),
            "tones_covered": len(stats["by_tone"])
        }

# Global enhanced vector store instance
enhanced_vector_store = None

def get_enhanced_vector_store(config: Optional[RAGConfig] = None) -> EnhancedVectorStore:
    """Get or create global enhanced vector store instance"""
    global enhanced_vector_store
    if enhanced_vector_store is None:
        enhanced_vector_store = EnhancedVectorStore(config)
    return enhanced_vector_store
