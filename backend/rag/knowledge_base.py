"""
Knowledge Base Manager for AgenticAds RAG system
Handles document structure, ingestion pipeline, and knowledge organization
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import os

from .config import RAGConfig
from .vector_store import VectorStoreManager, get_vector_store

@dataclass
class KnowledgeDocument:
    """Standardized knowledge document structure"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    created_at: datetime
    updated_at: datetime
    content_type: str  # 'template', 'guideline', 'feedback', 'example', 'best_practice'
    platform: Optional[str] = None
    tone: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class KnowledgeBaseManager:
    """Manages the knowledge base for RAG system"""

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.vector_store = get_vector_store(config)
        self.knowledge_path = Path("./knowledge_base")
        self._ensure_knowledge_directory()

    def _ensure_knowledge_directory(self):
        """Create knowledge base directory if it doesn't exist"""
        self.knowledge_path.mkdir(exist_ok=True)
        (self.knowledge_path / "templates").mkdir(exist_ok=True)
        (self.knowledge_path / "guidelines").mkdir(exist_ok=True)
        (self.knowledge_path / "feedback").mkdir(exist_ok=True)
        (self.knowledge_path / "examples").mkdir(exist_ok=True)

    def create_ad_template(self, content: str, platform: str, tone: str,
                          category: str = "general", tags: List[str] = None) -> KnowledgeDocument:
        """Create an ad template document"""
        doc_id = f"template_{platform}_{tone}_{len(content)}chars_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        metadata = {
            "platform": platform,
            "tone": tone,
            "category": category,
            "char_length": len(content),
            "word_count": len(content.split()),
            "template_type": "text"
        }

        now = datetime.utcnow()
        return KnowledgeDocument(
            id=doc_id,
            content=content,
            metadata=metadata,
            source="manual_template",
            content_type="template",
            platform=platform,
            tone=tone,
            category=category,
            tags=tags or [],
            created_at=now,
            updated_at=now
        )

    def create_brand_guideline(self, content: str, brand_name: str,
                              guideline_type: str = "general", tags: List[str] = None) -> KnowledgeDocument:
        """Create a brand guideline document"""
        doc_id = f"guideline_{brand_name}_{guideline_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        metadata = {
            "brand_name": brand_name,
            "guideline_type": guideline_type,
            "char_length": len(content),
            "word_count": len(content.split())
        }

        now = datetime.utcnow()
        return KnowledgeDocument(
            id=doc_id,
            content=content,
            metadata=metadata,
            source="brand_guidelines",
            content_type="guideline",
            category=guideline_type,
            tags=tags or [brand_name, guideline_type],
            created_at=now,
            updated_at=now
        )

    def create_successful_example(self, content: str, platform: str, tone: str,
                                 performance_metrics: Dict[str, Any] = None,
                                 tags: List[str] = None) -> KnowledgeDocument:
        """Create a successful ad example document"""
        doc_id = f"example_{platform}_{tone}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Flatten performance metrics into top-level metadata
        metrics = performance_metrics or {}
        metadata = {
            "platform": platform,
            "tone": tone,
            "char_length": len(content),
            "word_count": len(content.split()),
            "engagement_rate": metrics.get("engagement_rate", 0),
            "click_through_rate": metrics.get("click_through_rate", 0),
            "conversions": metrics.get("conversions", 0),
            "performance_score": sum(metrics.values()) if metrics else 0
        }

        now = datetime.utcnow()
        return KnowledgeDocument(
            id=doc_id,
            content=content,
            metadata=metadata,
            source="successful_examples",
            content_type="example",
            platform=platform,
            tone=tone,
            category="successful",
            tags=tags or [platform, tone, "successful"],
            created_at=now,
            updated_at=now
        )

    def create_user_feedback(self, content: str, platform: str, rating: int,
                           user_id: str = "anonymous", tags: List[str] = None) -> KnowledgeDocument:
        """Create a user feedback document"""
        doc_id = f"feedback_{user_id}_{platform}_{rating}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        metadata = {
            "platform": platform,
            "rating": rating,
            "user_id": user_id,
            "char_length": len(content),
            "word_count": len(content.split()),
            "feedback_type": "rating" if rating > 0 else "complaint"
        }

        now = datetime.utcnow()
        return KnowledgeDocument(
            id=doc_id,
            content=content,
            metadata=metadata,
            source="user_feedback",
            content_type="feedback",
            platform=platform,
            category=f"rating_{rating}",
            tags=tags or [platform, f"rating_{rating}"],
            created_at=now,
            updated_at=now
        )

    def add_document(self, document: KnowledgeDocument) -> bool:
        """Add a single document to the knowledge base"""
        try:
            # Save to file system
            self._save_document_to_file(document)

            # Add to vector store
            doc_dict = document.to_dict()
            vector_docs = [{
                "content": document.content,
                "metadata": doc_dict["metadata"],
                "id": document.id
            }]

            return self.vector_store.add_documents(vector_docs)

        except Exception as e:
            print(f"Error adding document {document.id}: {e}")
            return False

    def add_documents(self, documents: List[KnowledgeDocument]) -> bool:
        """Add multiple documents to the knowledge base"""
        try:
            # Save to file system
            for doc in documents:
                self._save_document_to_file(doc)

            # Add to vector store
            vector_docs = []
            for doc in documents:
                vector_docs.append({
                    "content": doc.content,
                    "metadata": doc.to_dict()["metadata"],
                    "id": doc.id
                })

            return self.vector_store.add_documents(vector_docs)

        except Exception as e:
            print(f"Error adding documents: {e}")
            return False

    def _save_document_to_file(self, document: KnowledgeDocument):
        """Save document to file system for backup"""
        content_type_dir = self.knowledge_path / document.content_type
        content_type_dir.mkdir(exist_ok=True)

        file_path = content_type_dir / f"{document.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

    def load_documents_from_files(self) -> List[KnowledgeDocument]:
        """Load documents from file system"""
        documents = []

        for content_type in ["templates", "guidelines", "feedback", "examples"]:
            content_type_dir = self.knowledge_path / content_type
            if not content_type_dir.exists():
                continue

            for file_path in content_type_dir.iterdir():
                if file_path.suffix == ".json":
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            doc_data = json.load(f)

                        # Convert back to KnowledgeDocument
                        doc = KnowledgeDocument(
                            id=doc_data["id"],
                            content=doc_data["content"],
                            metadata=doc_data["metadata"],
                            source=doc_data["source"],
                            created_at=datetime.fromisoformat(doc_data["created_at"]),
                            updated_at=datetime.fromisoformat(doc_data["updated_at"]),
                            content_type=doc_data["content_type"],
                            platform=doc_data.get("platform"),
                            tone=doc_data.get("tone"),
                            category=doc_data.get("category"),
                            tags=doc_data.get("tags", [])
                        )
                        documents.append(doc)

                    except Exception as e:
                        print(f"Error loading document {file_path}: {e}")

        return documents

    def seed_initial_knowledge_base(self):
        """Seed the knowledge base with initial templates and guidelines"""

        # Ad templates for different platforms and tones
        templates = [
            # Instagram templates
            self.create_ad_template(
                "🌟 Transform your daily routine with our revolutionary fitness app! Join 10K+ users achieving their goals. #FitnessRevolution #GetFitToday",
                "instagram", "motivational", "fitness", ["fitness", "motivation", "health"]
            ),
            self.create_ad_template(
                "✨ Elevate your style game with our premium collection. Limited time offer: 30% off everything! Shop now and shine bright. #FashionForward",
                "instagram", "luxury", "fashion", ["fashion", "luxury", "sale"]
            ),

            # Facebook templates
            self.create_ad_template(
                "Discover how our comprehensive business solution helped Sarah increase her revenue by 150% in just 6 months. Read her success story and see how we can help your business grow.",
                "facebook", "professional", "business", ["business", "success", "growth"]
            ),

            # Twitter templates
            self.create_ad_template(
                "🚨 Flash Sale Alert! 50% off all premium plans for the next 24 hours only! Don't miss out ⏰ #LimitedTime #Sale",
                "twitter", "urgent", "general", ["sale", "urgent", "limited"]
            ),

            # LinkedIn templates
            self.create_ad_template(
                "Industry Insight: The future of digital marketing in 2024. Our latest whitepaper reveals key trends and actionable strategies for forward-thinking professionals.",
                "linkedin", "professional", "industry", ["marketing", "insights", "professional"]
            )
        ]

        # Brand guidelines
        guidelines = [
            self.create_brand_guideline(
                "Brand Voice: Professional, knowledgeable, and approachable. Use clear, concise language that demonstrates expertise while remaining accessible to all audiences.",
                "AgenticAds", "voice", ["professional", "approachable", "expertise"]
            ),
            self.create_brand_guideline(
                "Visual Style: Clean, modern design with blue and white color scheme. Use high-quality imagery and maintain consistent typography across all platforms.",
                "AgenticAds", "visual", ["design", "modern", "consistent"]
            ),
            self.create_brand_guideline(
                "Content Guidelines: Focus on value-driven content that educates and empowers users. Avoid aggressive sales language; emphasize solutions and benefits.",
                "AgenticAds", "content", ["value", "education", "benefits"]
            )
        ]

        # Platform-specific best practices
        best_practices = [
            self.create_successful_example(
                "Instagram ads perform best with visually striking images, short compelling copy (under 100 characters), and 5-10 relevant hashtags. Focus on lifestyle and aspirational content.",
                "instagram", "general",
                {"engagement_rate": 0.85, "click_through_rate": 0.03, "conversions": 150},
                ["best_practices", "instagram", "visual"]
            ),
            self.create_successful_example(
                "Facebook ads work well with detailed product descriptions, customer testimonials, and clear call-to-action buttons. Use longer copy that tells a complete story.",
                "facebook", "general",
                {"engagement_rate": 0.65, "click_through_rate": 0.02, "conversions": 200},
                ["best_practices", "facebook", "storytelling"]
            ),
            self.create_successful_example(
                "Twitter ads should be concise, use trending hashtags, and encourage engagement through questions or polls. Keep copy under 100 characters when possible.",
                "twitter", "general",
                {"engagement_rate": 0.45, "click_through_rate": 0.015, "conversions": 75},
                ["best_practices", "twitter", "concise"]
            ),
            self.create_successful_example(
                "LinkedIn ads perform best with professional tone, industry insights, and thought leadership content. Focus on business value and expertise demonstration.",
                "linkedin", "general",
                {"engagement_rate": 0.75, "click_through_rate": 0.025, "conversions": 120},
                ["best_practices", "linkedin", "professional"]
            )
        ]

        # Add all initial documents
        all_documents = templates + guidelines + best_practices

        success = self.add_documents(all_documents)
        if success:
            print(f"Successfully seeded knowledge base with {len(all_documents)} documents")
            
            # Verify vector store has documents
            try:
                if hasattr(self.vector_store, 'collection'):
                    vector_count = self.vector_store.collection.count()
                    print(f"✅ Vector store now contains {vector_count} documents")
                else:
                    print("⚠️  Vector store doesn't have collection attribute")
            except Exception as e:
                print(f"⚠️  Could not verify vector store count: {e}")
        else:
            print("Failed to seed knowledge base")

        return success

    def get_documents_by_filter(self, content_type: Optional[str] = None,
                               platform: Optional[str] = None,
                               tone: Optional[str] = None,
                               category: Optional[str] = None) -> List[KnowledgeDocument]:
        """Retrieve documents based on filters"""
        documents = self.load_documents_from_files()

        filtered_docs = documents

        if content_type:
            filtered_docs = [doc for doc in filtered_docs if doc.content_type == content_type]

        if platform:
            filtered_docs = [doc for doc in filtered_docs if doc.platform == platform]

        if tone:
            filtered_docs = [doc for doc in filtered_docs if doc.tone == tone]

        if category:
            filtered_docs = [doc for doc in filtered_docs if doc.category == category]

        return filtered_docs

    def search_similar_content(self, query: str, n_results: int = 5,
                             platform: Optional[str] = None) -> List[KnowledgeDocument]:
        """Search for similar content using vector similarity"""
        try:
            # Query vector store
            results = self.vector_store.query(
                query_texts=[query],
                n_results=n_results,
                where={"platform": platform} if platform else None
            )

            if not results["documents"] or not results["documents"][0]:
                return []

            # Load full documents based on IDs
            similar_docs = []
            for doc_id in results["metadatas"][0]:
                docs = self.get_documents_by_filter()
                doc = next((d for d in docs if d.id == doc_id), None)
                if doc:
                    similar_docs.append(doc)

            return similar_docs

        except Exception as e:
            print(f"Error searching similar content: {e}")
            return []

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        documents = self.load_documents_from_files()

        # Also try to get stats from vector store
        try:
            vector_count = self.vector_store.collection.count() if hasattr(self.vector_store, 'collection') else 0
            if vector_count > len(documents):
                # Use vector store count if it's higher
                documents = []  # We'll count from vector store instead
                # Note: We can't easily get metadata from vector store without querying,
                # so we'll use file-based stats for now but add the vector count
        except Exception:
            vector_count = 0

        stats = {
            "total_documents": max(len(documents), vector_count),
            "by_content_type": {},
            "by_platform": {},
            "by_tone": {},
            "by_category": {}
        }

        for doc in documents:
            # Count by content type
            content_type = doc.content_type
            stats["by_content_type"][content_type] = stats["by_content_type"].get(content_type, 0) + 1

            # Count by platform
            if doc.platform:
                platform = doc.platform
                stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1

            # Count by tone
            if doc.tone:
                tone = doc.tone
                stats["by_tone"][tone] = stats["by_tone"].get(tone, 0) + 1

            # Count by category
            if doc.category:
                category = doc.category
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        return stats

    async def ingest_from_mongodb(self, mongodb_url: str = "mongodb://localhost:27017",
                                  db_name: str = "agentic_ads"):
        """Ingest historical data from MongoDB"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient

            client = AsyncIOMotorClient(mongodb_url)
            db = client[db_name]

            # Ingest generation history
            generation_collection = db.generation_history
            generations = await generation_collection.find().to_list(length=None)

            generation_docs = []
            for gen in generations:
                if gen.get("status") == "Completed":  # Only successful generations
                    doc = self.create_successful_example(
                        content=gen.get("adText", ""),
                        platform=gen.get("platform", "unknown"),
                        tone=gen.get("tone", "general").lower(),
                        performance_metrics={
                            "engagement_rate": 0.7,  # Placeholder - would need real metrics
                            "click_through_rate": 0.02,
                            "conversions": 1
                        },
                        tags=["historical", "generation_history"]
                    )
                    generation_docs.append(doc)

            # Ingest user feedback
            feedback_collection = db.feedback
            feedbacks = await feedback_collection.find().to_list(length=None)

            feedback_docs = []
            for feedback in feedbacks:
                doc = self.create_user_feedback(
                    content=feedback.get("message", ""),
                    platform=feedback.get("platform", "unknown"),
                    rating=feedback.get("rating", 3),
                    user_id=f"user_{feedback.get('email', 'anonymous')}",
                    tags=["historical", "user_feedback"]
                )
                feedback_docs.append(doc)

            # Add all documents
            all_docs = generation_docs + feedback_docs
            if all_docs:
                success = self.add_documents(all_docs)
                if success:
                    print(f"Successfully ingested {len(all_docs)} documents from MongoDB")
                    return len(all_docs)
                else:
                    print("Failed to ingest documents from MongoDB")
                    return 0
            else:
                print("No documents to ingest from MongoDB")
                return 0

        except Exception as e:
            print(f"Error ingesting from MongoDB: {e}")
            return 0

# Global knowledge base manager instance
knowledge_manager = None

def get_knowledge_manager(config: Optional[RAGConfig] = None) -> KnowledgeBaseManager:
    """Get or create global knowledge base manager instance"""
    global knowledge_manager
    if knowledge_manager is None:
        knowledge_manager = KnowledgeBaseManager(config)
    return knowledge_manager
