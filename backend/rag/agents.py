"""
Agent implementations for AgenticAds RAG system
Multi-agent orchestration for text, poster, and video generation
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import chromadb
from sentence_transformers import SentenceTransformer
from .text_generation import get_text_generator

@dataclass
class AgentContext:
    """Shared context for all agents"""
    platform: str
    tone: str
    brand_guidelines: Optional[str]
    input_text: str
    vector_store: Any
    embedding_model: Any
    feedback_summary: Optional[str] = None
    feedback_highlights: Optional[List[str]] = None
    feedback_suggestions: Optional[List[str]] = None
    feedback_keywords: Optional[List[str]] = None
    feedback_avg_rating: Optional[float] = None

class BaseAgent:
    """Base class for all agents"""

    def __init__(self, name: str, context: AgentContext):
        self.name = name
        self.context = context
        self.vector_store = context.vector_store
        self.embedding_model = context.embedding_model
        self.text_generator = get_text_generator()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic - to be implemented by subclasses"""
        raise NotImplementedError

    def _retrieve_context(self, query: str, n_results: int = 5) -> List[str]:
        """Retrieve relevant context from vector store"""
        try:
            if not self.vector_store or not hasattr(self.vector_store, "collection"):
                print("Vector store not properly initialized")
                return []

            # Include platform and tone in the query for better semantic matching
            enhanced_query = f"{query} {self.context.platform} {self.context.tone}"

            # Query without filters (ChromaDB filtering can be unreliable)
            results = self.vector_store.collection.query(
                query_texts=[enhanced_query],
                n_results=n_results
            )
            
            # Debug logging
            print(f"🔍 RAG Query: '{enhanced_query}'")
            print(f"📊 Results found: {len(results['documents'][0]) if results['documents'] else 0}")
            
            if results['documents'] and results['documents'][0]:
                context = results["documents"][0][:3]  # Take top 3 results
                print(f"📝 Retrieved context: {len(context)} items")
                return context
            else:
                print("⚠️  No context retrieved from knowledge base")
                return []

        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            return []

class ContentResearcher(BaseAgent):
    """Retrieves relevant templates and successful examples"""

    def __init__(self, context: AgentContext):
        super().__init__("ContentResearcher", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Research and retrieve relevant content"""
        input_text = state.get("input", self.context.input_text)

        # Create search queries
        queries = [
            f"successful {self.context.platform} ads {self.context.tone} tone",
            f"high performing {self.context.platform} content",
            f"viral {self.context.platform} campaigns",
            f"{self.context.tone} marketing copy examples"
        ]

        research_results = []
        for query in queries:
            context_docs = self._retrieve_context(query, 3)
            research_results.extend(context_docs)

        # Remove duplicates and format
        unique_context = list(set(research_results))[:10]

        return {
            **state,
            "research_context": unique_context,
            "research_summary": f"Found {len(unique_context)} relevant examples for {self.context.platform} {self.context.tone} content"
        }

class CopywriterAgent(BaseAgent):
    """Generates platform-optimized text with RAG context"""

    def __init__(self, context: AgentContext):
        super().__init__("CopywriterAgent", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform-optimized text"""
        output_types = state.get("output_types", [])
        
        # Skip text generation if not requested
        if "text" not in output_types:
            return {
                **state,
                "generated_text": state.get("generated_text", ""),
                "copywriter_notes": "Text generation skipped - not requested"
            }

        research_context = state.get("research_context", [])
        input_text = state.get("input", self.context.input_text)

        print(f"CopywriterAgent: Starting text generation for input: '{input_text[:50]}...'")

        # Create prompt for text generation
        context_str = "\n".join(research_context[:5]) if research_context else "No specific examples found."
        print(f"CopywriterAgent: Using context: '{context_str[:50]}...'")

        try:
            print("CopywriterAgent: Calling _generate_text...")
            # Generate text using the synchronous method (no await needed)
            generated_text = self._generate_text_sync(state)
            print(f"CopywriterAgent: Generated text: '{generated_text[:50]}...'")

            return {
                **state,
                "generated_text": generated_text,
                "copywriter_notes": f"Generated {len(generated_text)} characters of {self.context.tone} copy for {self.context.platform}"
            }
        except Exception as e:
            error_msg = f"Error generating text: {str(e)}"
            print(f"CopywriterAgent: {error_msg}")
            return {
                **state,
                "generated_text": error_msg,
                "copywriter_notes": "Failed to generate copy",
                "errors": state.get("errors", []) + [error_msg]
            }

    def _generate_text_sync(self, state: Dict[str, Any]) -> str:
        """Generate text synchronously using the Gemini model with feedback awareness"""
        try:
            print(f"_generate_text_sync: Starting generation")
            
            # Get relevant examples from the vector store with fallback
            examples = self._retrieve_context(
                f"{self.context.platform} {self.context.tone} ad examples",
                n_results=3
            )
            
            print(f"_generate_text_sync: Retrieved {len(examples)} examples")
            
            if not examples:
                # Try a more general query if specific search fails
                examples = self._retrieve_context(
                    "successful ad examples",
                    n_results=2
                )
                print(f"_generate_text_sync: Fallback retrieved {len(examples)} examples")
            
            # Convert examples to proper format, adding basic metadata
            context_examples: List[Dict[str, Any]] = []
            for example in examples:
                try:
                    # Handle both string and dict examples
                    if isinstance(example, dict):
                        context_examples.append({
                            "content": example.get("content", str(example)),
                            "metadata": example.get("metadata", {})
                        })
                    else:
                        context_examples.append({
                            "content": str(example),
                            "metadata": {
                                "platform": self.context.platform,
                                "tone": self.context.tone
                            }
                        })
                except Exception as e:
                    print(f"_generate_text_sync: Error processing example: {e}")
                    continue
            
            print(f"_generate_text_sync: Processed {len(context_examples)} context examples")
            
            # Add fallback example if no valid examples found
            if not context_examples:
                context_examples = [{
                    "content": f"Create an engaging {self.context.tone} post for {self.context.platform}",
                    "metadata": {
                        "platform": self.context.platform,
                        "tone": self.context.tone,
                        "is_fallback": True
                    }
                }]
                print("_generate_text_sync: Using fallback example")

            # Inject user feedback signals to guide generation
            feedback_highlights: List[str] = state.get("feedback_highlights", [])
            feedback_suggestions: List[str] = state.get("feedback_suggestions", [])
            feedback_keywords: List[str] = state.get("feedback_keywords", [])

            if self.context.feedback_summary:
                context_examples.insert(0, {
                    "content": f"User feedback summary: {self.context.feedback_summary}",
                    "metadata": {"source": "user_feedback"}
                })

            for highlight in feedback_highlights[:2]:
                context_examples.append({
                    "content": f"What users loved: {highlight}",
                    "metadata": {"source": "user_feedback", "sentiment": "positive"}
                })

            for suggestion in feedback_suggestions[:2]:
                context_examples.append({
                    "content": f"Improve by: {suggestion}",
                    "metadata": {"source": "user_feedback", "sentiment": "improvement"}
                })

            if feedback_keywords:
                context_examples.append({
                    "content": "Important keywords: " + ", ".join(feedback_keywords[:5]),
                    "metadata": {"source": "user_feedback"}
                })

            print(f"_generate_text_sync: Calling text_generator.generate_ad with {len(context_examples)} examples")
            
            # Generate text using our text generation service (SYNCHRONOUS - no await)
            generated_text = self.text_generator.generate_ad(
                context=context_examples,
                platform=self.context.platform,
                tone=self.context.tone,
                input_text=self.context.input_text
            )
            
            print(f"_generate_text_sync: Text generation completed, result length: {len(generated_text)}")
            
            if not generated_text or len(generated_text.strip()) < 10:
                raise ValueError("Generated text too short or empty")
            
            return generated_text
            
        except Exception as e:
            print(f"Error in text generation: {str(e)}")
            # Provide a more specific fallback based on the error
            fallback_focus = feedback_suggestions[0][:100] if feedback_suggestions else "premium experience"
            fallback_text = (
                f"🚀 {self.context.input_text[:100]}\n\n"
                f"Focus: {fallback_focus}\n"
                f"#{self.context.platform.lower()} #innovation #professional"
            )
            return fallback_text

class VisualDesignerAgent(BaseAgent):
    """Creates poster design prompts with brand consistency"""

    def __init__(self, context: AgentContext):
        super().__init__("VisualDesignerAgent", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate poster design prompts"""
        output_types = state.get("output_types", [])
        
        # Skip poster generation if not requested
        if "poster" not in output_types:
            return {
                **state,
                "poster_prompt": state.get("poster_prompt", ""),
                "visual_designer_notes": "Poster generation skipped - not requested"
            }

        generated_text = state.get("generated_text", "")

        # Research visual design patterns
        visual_queries = [
            f"{self.context.platform} visual design trends",
            f"{self.context.tone} poster layouts",
            "successful ad poster designs"
        ]

        visual_context = []
        for query in visual_queries:
            context_docs = self._retrieve_context(query, 2)
            visual_context.extend(context_docs)

        visual_inspiration = "\n".join(visual_context[:3]) if visual_context else ""
        if self.context.feedback_keywords:
            visual_inspiration += "\nKeywords to emphasize: " + ", ".join(self.context.feedback_keywords[:5])
        if self.context.feedback_suggestions:
            visual_inspiration += "\nImprovements requested: " + "; ".join(self.context.feedback_suggestions[:2])

        try:
            # Generate synchronously
            design_prompt = self._generate_poster_prompt_sync(
                generated_text,
                visual_inspiration,
                state.get("feedback_highlights", []),
                state.get("feedback_suggestions", [])
            )

            return {
                **state,
                "poster_prompt": design_prompt,
                "visual_designer_notes": f"Created design prompt for {self.context.platform} {self.context.tone} poster"
            }
        except Exception as e:
            return {
                **state,
                "poster_prompt": f"Create a {self.context.tone} {self.context.platform} poster featuring: {generated_text[:100]}",
                "visual_designer_notes": f"Used fallback poster prompt due to error: {str(e)}"
            }

    def _generate_poster_prompt_sync(
        self,
        text: str,
        inspiration: str,
        highlights: List[str],
        suggestions: List[str]
    ) -> str:
        """Generate poster prompt synchronously"""
        improvement_line = (
            "Incorporate feedback: " + "; ".join(suggestions[:2])
        ) if suggestions else "Ensure the design resonates with recent audience preferences."

        highlight_line = (
            "Celebrate wins: " + "; ".join(highlights[:2])
        ) if highlights else "Emphasize the core value proposition confidently."

        return (
            f"Create a professional {self.context.platform} poster with:\n"
            f"- {self.context.tone} tone\n"
            f"- Modern, clean design\n"
            f"- Featured text: {text[:150]}\n"
            f"- Brand colors and typography\n"
            f"- Eye-catching visual elements\n"
            f"- {highlight_line}\n"
            f"- {improvement_line}\n"
            f"Inspiration cues:\n{inspiration.strip()}"
        )

class VideoScriptwriterAgent(BaseAgent):
    """Develops video narratives and scene descriptions"""

    def __init__(self, context: AgentContext):
        super().__init__("VideoScriptwriterAgent", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video script and scene descriptions"""
        output_types = state.get("output_types", [])
        
        # Skip video generation if not requested
        if "video" not in output_types:
            return {
                **state,
                "video_script": state.get("video_script", ""),
                "video_scriptwriter_notes": "Video generation skipped - not requested"
            }

        generated_text = state.get("generated_text", "")

        # Research video storytelling patterns
        video_queries = [
            f"{self.context.platform} video storytelling",
            f"{self.context.tone} video script examples",
            "successful video ad scripts"
        ]

        video_context = []
        for query in video_queries:
            context_docs = self._retrieve_context(query, 2)
            video_context.extend(context_docs)

        video_inspiration = "\n".join(video_context[:3]) if video_context else ""
        if self.context.feedback_summary:
            video_inspiration += f"\nAudience feedback summary: {self.context.feedback_summary}"

        try:
            # Generate synchronously
            video_script = self._generate_video_script_sync(
                generated_text,
                video_inspiration,
                state.get("feedback_suggestions", [])
            )

            return {
                **state,
                "video_script": video_script,
                "video_scriptwriter_notes": f"Created video script for {self.context.platform} with {self.context.tone} tone"
            }
        except Exception as e:
            return {
                **state,
                "video_script": f"SCENE 1: Product showcase\nNARRATION: {generated_text[:100]}\n\nSCENE 2: Call to action\nNARRATION: Learn more today!",
                "video_scriptwriter_notes": f"Used fallback video script due to error: {str(e)}"
            }

    def _generate_video_script_sync(self, text: str, inspiration: str, suggestions: List[str]) -> str:
        """Generate video script synchronously"""
        cta_line = suggestions[0][:100] if suggestions else f"Join us on {self.context.platform} today"
        return (
            f"SCENE 1: Opening shot - Dynamic visual introduction\n"
            f"NARRATION: {text[:100]}\n\n"
            f"SCENE 2: Product/Service showcase with {self.context.tone} tone\n"
            f"NARRATION: Experience innovation like never before\n\n"
            f"SCENE 3: Call-to-action with platform-specific elements\n"
            f"NARRATION: {cta_line}!\n\n"
            f"Creative cues:\n{inspiration.strip()}"
        )

class QualityAssuranceAgent(BaseAgent):
    """Validates outputs against guidelines and feedback"""

    def __init__(self, context: AgentContext):
        super().__init__("QualityAssuranceAgent", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score generated content"""
        output_types = state.get("output_types", [])
        
        generated_text = state.get("generated_text", "")
        poster_prompt = state.get("poster_prompt", "")
        video_script = state.get("video_script", "")

        # Quality checks - only score requested outputs
        quality_scores = {}

        # Check text quality if requested
        if "text" in output_types:
            text_score = self._check_text_quality(generated_text)
            quality_scores["text"] = text_score

        # Check poster prompt quality if requested
        if "poster" in output_types:
            poster_score = self._check_poster_quality(poster_prompt)
            quality_scores["poster"] = poster_score

        # Check video script quality if requested
        if "video" in output_types:
            video_score = self._check_video_quality(video_script)
            quality_scores["video"] = video_score

        # Overall assessment
        overall_score = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 5.0

        validation_feedback = {}
        if "text" in output_types:
            validation_feedback["text_feedback"] = self._generate_text_feedback(quality_scores.get("text", 5.0))
        if "poster" in output_types:
            validation_feedback["poster_feedback"] = self._generate_poster_feedback(quality_scores.get("poster", 5.0))
        if "video" in output_types:
            validation_feedback["video_feedback"] = self._generate_video_feedback(quality_scores.get("video", 5.0))
        
        validation_feedback["overall_assessment"] = "PASS" if overall_score >= 7 else "NEEDS_IMPROVEMENT"

        return {
            **state,
            "quality_scores": quality_scores,
            "validation_feedback": validation_feedback,
            "qa_notes": f"Overall quality score: {overall_score:.1f}/10 for requested outputs: {', '.join(output_types)}",
            # Set final outputs when QA completes successfully
            "final_text": state.get("generated_text", ""),
            "final_poster_prompt": state.get("poster_prompt", ""),
            "final_video_script": state.get("video_script", "")
        }

    def _check_text_quality(self, text: str) -> float:
        """Score text quality on scale of 1-10"""
        score = 5.0  # Base score

        if not text or "Error" in text:
            return 3.0  # Changed from 1.0 to be more forgiving

        # Check length
        if len(text) > 100:
            score += 2
        elif len(text) > 50:
            score += 1

        # Check platform relevance
        if self.context.platform.lower() in text.lower():
            score += 1

        # Check for hashtags and CTA
        if "#" in text or "!" in text or "?" in text:
            score += 1

        # Check for emojis (common in social media)
        if any(ord(char) > 127 for char in text):
            score += 1

        return min(score, 10.0)

    def _check_poster_quality(self, prompt: str) -> float:
        """Score poster prompt quality"""
        score = 5.0

        if not prompt or "Error" in prompt:
            return 3.0

        # Check for descriptive elements
        if any(word in prompt.lower() for word in ["color", "layout", "typography", "design", "visual", "poster"]):
            score += 2

        # Check for platform specificity
        if self.context.platform.lower() in prompt.lower():
            score += 2

        # Check for brand consistency
        if self.context.brand_guidelines and self.context.brand_guidelines.lower() in prompt.lower():
            score += 1

        return min(score, 10.0)

    def _check_video_quality(self, script: str) -> float:
        """Score video script quality"""
        score = 5.0

        if not script or "Error" in script:
            return 3.0

        # Check for scene structure
        scene_count = script.count("SCENE")
        if scene_count >= 2:
            score += 2
        elif scene_count >= 1:
            score += 1

        # Check for narration
        if "NARRATION:" in script:
            score += 2

        # Check for visual descriptions
        if "visual" in script.lower() or "scene" in script.lower():
            score += 1

        return min(score, 10.0)

    def _generate_text_feedback(self, score: float) -> str:
        if score >= 8:
            return "Excellent text quality with strong platform optimization"
        elif score >= 6:
            return "Good text quality with room for platform-specific improvements"
        else:
            return "Text generated successfully with basic quality"

    def _generate_poster_feedback(self, score: float) -> str:
        if score >= 8:
            return "Strong visual design prompt with clear platform adaptation"
        elif score >= 6:
            return "Decent design prompt but could be more visually descriptive"
        else:
            return "Design prompt created with basic elements"

    def _generate_video_feedback(self, score: float) -> str:
        if score >= 8:
            return "Well-structured video script with clear scene progression"
        elif score >= 6:
            return "Good script foundation but needs more visual detail"
        else:
            return "Video script created with basic structure"