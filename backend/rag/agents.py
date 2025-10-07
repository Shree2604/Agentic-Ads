"""
Agent implementations for AgenticAds RAG system
Multi-agent orchestration for text, poster, and video generation
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from langchain_core.language_models.llms import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import chromadb
from sentence_transformers import SentenceTransformer

@dataclass
class AgentContext:
    """Shared context for all agents"""
    platform: str
    tone: str
    brand_guidelines: Optional[str]
    input_text: str
    vector_store: Any
    llm_model: Any
    embedding_model: Any

class BaseAgent:
    """Base class for all agents"""

    def __init__(self, name: str, context: AgentContext):
        self.name = name
        self.context = context
        self.llm = context.llm_model
        self.vector_store = context.vector_store
        self.embedding_model = context.embedding_model

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic - to be implemented by subclasses"""
        raise NotImplementedError

    def _retrieve_context(self, query: str, n_results: int = 5) -> List[str]:
        """Retrieve relevant context from vector store"""
        try:
            results = self.vector_store.query(
                query_texts=[query],
                n_results=n_results,
                where={"platform": self.context.platform, "tone": self.context.tone}
            )
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            print(f"Error retrieving context: {e}")
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

    async def _generate_text(self, prompt: str) -> str:
        """Generate text using the LLM"""
        try:
            # Use the LLM pipeline to generate text
            result = self.llm(prompt, max_new_tokens=200, temperature=0.7)
            return result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            return f"Generated copy for {self.context.platform}: {self.context.input_text} (powered by AI)"

class VisualDesignerAgent(BaseAgent):
    """Creates poster design prompts with brand consistency"""

    def __init__(self, context: AgentContext):
        super().__init__("VisualDesignerAgent", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate poster design prompts"""
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
        generated_text = state.get("generated_text", "")
        poster_prompt = state.get("poster_prompt", "")
        video_script = state.get("video_script", "")

        # Quality checks
        quality_scores = {}

        # Check text quality
        text_score = self._check_text_quality(generated_text)
        quality_scores["text"] = text_score

        # Check poster prompt quality
        poster_score = self._check_poster_quality(poster_prompt)
        quality_scores["poster"] = poster_score

        # Check video script quality
        video_score = self._check_video_quality(video_script)
        quality_scores["video"] = video_score

        # Overall assessment
        overall_score = sum(quality_scores.values()) / len(quality_scores)

        validation_feedback = {
            "text_feedback": self._generate_text_feedback(text_score),
            "poster_feedback": self._generate_poster_feedback(poster_score),
            "video_feedback": self._generate_video_feedback(video_score),
            "overall_assessment": "PASS" if overall_score >= 7 else "NEEDS_IMPROVEMENT"
        }

        return {
            **state,
            "quality_scores": quality_scores,
            "validation_feedback": validation_feedback,
            "qa_notes": f"Overall quality score: {overall_score:.1f}/10"
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
            result = self.llm(prompt, max_new_tokens=150, temperature=0.5)
            return result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            return f"Error in generation: {str(e)}"
