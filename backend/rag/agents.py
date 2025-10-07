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

        # Create prompt for text generation
        context_str = "\n".join(research_context[:5]) if research_context else "No specific examples found."

        prompt = f"""
        You are a professional copywriter creating {self.context.tone} content for {self.context.platform}.

        Context from successful examples:
        {context_str}

        Brand guidelines: {self.context.brand_guidelines or 'No specific guidelines provided.'}

        Original request: {input_text}

        Generate compelling, platform-optimized copy that:
        - Matches the {self.context.tone} tone
        - Is optimized for {self.context.platform} platform
        - Follows brand guidelines
        - Engages the target audience
        - Includes relevant hashtags and calls-to-action

        Output only the generated text copy:
        """

        try:
            # Generate text using the LLM
            generated_text = await self._generate_text(prompt)

            return {
                **state,
                "generated_text": generated_text,
                "copywriter_notes": f"Generated {len(generated_text)} characters of {self.context.tone} copy for {self.context.platform}"
            }
        except Exception as e:
            return {
                **state,
                "generated_text": f"Error generating text: {str(e)}",
                "copywriter_notes": "Failed to generate copy"
            }

    def _generate_text(self, prompt: str) -> str:
        """Generate text using the Hugging Face model"""
        try:
            # Get relevant examples from the vector store with fallback
            examples = self._retrieve_context(
                f"{self.context.platform} {self.context.tone} ad examples",
                n_results=3
            )
            
            if not examples:
                # Try a more general query if specific search fails
                examples = self._retrieve_context(
                    "successful ad examples",
                    n_results=2
                )
            
            # Convert examples to proper format, adding basic metadata
            context_examples = []
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
                    print(f"Error processing example: {e}")
                    continue
            
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
            
            # Generate text using our text generation service
            generated_text = self.text_generator.generate_ad(
                context=context_examples,
                platform=self.context.platform,
                tone=self.context.tone,
                input_text=self.context.input_text
            )
            
            if not generated_text or len(generated_text.strip()) < 10:
                raise ValueError("Generated text too short or empty")
            
            return generated_text
            
        except Exception as e:
            print(f"Error in text generation: {str(e)}")
            # Provide a more specific fallback based on the error
            if "403" in str(e) or "Forbidden" in str(e):
                fallback_text = (
                    f"🚀 {self.context.input_text}\n\n"
                    f"#{self.context.platform.lower()} #innovation"
                )
            elif "timeout" in str(e).lower():
                fallback_text = (
                    f"⚡ Fast-track your success with our cutting-edge solutions!\n\n"
                    f"#{self.context.platform.lower()} #success"
                )
            else:
                fallback_text = (
                    f"✨ Transform your experience with our premium offerings!\n\n"
                    f"#{self.context.platform.lower()} #premium"
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

        prompt = f"""
        You are a visual designer creating design prompts for AI image generation.

        Design Context:
        {visual_inspiration}

        Text to visualize: {generated_text}
        Platform: {self.context.platform}
        Tone: {self.context.tone}
        Brand guidelines: {self.context.brand_guidelines or 'Modern, professional design'}

        Create a detailed prompt for AI image generation that:
        - Captures the {self.context.tone} mood
        - Is optimized for {self.context.platform} format
        - Maintains brand consistency
        - Is visually compelling and attention-grabbing
        - Uses appropriate colors, typography, and layout

        Output format: "Generate a [platform] [tone] poster image of [detailed description]"
        """

        try:
            design_prompt = await self._generate_text(prompt)

            return {
                **state,
                "poster_prompt": design_prompt,
                "visual_designer_notes": f"Created design prompt for {self.context.platform} {self.context.tone} poster"
            }
        except Exception as e:
            return {
                **state,
                "poster_prompt": f"Error generating poster prompt: {str(e)}",
                "visual_designer_notes": "Failed to generate design prompt"
            }

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

        prompt = f"""
        You are a video scriptwriter creating engaging video narratives.

        Video Inspiration:
        {video_inspiration}

        Text to adapt for video: {generated_text}
        Platform: {self.context.platform}
        Tone: {self.context.tone}

        Create a video script with:
        - 3-5 key scenes
        - Voiceover narration
        - Visual descriptions for each scene
        - Appropriate pacing for {self.context.platform}
        - {self.context.tone} emotional tone

        Format your response as:
        SCENE 1: [Visual description]
        NARRATION: [Voiceover text]

        SCENE 2: [Visual description]
        NARRATION: [Voiceover text]
        """

        try:
            video_script = await self._generate_text(prompt)

            return {
                **state,
                "video_script": video_script,
                "video_scriptwriter_notes": f"Created video script for {self.context.platform} with {self.context.tone} tone"
            }
        except Exception as e:
            return {
                **state,
                "video_script": f"Error generating video script: {str(e)}",
                "video_scriptwriter_notes": "Failed to generate video script"
            }

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
            "qa_notes": f"Overall quality score: {overall_score:.1f}/10 for requested outputs: {', '.join(output_types)}"
        }

    def _check_text_quality(self, text: str) -> float:
        """Score text quality on scale of 1-10"""
        score = 5.0  # Base score

        if not text or "Error" in text:
            return 1.0

        # Check length
        if len(text) > 100:
            score += 2
        elif len(text) > 50:
            score += 1

        # Check platform relevance
        if self.context.platform.lower() in text.lower():
            score += 1

        # Check tone relevance
        if self.context.tone.lower() in text.lower():
            score += 1

        # Check for hashtags and CTA
        if "#" in text or "!" in text or "?" in text:
            score += 1

        return min(score, 10.0)

    def _check_poster_quality(self, prompt: str) -> float:
        """Score poster prompt quality"""
        score = 5.0

        if not prompt or "Error" in prompt:
            return 1.0

        # Check for descriptive elements
        if any(word in prompt.lower() for word in ["color", "layout", "typography", "design"]):
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
            return 1.0

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
            return "Text needs significant platform and tone optimization"

    def _generate_poster_feedback(self, score: float) -> str:
        if score >= 8:
            return "Strong visual design prompt with clear platform adaptation"
        elif score >= 6:
            return "Decent design prompt but could be more visually descriptive"
        else:
            return "Design prompt needs more detail and platform specificity"

    def _generate_video_feedback(self, score: float) -> str:
        if score >= 8:
            return "Well-structured video script with clear scene progression"
        elif score >= 6:
            return "Good script foundation but needs more visual detail"
        else:
            return "Video script needs better structure and scene descriptions"

    async def _generate_text(self, prompt: str) -> str:
        """Generate text using the LLM"""
        try:
            # Use the text generator service instead of undefined llm attribute
            return self.text_generator.generate_ad(
                context=[{"content": prompt, "metadata": {"platform": self.context.platform, "tone": self.context.tone}}],
                platform=self.context.platform,
                tone=self.context.tone,
                input_text=prompt
            )
        except Exception as e:
            return f"Error in generation: {str(e)}"
