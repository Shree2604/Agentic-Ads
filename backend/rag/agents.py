import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import chromadb
from sentence_transformers import SentenceTransformer
from .text_generation import get_text_generator
from .poster_generation import PosterGenerationAgent, PosterGenerationContext
from .video_generation import VideoGIFGenerationAgent, VideoGenerationContext
import tempfile
import uuid
import aiofiles
from pathlib import Path
import io
from PIL import Image

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
    logo_data: Optional[bytes] = None
    logo_position: str = "top-right"

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

            enhanced_query = f"{query} {self.context.platform} {self.context.tone}"
            results = self.vector_store.collection.query(
                query_texts=[enhanced_query],
                n_results=n_results
            )
            
            print(f"🔍 RAG Query: '{enhaled_query}'")
            print(f"📊 Results found: {len(results['documents'][0]) if results['documents'] else 0}")
            
            if results and results['documents'] and len(results['documents'][0]) > 0:
                context = results["documents"][0][:3]
                print(f"📚 Retrieved context: {len(context)} items")
                return context
            else:
                print("⚠️  No context retrieved from knowledge base")
                return []
                
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return []

class LogoIntegrationAgent(BaseAgent):
    """Handles logo upload, temporary storage, and integration into final posters"""

    def __init__(self, context: AgentContext):
        super().__init__("LogoIntegrationAgent", context)
        self.temp_logo_dir = Path(tempfile.gettempdir()) / "agentic_ads_logos"
        self.temp_logo_dir.mkdir(exist_ok=True, parents=True)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process logo upload and prepare for poster integration"""
        print("🎨 LogoIntegrationAgent: Starting logo processing...")

        logo_file = state.get("logo_file")
        if not logo_file:
            print("ℹ️ LogoIntegrationAgent: No logo file provided")
            return {
                **state,
                "logo_processed": False,
                "logo_integration_notes": "No logo file to process"
            }

        try:
            print(f"🎨 LogoIntegrationAgent: Processing logo file: {logo_file.filename}")

            logo_data = await logo_file.read()
            print(f"🎨 LogoIntegrationAgent: Logo file read, size: {len(logo_data)} bytes")

            if not self._validate_logo_file(logo_data):
                print("❌ LogoIntegrationAgent: Invalid logo file format")
                return {
                    **state,
                    "logo_processed": False,
                    "logo_error": "Invalid logo file format. Please upload a PNG, JPG, or SVG file.",
                    "logo_integration_notes": "Logo validation failed"
                }

            logo_id = f"logo_{uuid.uuid4().hex[:12]}"
            logo_path = await self._save_logo_temporarily(logo_data, logo_id, logo_file.filename)
            print(f"🎨 LogoIntegrationAgent: Logo saved to: {logo_path}")

            updated_context = self.context
            updated_context.logo_data = logo_data
            updated_context.logo_position = state.get("logo_position", "top-right")

            print(f"🎨 LogoIntegrationAgent: Logo prepared for integration at {updated_context.logo_position}")

            return {
                **state,
                "logo_processed": True,
                "logo_data": logo_data,
                "logo_id": logo_id,
                "logo_path": str(logo_path),
                "logo_filename": logo_file.filename,
                "logo_size": len(logo_data),
                "logo_integration_notes": f"Logo '{logo_file.filename}' ready for poster integration"
            }

        except Exception as e:
            error_msg = f"Error processing logo: {str(e)}"
            print(f"❌ LogoIntegrationAgent: {error_msg}")
            return {
                **state,
                "logo_processed": False,
                "logo_error": error_msg,
                "logo_integration_notes": "Logo processing failed"
            }

    def _validate_logo_file(self, logo_data: bytes) -> bool:
        """Validate that the uploaded file is a valid image"""
        try:
            image = Image.open(io.BytesIO(logo_data))

            if len(logo_data) > 5 * 1024 * 1024:
                print("❌ LogoIntegrationAgent: Logo file too large (>5MB)")
                return False

            width, height = image.size
            if width > 2000 or height > 2000:
                print("❌ LogoIntegrationAgent: Logo dimensions too large (>2000px)")
                return False

            valid_formats = ['PNG', 'JPEG', 'JPG', 'SVG', 'WEBP']
            if image.format and image.format.upper() not in valid_formats:
                print(f"❌ LogoIntegrationAgent: Unsupported format: {image.format}")
                return False

            print(f"✅ LogoIntegrationAgent: Valid logo - {image.format} {width}x{height}")
            return True

        except Exception as e:
            print(f"❌ LogoIntegrationAgent: Logo validation failed: {str(e)}")
            return False

    async def _save_logo_temporarily(self, logo_data: bytes, logo_id: str, original_filename: str) -> Path:
        """Save logo file temporarily with unique ID"""
        file_extension = Path(original_filename).suffix.lower() or ".png"
        temp_filename = f"{logo_id}{file_extension}"
        temp_path = self.temp_logo_dir / temp_filename

        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(logo_data)

        print(f"💾 LogoIntegrationAgent: Logo saved to temporary file: {temp_path}")
        return temp_path

    def cleanup_temp_logo(self, logo_id: str):
        """Clean up temporary logo file"""
        try:
            for logo_file in self.temp_logo_dir.glob(f"{logo_id}.*"):
                logo_file.unlink()
                print(f"🧹 LogoIntegrationAgent: Cleaned up temp logo: {logo_file}")
        except Exception as e:
            print(f"⚠️ LogoIntegrationAgent: Failed to cleanup logo {logo_id}: {str(e)}")


class PosterFinalizationAgent(BaseAgent):
    """Finalizes posters with logo integration and cleanup"""

    def __init__(self, context: AgentContext):
        super().__init__("PosterFinalizationAgent", context)
        self.logo_agent = LogoIntegrationAgent(context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize poster with proper logo integration"""
        print("🎨 PosterFinalizationAgent: Starting poster finalization...")

        logo_processed = state.get("logo_processed", False)

        if not logo_processed:
            print("ℹ️ PosterFinalizationAgent: No logo to integrate")
            return {
                **state,
                "poster_finalized": True,
                "finalization_notes": "No logo integration needed"
            }

        try:
            # Get logo information
            logo_id = state.get("logo_id")
            poster_url = state.get("poster_url")

            if not logo_id or not poster_url:
                print("⚠️ PosterFinalizationAgent: Missing logo or poster data")
                return {
                    **state,
                    "poster_finalized": False,
                    "finalization_notes": "Missing logo or poster data for finalization"
                }

            print(f"🎨 PosterFinalizationAgent: Finalizing poster with logo {logo_id}")

            # Clean up temporary logo file after successful integration
            if hasattr(self, 'logo_agent') and self.logo_agent:
                self.logo_agent.cleanup_temp_logo(logo_id)

            print("✅ PosterFinalizationAgent: Poster finalization completed successfully")

            return {
                **state,
                "poster_finalized": True,
                "finalization_notes": "Poster finalized with logo integration and cleanup completed"
            }

        except Exception as e:
            error_msg = f"Error finalizing poster: {str(e)}"
            print(f"❌ PosterFinalizationAgent: {error_msg}")
            return {
                **state,
                "poster_finalized": False,
                "finalization_notes": error_msg
            }


# Rest of the imports and class definitions
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import chromadb
from sentence_transformers import SentenceTransformer
from .text_generation import get_text_generator
from .poster_generation import PosterGenerationAgent, PosterGenerationContext
from .video_generation import VideoGIFGenerationAgent, VideoGenerationContext
import tempfile
import uuid
import aiofiles
from pathlib import Path
import io
from PIL import Image

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
    logo_data: Optional[bytes] = None
    logo_position: str = "top-right"

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

            enhanced_query = f"{query} {self.context.platform} {self.context.tone}"
            results = self.vector_store.collection.query(
                query_texts=[enhanced_query],
                n_results=n_results
            )
            
            print(f"🔍 RAG Query: '{enhanced_query}'")
            print(f"📊 Results found: {len(results['documents'][0]) if results['documents'] else 0}")
            
            if results['documents'] and results['documents'][0]:
                context = results["documents"][0][:3]
                print(f"📚 Retrieved context: {len(context)} items")
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
        
        if "text" not in output_types:
            return {
                **state,
                "generated_text": state.get("generated_text", ""),
                "copywriter_notes": "Text generation skipped - not requested"
            }

        research_context = state.get("research_context", [])
        input_text = state.get("input", self.context.input_text)

        print(f"CopywriterAgent: Starting text generation for input: '{input_text[:50]}...'")

        context_str = "\n".join(research_context[:5]) if research_context else "No specific examples found."
        print(f"CopywriterAgent: Using context: '{context_str[:50]}...'")

        try:
            print("CopywriterAgent: Calling _generate_text...")
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
            
            examples = self._retrieve_context(
                f"{self.context.platform} {self.context.tone} ad examples",
                n_results=3
            )
            
            print(f"_generate_text_sync: Retrieved {len(examples)} examples")
            
            if not examples:
                examples = self._retrieve_context("successful ad examples", n_results=2)
                print(f"_generate_text_sync: Fallback retrieved {len(examples)} examples")
            
            context_examples: List[Dict[str, Any]] = []
            for example in examples:
                try:
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
            fallback_focus = feedback_suggestions[0][:100] if feedback_suggestions else "premium experience"
            fallback_text = (
                f"🚀 {self.context.input_text[:100]}\n\n"
                f"Focus: {fallback_focus}\n"
                f"#{self.context.platform.lower()} #innovation #professional"
            )
            return fallback_text

class VisualDesignerAgent(BaseAgent):
    """Creates poster design prompts and generates actual poster images with logo integration"""

    def __init__(self, context: AgentContext):
        super().__init__("VisualDesignerAgent", context)
        self.poster_agent = None

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate poster design prompts and actual poster images"""
        output_types = state.get("output_types", [])

        print(f"VisualDesignerAgent: Starting execution with output_types: {output_types}")

        if "poster" not in output_types:
            print("VisualDesignerAgent: Poster generation skipped - not requested")
            return {
                **state,
                "poster_prompt": state.get("poster_prompt", ""),
                "poster_url": state.get("poster_url", ""),
                "visual_designer_notes": "Poster generation skipped - not requested"
            }

        print("VisualDesignerAgent: Poster generation requested - starting process")
        generated_text = state.get("generated_text", "")
        logo_data = state.get("logo_data")
        logo_position = state.get("logo_position", "top-right")

        print(f"🎨 VisualDesignerAgent: Logo data available: {bool(logo_data)}")
        print(f"🎨 VisualDesignerAgent: Logo data size: {len(logo_data) if logo_data else 0} bytes")
        print(f"🎨 VisualDesignerAgent: Logo position: {logo_position}")

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
            design_prompt = self._generate_poster_prompt_sync(
                generated_text,
                visual_inspiration,
                state.get("feedback_highlights", []),
                state.get("feedback_suggestions", [])
            )

            print(f"VisualDesignerAgent: Generated poster prompt: {design_prompt[:100]}...")

            poster_context = PosterGenerationContext(
                platform=self.context.platform,
                tone=self.context.tone,
                brand_guidelines=self.context.brand_guidelines,
                input_text=self.context.input_text,
                poster_prompt=design_prompt,
                logo_data=logo_data,
                logo_position=logo_position
            )

            self.poster_agent = PosterGenerationAgent(poster_context)
            poster_state = await self.poster_agent.generate_poster({
                "poster_prompt": design_prompt,
                **state
            })

            print(f"VisualDesignerAgent: Poster generation result: poster_url={poster_state.get('poster_url', 'None')[:50]}...")
            print(f"VisualDesignerAgent: Poster generation completed. URL: {poster_state.get('poster_url', 'None')[:50]}...")

            return {
                **state,
                **poster_state,
                "visual_designer_notes": f"Created design prompt and generated poster for {self.context.platform} {self.context.tone}"
            }

        except Exception as e:
            error_msg = f"Error in poster generation: {str(e)}"
            print(f"VisualDesignerAgent: {error_msg}")
            import traceback
            print(f"VisualDesignerAgent: Traceback: {traceback.format_exc()}")
            return {
                **state,
                "poster_prompt": f"Create a {self.context.tone} {self.context.platform} poster featuring: {generated_text[:100]}",
                "poster_url": "",
                "visual_designer_notes": f"Poster generation failed: {error_msg}"
            }

    def _generate_poster_prompt_sync(
        self,
        text: str,
        inspiration: str,
        highlights: List[str],
        suggestions: List[str]
    ) -> str:
        """Generate detailed poster prompt focused on visual design from user's ad text"""

        user_text = text[:300]
        visual_elements = self._extract_visual_elements(user_text)

        prompt_parts = [
            f"Create a professional {self.context.platform} poster design featuring the ad content: '{user_text}'",
            "",
            "**VISUAL DESIGN REQUIREMENTS:**",
            f"- Primary visual theme: {visual_elements.get('theme', 'Modern and professional')}",
            f"- Color scheme: {visual_elements.get('colors', 'Professional blue and white palette')}",
            f"- Layout style: {visual_elements.get('layout', 'Clean, modern layout with clear visual hierarchy')}",
            "",
            "**CONTENT INTEGRATION:**",
            "- Main headline text should be prominently displayed",
            "- Supporting text should complement the main message",
            "- Include relevant visual metaphors or icons that represent the ad content",
            "- Ensure text is readable and well-positioned",
            "",
            "**PLATFORM OPTIMIZATION:**",
            f"- Optimized for {self.context.platform} platform specifications",
            f"- Use {self.context.tone} visual tone throughout",
            "- Include appropriate visual elements for social media engagement",
            "",
            "**TECHNICAL SPECIFICATIONS:**",
            "- High-quality, professional design",
            "- Proper contrast for text readability",
            "- Brand-appropriate styling",
            "- Mobile-friendly layout"
        ]

        if inspiration and len(inspiration.strip()) > 0:
            prompt_parts.extend([
                "",
                "**DESIGN INSPIRATION:**",
                f"Consider these design elements: {inspiration[:150]}"
            ])

        if highlights or suggestions:
            prompt_parts.extend([
                "",
                "**ENHANCEMENT NOTES:**"
            ])
            if highlights:
                prompt_parts.append(f"- Strengthen: {highlights[0][:100]}")
            if suggestions:
                prompt_parts.append(f"- Improve: {suggestions[0][:100]}")

        return "\n".join(prompt_parts)

    def _extract_visual_elements(self, text: str) -> Dict[str, str]:
        """Extract visual design elements from ad text content"""
        text_lower = text.lower()

        theme_keywords = {
            'technology': ['tech', 'digital', 'innovation', 'future', 'smart', 'ai', 'app'],
            'lifestyle': ['life', 'home', 'family', 'comfort', 'relax', 'peace'],
            'business': ['business', 'corporate', 'professional', 'career', 'success', 'growth'],
            'creative': ['creative', 'design', 'art', 'music', 'color', 'inspire'],
            'food': ['food', 'restaurant', 'delicious', 'taste', 'cook', 'recipe'],
            'fitness': ['fitness', 'health', 'workout', 'gym', 'exercise', 'strong']
        }

        theme = "Modern and professional"
        for theme_name, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                theme = f"Professional {theme_name} theme"
                break

        colors = "Professional blue and white palette"
        if 'creative' in theme or 'art' in text_lower:
            colors = "Vibrant and creative color palette"
        elif 'business' in theme:
            colors = "Corporate blue and gray palette"
        elif 'food' in text_lower:
            colors = "Warm, appetizing colors"

        layout = "Clean, modern layout with clear visual hierarchy"
        if 'tech' in theme or 'innovation' in text_lower:
            layout = "Modern, tech-focused layout with clean lines"

        return {
            'theme': theme,
            'colors': colors,
            'layout': layout
        }

class VideoScriptwriterAgent(BaseAgent):
    """Develops video narratives, scene descriptions, and generates actual video GIFs"""

    def __init__(self, context: AgentContext):
        super().__init__("VideoScriptwriterAgent", context)
        self.video_agent = None

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video script and actual video GIF"""
        output_types = state.get("output_types", [])
        
        print(f"VideoScriptwriterAgent: Starting execution with output_types: {output_types}")
        
        # Skip video generation if not requested
        if "video" not in output_types:
            print("VideoScriptwriterAgent: Video generation skipped - not requested")
            return {
                **state,
                "video_script": state.get("video_script", ""),
                "video_scriptwriter_notes": "Video generation skipped - not requested"
            }

        print("VideoScriptwriterAgent: Video generation requested - starting process")
        generated_text = state.get("generated_text", "")
        logo_data = state.get("logo_data")
        logo_position = state.get("logo_position", "top-right")

        print(f"🎬 VideoScriptwriterAgent: Logo data available: {bool(logo_data)}")
        print(f"🎬 VideoScriptwriterAgent: Logo data size: {len(logo_data) if logo_data else 0} bytes")
        print(f"🎬 VideoScriptwriterAgent: Logo position: {logo_position}")

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
            # Generate video script
            video_script = self._generate_video_script_sync(
                generated_text,
                video_inspiration,
                state.get("feedback_suggestions", [])
            )

            print(f"VideoScriptwriterAgent: Generated video script: {video_script[:100]}...")

            # Initialize video generation context
            video_context = VideoGenerationContext(
                platform=self.context.platform,
                tone=self.context.tone,
                brand_guidelines=self.context.brand_guidelines,
                input_text=self.context.input_text,
                video_script=video_script,
                logo_data=logo_data,
                logo_position=logo_position,
                frame_count=5,
                frame_duration_ms=1100
            )

            # Create video generation agent
            self.video_agent = VideoGIFGenerationAgent(video_context)
            
            # Generate the actual video GIF
            video_state = await self.video_agent.generate_gif({
                "video_script": video_script,
                **state
            })

            print(f"VideoScriptwriterAgent: Video generation result: video_gif_url={video_state.get('video_gif_url', 'None')[:50]}...")

            return {
                **state,
                "video_script": video_script,  # Explicitly include the generated script
                **video_state,
                "video_scriptwriter_notes": f"Created video script and generated GIF for {self.context.platform} with {self.context.tone} tone"
            }

        except Exception as e:
            error_msg = f"Error in video generation: {str(e)}"
            print(f"VideoScriptwriterAgent: {error_msg}")
            import traceback
            print(f"VideoScriptwriterAgent: Traceback: {traceback.format_exc()}")
            
            # Return fallback script
            fallback_script = f"SCENE 1: Product showcase\nNARRATION: {generated_text[:100]}\n\nSCENE 2: Call to action\nNARRATION: Learn more today!"
            return {
                **state,
                "video_script": f"SCENE 1: Product showcase\nNARRATION: {generated_text[:100]}\n\nSCENE 2: Call to action\nNARRATION: Learn more today!",
                "video_gif_url": None,
                "video_scriptwriter_notes": f"Video generation failed: {error_msg}"
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

# ... (Keep LogoIntegrationAgent and PosterFinalizationAgent classes unchanged)

class QualityAssuranceAgent(BaseAgent):

    def __init__(self, context: AgentContext):
        super().__init__("QualityAssuranceAgent", context)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score generated content"""
        output_types = state.get("output_types", [])
        
        generated_text = state.get("generated_text", "")
        poster_prompt = state.get("poster_prompt", "")
        video_script = state.get("video_script", "")
        video_gif_url = state.get("video_gif_url")

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
            video_score = self._check_video_quality(video_script, video_gif_url)
            quality_scores["video"] = video_score

        # Overall assessment
        overall_score = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 5.0

        validation_feedback = {}
        if "text" in output_types:
            validation_feedback["text_feedback"] = self._generate_text_feedback(quality_scores.get("text", 5.0))
        if "poster" in output_types:
            validation_feedback["poster_feedback"] = self._generate_poster_feedback(quality_scores.get("poster", 5.0))
        if "video" in output_types:
            validation_feedback["video_feedback"] = self._generate_video_feedback(quality_scores.get("video", 5.0), video_gif_url)
        
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
        score = 5.0
        if not text or "Error" in text:
            return 3.0

        if len(text) > 100:
            score += 2
        elif len(text) > 50:
            score += 1

        if self.context.platform.lower() in text.lower():
            score += 1

        if "#" in text or "!" in text or "?" in text:
            score += 1

        if any(ord(char) > 127 for char in text):
            score += 1

        return min(score, 10.0)

    def _check_poster_quality(self, prompt: str) -> float:
        """Score poster prompt quality"""
        score = 5.0
        if not prompt or "Error" in prompt:
            return 3.0

        if any(word in prompt.lower() for word in ["color", "layout", "typography", "design", "visual", "poster"]):
            score += 2

        if self.context.platform.lower() in prompt.lower():
            score += 2

        if self.context.brand_guidelines and self.context.brand_guidelines.lower() in prompt.lower():
            score += 1

        return min(score, 10.0)

    def _check_video_quality(self, script: str, video_url: Optional[str]) -> float:
        """Score video script and GIF quality"""
        score = 5.0

        if not script or "Error" in script:
            return 3.0

        # Check for scene structure
        scene_count = script.count("SCENE")
        if scene_count >= 2:
            score += 1.5
        elif scene_count >= 1:
            score += 0.5

        # Check for narration
        if "NARRATION:" in script:
            score += 1.5

        # Check for visual descriptions
        if "visual" in script.lower() or "scene" in script.lower():
            score += 1

        # Bonus points if actual video GIF was generated
        if video_url:
            score += 2

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

    def _generate_video_feedback(self, score: float, video_url: Optional[str]) -> str:
        if score >= 8:
            video_status = " and video GIF generated successfully" if video_url else ""
            return f"Well-structured video script with clear scene progression{video_status}"
        elif score >= 6:
            return "Good script foundation but needs more visual detail"
        else:
            return "Video script created with basic structure"