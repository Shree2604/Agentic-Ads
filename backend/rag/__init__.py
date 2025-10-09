"""
Agentic RAG System for AgenticAds
Main module for LangGraph-based multi-agent ad generation
"""

from .agents import (
    ContentResearcher,
    CopywriterAgent,
    VisualDesignerAgent,
    VideoScriptwriterAgent,
    QualityAssuranceAgent
)
from .graph import create_generation_graph, run_generation_workflow
from .config import RAGConfig
from .vector_store import VectorStoreManager, get_vector_store
from .enhanced_vector_store import EnhancedVectorStore, get_enhanced_vector_store
from .knowledge_base import KnowledgeBaseManager, get_knowledge_manager, KnowledgeDocument
from .chunking import TextChunker, AdaptiveChunker, Chunk, create_chunks_for_documents
from .video_generation import VideoGIFGenerationAgent, VideoGenerationContext

__version__ = "1.0.0"
__all__ = [
    "ContentResearcher",
    "CopywriterAgent",
    "VisualDesignerAgent",
    "VideoScriptwriterAgent",
    "QualityAssuranceAgent",
    "VideoGIFGenerationAgent",
    "VideoGenerationContext",
    "create_generation_graph",
    "run_generation_workflow",
    "RAGConfig",
    "VectorStoreManager",
    "get_vector_store",
    "EnhancedVectorStore",
    "get_enhanced_vector_store",
    "KnowledgeBaseManager",
    "get_knowledge_manager",
    "KnowledgeDocument",
    "TextChunker",
    "AdaptiveChunker",
    "Chunk",
    "create_chunks_for_documents"
]
