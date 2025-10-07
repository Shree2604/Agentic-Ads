"""
Text chunking utilities for optimal RAG retrieval
Implements various chunking strategies for different content types
"""

import re
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    content: str
    start_index: int
    end_index: int
    metadata: Dict[str, Any]
    chunk_id: str

class TextChunker:
    """Advanced text chunking for RAG optimization"""

    def __init__(self,
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 separator: str = "\n\n"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """Chunk text using size-based strategy"""
        if not metadata:
            metadata = {}

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))

            # Try to find a good breaking point
            if end < len(text):
                # Look for separator within the last 100 characters
                search_start = max(start, end - 100)
                separator_pos = text.rfind(self.separator, search_start, end)

                if separator_pos != -1 and separator_pos > start:
                    end = separator_pos + len(self.separator)
                else:
                    # Look for sentence endings
                    sentence_endings = ['. ', '! ', '? ', '\n']
                    for ending in sentence_endings:
                        pos = text.rfind(ending, search_start, end)
                        if pos != -1 and pos > start:
                            end = pos + len(ending)
                            break

            # Extract chunk
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunk = Chunk(
                    content=chunk_content,
                    start_index=start,
                    end_index=end,
                    metadata=metadata.copy(),
                    chunk_id=f"chunk_{len(chunks)}"
                )
                chunks.append(chunk)

            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def chunk_by_sentences(self, text: str, metadata: Optional[Dict[str, Any]] = None,
                          max_chunk_size: int = 512) -> List[Chunk]:
        """Chunk text by sentences while respecting size limits"""
        if not metadata:
            metadata = {}

        # Split into sentences
        sentences = re.split(r'([.!?]+)', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""
        current_start = 0

        for i, sentence in enumerate(sentences):
            # Add sentence to current chunk
            potential_chunk = current_chunk + sentence if current_chunk else sentence

            # Check if adding this sentence would exceed size limit
            if len(potential_chunk) > max_chunk_size and current_chunk:
                # Save current chunk
                chunk = Chunk(
                    content=current_chunk.strip(),
                    start_index=current_start,
                    end_index=current_start + len(current_chunk),
                    metadata=metadata.copy(),
                    chunk_id=f"chunk_{len(chunks)}"
                )
                chunks.append(chunk)

                # Start new chunk
                current_chunk = sentence
                current_start = current_start + len(current_chunk)
            else:
                current_chunk = potential_chunk

        # Add final chunk
        if current_chunk:
            chunk = Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata=metadata.copy(),
                chunk_id=f"chunk_{len(chunks)}"
            )
            chunks.append(chunk)

        return chunks

    def chunk_by_paragraphs(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """Chunk text by paragraphs"""
        if not metadata:
            metadata = {}

        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []

        for i, paragraph in enumerate(paragraphs):
            chunk = Chunk(
                content=paragraph,
                start_index=0,  # Would need original text to calculate properly
                end_index=len(paragraph),
                metadata=metadata.copy(),
                chunk_id=f"chunk_{i}"
            )
            chunks.append(chunk)

        return chunks

    def chunk_markdown_sections(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """Chunk markdown content by sections (headers)"""
        if not metadata:
            metadata = {}

        chunks = []
        lines = text.split('\n')

        current_section = ""
        current_start = 0
        current_metadata = metadata.copy()

        for i, line in enumerate(lines):
            # Check if line is a header
            if line.startswith('#'):
                # Save previous section if it exists
                if current_section.strip():
                    chunk = Chunk(
                        content=current_section.strip(),
                        start_index=current_start,
                        end_index=i,
                        metadata=current_metadata,
                        chunk_id=f"chunk_{len(chunks)}"
                    )
                    chunks.append(chunk)

                # Start new section
                current_section = line + '\n'
                current_start = i

                # Extract section level and title
                header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if header_match:
                    level = len(header_match.group(1))
                    title = header_match.group(2)
                    current_metadata.update({
                        "section_level": level,
                        "section_title": title
                    })
            else:
                current_section += line + '\n'

        # Add final section
        if current_section.strip():
            chunk = Chunk(
                content=current_section.strip(),
                start_index=current_start,
                end_index=len(lines),
                metadata=current_metadata,
                chunk_id=f"chunk_{len(chunks)}"
            )
            chunks.append(chunk)

        return chunks

class AdaptiveChunker:
    """Adaptive chunker that chooses best strategy based on content"""

    def __init__(self):
        self.base_chunker = TextChunker()

    def chunk_content(self, content: str, content_type: str = "text",
                     metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """Choose appropriate chunking strategy based on content type"""

        if content_type == "markdown":
            return self.base_chunker.chunk_markdown_sections(content, metadata)
        elif content_type == "structured":
            return self.base_chunker.chunk_by_paragraphs(content, metadata)
        elif content_type == "conversational":
            return self.base_chunker.chunk_by_sentences(content, metadata)
        else:
            # Default size-based chunking
            return self.base_chunker.chunk_text(content, metadata)

    def get_optimal_chunk_size(self, content_type: str, platform: str = None) -> int:
        """Get optimal chunk size based on content type and platform"""

        # Platform-specific chunk sizes
        if platform == "twitter":
            return 280  # Twitter's character limit
        elif platform == "instagram":
            return 400  # Optimal for Instagram captions
        elif platform == "facebook":
            return 600  # Good for Facebook posts
        elif platform == "linkedin":
            return 800  # Suitable for LinkedIn articles

        # Content type specific sizes
        if content_type == "short_form":
            return 300
        elif content_type == "long_form":
            return 1000
        elif content_type == "technical":
            return 600
        else:
            return 512  # Default

def create_chunks_for_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create chunks for a list of documents"""

    chunker = AdaptiveChunker()
    chunked_documents = []

    for doc in documents:
        content = doc.get("content", "")
        content_type = doc.get("content_type", "text")
        metadata = doc.get("metadata", {})

        chunks = chunker.chunk_content(content, content_type, metadata)

        for chunk in chunks:
            chunked_documents.append({
                "content": chunk.content,
                "metadata": {
                    **chunk.metadata,
                    "original_id": doc.get("id"),
                    "chunk_id": chunk.chunk_id,
                    "chunk_start": chunk.start_index,
                    "chunk_end": chunk.end_index
                },
                "id": f"{doc.get('id', 'unknown')}_{chunk.chunk_id}"
            })

    return chunked_documents

def calculate_chunk_similarity(chunk1: Chunk, chunk2: Chunk) -> float:
    """Calculate similarity between two chunks (simple overlap-based)"""

    # Simple Jaccard similarity for tokens
    tokens1 = set(chunk1.content.lower().split())
    tokens2 = set(chunk2.content.lower().split())

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))

    return intersection / union if union > 0 else 0.0
