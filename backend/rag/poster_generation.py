"""
Poster Generation Agent for AgenticAds RAG system
Generates actual poster images with logo integration
"""

import os
import io
import base64
import aiohttp
import tempfile
import uuid
import aiofiles
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path

@dataclass
class PosterGenerationContext:
    """Context for poster generation with logo integration"""
    platform: str
    tone: str
    brand_guidelines: Optional[str]
    input_text: str
    poster_prompt: str
    logo_data: Optional[bytes] = None
    logo_position: str = "top-right"
    output_format: str = "PNG"

    def get_platform_dimensions(self) -> tuple:
        """Get optimal dimensions for the platform"""
        platform_dimensions = {
            "Instagram": (1080, 1080),    # Square (1:1)
            "LinkedIn": (1200, 627),      # Landscape (1.91:1)
            "Twitter": (1200, 675),       # Landscape (16:9)
            "YouTube": (1280, 720)        # Landscape (16:9)
        }
        return platform_dimensions.get(self.platform, (1080, 1080))  # Default to square

    def get_platform_aspect_ratio_info(self) -> str:
        """Get aspect ratio information for AI prompts"""
        aspect_info = {
            "Instagram": "square format (1:1), perfect for social media feeds",
            "LinkedIn": "landscape format (1.91:1), ideal for professional networking",
            "Twitter": "landscape format (16:9), optimized for tweet cards",
            "YouTube": "landscape format (16:9), perfect for video thumbnails"
        }
        return aspect_info.get(self.platform, "square format (1:1)")

class PosterGenerationAgent:
    """Generates actual poster images using AI models"""

    def __init__(self, context: PosterGenerationContext):
        self.context = context
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_TOKEN", "") or os.getenv("HUGGINGFACE_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.temp_dir = Path(tempfile.gettempdir()) / "agentic_ads_posters"
        self.temp_dir.mkdir(exist_ok=True, parents=True)

        print("🎨 [PosterAgent] Initializing Poster Generation Agent")
        print(f"🎨 [PosterAgent] Platform: {context.platform}")
        print(f"🎨 [PosterAgent] Tone: {context.tone}")
        print(f"🎨 [PosterAgent] HF API key length: {len(self.huggingface_api_key) if self.huggingface_api_key else 0}")
        print(f"🎨 [PosterAgent] Google API key length: {len(self.google_api_key) if self.google_api_key else 0}")
        print(f"🎨 [PosterAgent] Logo data provided: {bool(context.logo_data)}")
        print(f"🎨 [PosterAgent] Logo position: {context.logo_position}")
        print(f"🎨 [PosterAgent] Temp directory: {self.temp_dir}")
        print(f"🎨 [PosterAgent] Temp directory absolute: {self.temp_dir.absolute()}")

        if not self.huggingface_api_key and not self.google_api_key:
            print("⚠️ [PosterAgent] WARNING: No API keys found! Will use fallback posters only.")
            print("⚠️ [PosterAgent] Please set HUGGINGFACE_API_TOKEN or GOOGLE_API_KEY environment variable.")

    async def generate_poster(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a poster image with optional logo integration"""
        print("🎨 [PosterAgent] Starting poster generation...")
        print(f"🎨 [PosterAgent] State keys received: {list(state.keys())}")

        try:
            print("🎨 [PosterAgent] Step 1: Getting poster prompt")
            # Get the poster prompt from the state or context
            poster_prompt_from_state = state.get("poster_prompt")
            poster_prompt_from_context = self.context.poster_prompt

            print(f"🎨 [PosterAgent] From state (len={len(poster_prompt_from_state) if poster_prompt_from_state else 0}): '{poster_prompt_from_state or 'None'}'")
            print(f"🎨 [PosterAgent] From context (len={len(poster_prompt_from_context) if poster_prompt_from_context else 0}): '{poster_prompt_from_context or 'None'}'")

            # Use context poster prompt if state one is invalid/truncated
            if poster_prompt_from_context and (not poster_prompt_from_state or len(poster_prompt_from_state.strip()) < 20):
                print("🎨 [PosterAgent] Using context poster prompt (state one was invalid/truncated)")
                poster_prompt = poster_prompt_from_context
            else:
                poster_prompt = poster_prompt_from_state

            print(f"🎨 [PosterAgent] Final poster prompt (len={len(poster_prompt) if poster_prompt else 0}): '{poster_prompt}'")

            if not poster_prompt:
                print("❌ [PosterAgent] No poster prompt provided!")
                return {
                    **state,
                    "poster_url": "",
                    "poster_file_path": "",
                    "poster_error": "No poster prompt provided"
                }

            print("🎨 [PosterAgent] Step 2: Enhancing prompt")
            # Enhance the prompt for better poster generation
            enhanced_prompt = self._enhance_poster_prompt(poster_prompt)
            print(f"🎨 [PosterAgent] Enhanced prompt (len={len(enhanced_prompt)}): '{enhanced_prompt}'")

            print("🎨 [PosterAgent] Step 3: Generating base image")
            # Generate the base poster image
            base_image = await self._generate_base_image(enhanced_prompt)
            print(f"🎨 [PosterAgent] Base image generated: {base_image.size if hasattr(base_image, 'size') else 'No size attribute'}")

            print("🎨 [PosterAgent] Step 4: Adding logo")
            # Add logo if provided
            final_image = await self._add_logo_to_poster(base_image)
            print(f"🎨 [PosterAgent] Final image ready: {final_image.size if hasattr(final_image, 'size') else 'No size attribute'}")

            print("🎨 [PosterAgent] Step 5: Saving poster to file")
            # Save poster to temporary file
            file_path, download_url = await self._save_poster_to_file(final_image)
            print(f"🎨 [PosterAgent] Poster saved successfully!")
            print(f"🎨 [PosterAgent] File path: {file_path}")
            print(f"🎨 [PosterAgent] Download URL: {download_url}")

            print("🎨 [PosterAgent] Step 6: Returning success result")
            result = {
                **state,
                "poster_url": download_url,
                "poster_file_path": str(file_path),
                "poster_filename": f"poster_{self.context.platform}_{self.context.tone}_{uuid.uuid4().hex[:8]}.png",
                "poster_generation_notes": "Poster generated successfully with AI"
            }
            print(f"🎨 [PosterAgent] Success result: poster_url={result['poster_url'][:50]}...")
            print("✅ [PosterAgent] Poster generation completed successfully")
            return result

        except Exception as e:
            error_msg = f"Error generating poster: {str(e)}"
            print(f"❌ [PosterAgent] Exception caught: {error_msg}")
            import traceback
            print(f"❌ [PosterAgent] Full traceback:")
            traceback.print_exc()

            print("🎨 [PosterAgent] Attempting fallback poster...")
            try:
                print("🎨 [PosterAgent] Creating fallback poster")
                fallback_poster = await self._create_fallback_poster()
                print(f"🎨 [PosterAgent] Fallback poster created: {fallback_poster.size if hasattr(fallback_poster, 'size') else 'No size'}")

                print("🎨 [PosterAgent] Saving fallback poster")
                fallback_file_path, fallback_download_url = await self._save_poster_to_file(fallback_poster)
                print(f"🎨 [PosterAgent] Fallback saved: {fallback_download_url}")

                result = {
                    **state,
                    "poster_url": fallback_download_url,
                    "poster_file_path": str(fallback_file_path),
                    "poster_filename": "fallback_poster.png",
                    "poster_error": error_msg,
                    "poster_generation_notes": "Used fallback poster due to generation error"
                }
                print(f"🎨 [PosterAgent] Fallback result: poster_url={result['poster_url'][:50]}...")
                return result

            except Exception as fallback_error:
                print(f"❌ [PosterAgent] Even fallback poster failed: {str(fallback_error)}")
                import traceback
                print(f"❌ [PosterAgent] Fallback traceback:")
                traceback.print_exc()

                # Last resort - return empty result
                print("❌ [PosterAgent] Returning empty poster result")
                return {
                    **state,
                    "poster_url": "",
                    "poster_file_path": "",
                    "poster_filename": "",
                    "poster_error": f"Both main and fallback generation failed: {error_msg}",
                    "poster_generation_notes": "Failed to generate poster"
                }

    def _enhance_poster_prompt(self, base_prompt: str) -> str:
        """Enhance the poster prompt for better image generation with 80/20 ratio"""

        # Extract the primary user input (80% focus) from the base prompt
        user_input_section = ""
        context_section = ""

        # Parse the structured prompt to maintain 80/20 ratio
        lines = base_prompt.split('\n')
        for line in lines:
            if line.startswith('- PRIMARY CONTENT (80% focus):'):
                user_input_section = line.replace('- PRIMARY CONTENT (80% focus):', '').strip()
            elif line.startswith('- VISUAL ENHANCEMENT (20% inspiration):'):
                context_section = line.replace('- VISUAL ENHANCEMENT (20% inspiration):', '').strip()

        platform_styles = {
            "Instagram": "modern, vibrant, social media style, square format, eye-catching, trendy",
            "LinkedIn": "professional, corporate, clean design, business-oriented, landscape format, executive",
            "Twitter": "concise, impactful, bold typography, attention-grabbing, landscape format, viral",
            "YouTube": "engaging, video thumbnail style, cinematic, dramatic, landscape format, compelling"
        }

        tone_styles = {
            "professional": "clean, sophisticated, corporate colors, formal, trustworthy, premium",
            "casual": "friendly, approachable, warm colors, relaxed, conversational, inviting",
            "energetic": "dynamic, vibrant colors, exciting, bold, high-energy, motivational",
            "fun": "playful, colorful, humorous, light-hearted, joyful, entertaining",
            "witty": "clever, sophisticated humor, smart design, engaging, charming, intelligent"
        }

        platform_style = platform_styles.get(self.context.platform, "modern, professional, visually appealing")
        tone_style = tone_styles.get(self.context.tone, "balanced, effective, engaging")
        aspect_ratio_info = self.context.get_platform_aspect_ratio_info()

        # Get platform-specific dimensions
        width, height = self.context.get_platform_dimensions()

        # Enhanced prompt with strict 80/20 ratio enforcement
        enhanced_prompt = f"""
        Create a professional, high-quality {self.context.platform} social media post image with:

        📱 PLATFORM: {self.context.platform} - {aspect_ratio_info}
        📏 DIMENSIONS: {width}x{height} pixels (exact aspect ratio required)
        🎨 STYLE: {platform_style}, {tone_style}
        🎯 PURPOSE: Optimized for {self.context.platform} platform specifications and audience engagement

        🎨 VISUAL DESIGN REQUIREMENTS:
        - Perfect aspect ratio composition for {self.context.platform}
        - Strong visual hierarchy with clear focal points
        - Professional typography that's easy to read
        - Appropriate color scheme matching {self.context.platform} brand guidelines
        - High-contrast elements for social media visibility
        - Clean, modern layout with proper spacing
        - Optimized for mobile viewing and quick engagement

        📝 PRIMARY CONTENT (80% FOCUS - USER INPUT):
        {user_input_section}

        🎯 VISUAL ENHANCEMENT (20% INSPIRATION - DESIGN CONTEXT):
        {context_section}

        🎯 BRANDING ELEMENTS:
        - Logo positioned in top-right corner (small, non-intrusive)
        - Brand colors incorporated naturally
        - Professional and trustworthy appearance
        - Social media optimized for shares and engagement

        🔧 TECHNICAL SPECIFICATIONS:
        - Exact dimensions: {width}x{height} pixels
        - RGB color space (255, 255, 255)
        - High resolution (300 DPI equivalent) for crisp display
        - Optimized file size under 5MB for fast loading
        - PNG format with transparency support if needed

        🚀 PERFORMANCE OPTIMIZATION:
        - Fast loading on mobile devices
        - Clear visibility on various screen sizes
        - High engagement potential with proper visual flow
        - Professional appearance that builds trust
        """

        return enhanced_prompt.strip()

    async def _save_poster_to_file(self, image: Image.Image) -> tuple[Path, str]:
        """Save poster image to temporary file and return file path and download URL"""
        print(f"🎨 [PosterAgent] _save_poster_to_file: Starting with image size {image.size if hasattr(image, 'size') else 'unknown'}")

        # Generate unique filename
        filename = f"poster_{self.context.platform}_{self.context.tone}_{uuid.uuid4().hex[:8]}.png"
        file_path = self.temp_dir / filename

        print(f"🎨 [PosterAgent] _save_poster_to_file: Saving to {file_path}")
        print(f"🎨 [PosterAgent] _save_poster_to_file: Temp dir exists: {self.temp_dir.exists()}")

        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(exist_ok=True, parents=True)

        # Save image to file
        try:
            image.save(file_path, format='PNG')
            print(f"🎨 [PosterAgent] _save_poster_to_file: Image saved successfully")
            print(f"🎨 [PosterAgent] _save_poster_to_file: File exists after save: {file_path.exists()}")
            print(f"🎨 [PosterAgent] _save_poster_to_file: File size: {file_path.stat().st_size} bytes")
        except Exception as save_error:
            print(f"❌ [PosterAgent] _save_poster_to_file: Failed to save image: {str(save_error)}")
            raise save_error

        # Create download URL (relative to static files)
        download_url = f"/api/posters/download/{filename}"

        print(f"💾 [PosterAgent] Poster saved to: {file_path}")
        print(f"🔗 [PosterAgent] Download URL: {download_url}")

        return file_path, download_url

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')

    async def _generate_base_image(self, prompt: str) -> Image.Image:
        """Generate the base poster image using AI APIs"""
        print(f"🎨 [PosterAgent] Generating base image with prompt: {prompt[:100]}...")

        # Try HuggingFace first, then Google, then fallback
        if self.huggingface_api_key:
            print("🎨 [PosterAgent] Using HuggingFace API")
            return await self._generate_with_huggingface(prompt)
        elif self.google_api_key:
            print("🎨 [PosterAgent] Using Google API")
            return await self._generate_with_google(prompt)
        else:
            print("❌ [PosterAgent] NO API KEYS FOUND!")
            print("❌ [PosterAgent] Set HUGGINGFACE_API_KEY or GOOGLE_API_KEY environment variable to generate real AI images")
            print("❌ [PosterAgent] Using fallback poster instead")
            return await self._create_fallback_poster()

    async def _generate_with_huggingface(self, prompt: str) -> Image.Image:
        """Generate image using HuggingFace API"""
        # Get platform-specific dimensions
        width, height = self.context.get_platform_dimensions()

        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": width,
                "height": height,
                "negative_prompt": "blurry, low quality, text, watermark, signature, ugly, deformed"
            }
        }

        print(f"🎨 [PosterAgent] Making HuggingFace API call: {api_url}")
        print(f"🎨 [PosterAgent] Using dimensions: {width}x{height}")
        print(f"🎨 [PosterAgent] API key starts with: {self.huggingface_api_key[:10]}...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers, timeout=60) as response:
                    print(f"🎨 [PosterAgent] HuggingFace API response status: {response.status}")

                    if response.status == 200:
                        image_bytes = await response.read()
                        print(f"🎨 [PosterAgent] Successfully received {len(image_bytes)} bytes from HuggingFace API")

                        try:
                            image = Image.open(io.BytesIO(image_bytes))
                            print(f"✅ [PosterAgent] Successfully generated AI image: {image.size}")
                            return image
                        except Exception as img_error:
                            print(f"❌ [PosterAgent] Failed to parse image from HuggingFace response: {str(img_error)}")
                            return await self._create_fallback_poster()

                    elif response.status == 401:
                        print(f"❌ [PosterAgent] HuggingFace API authentication failed (401)")
                        print(f"❌ [PosterAgent] Check your HUGGINGFACE_API_KEY")
                        return await self._create_fallback_poster()

                    elif response.status == 503:
                        print(f"⚠️ [PosterAgent] HuggingFace API is busy (503), trying Google API")
                        if self.google_api_key:
                            return await self._generate_with_google(prompt)
                        return await self._create_fallback_poster()

                    else:
                        error_text = await response.text()
                        print(f"❌ [PosterAgent] HuggingFace API Error: {response.status} - {error_text}")
                        return await self._create_fallback_poster()

        except Exception as e:
            print(f"❌ [PosterAgent] Exception during HuggingFace API call: {str(e)}")
            import traceback
            print(f"❌ [PosterAgent] Exception traceback: {traceback.format_exc()}")
            return await self._create_fallback_poster()

    async def _generate_with_google(self, prompt: str) -> Image.Image:
        """Generate image using Google AI API"""
        print("🎨 [PosterAgent] Google API not yet implemented, using fallback")
        return await self._create_fallback_poster()

    async def _add_logo_to_poster(self, base_image: Image.Image) -> Image.Image:
        """Add logo to the poster at specified position"""
        if not self.context.logo_data:
            print("ℹ️ [PosterAgent] No logo provided, returning base image")
            return base_image

        try:
            print("🎨 [PosterAgent] Adding logo to poster...")

            # Ensure base image is in RGBA for proper compositing
            if base_image.mode != "RGBA":
                base_image = base_image.convert("RGBA")
                print("🎨 [PosterAgent] Converted base image to RGBA")

            # Load the logo image as RGBA
            logo_image = Image.open(io.BytesIO(self.context.logo_data))
            if logo_image.mode != "RGBA":
                logo_image = logo_image.convert("RGBA")
            print(f"🎨 [PosterAgent] Logo loaded: {logo_image.size} format: {logo_image.format}")

            # Calculate logo position and size
            logo_size = self._calculate_logo_size(base_image.size)
            print(f"🎨 [PosterAgent] Calculated logo size: {logo_size}")

            # Resize logo to calculated size
            logo_image = logo_image.resize(logo_size, Image.Resampling.LANCZOS)
            print(f"🎨 [PosterAgent] Logo resized to: {logo_image.size}")

            # Determine placement (default top-right)
            position = self._get_logo_position(base_image.size, logo_size, self.context.logo_position)
            padding = 12
            bg_position = (max(position[0] - padding, 0), max(position[1] - padding, 0))
            print(f"🎨 [PosterAgent] Logo position: {position} ({self.context.logo_position})")

            # Prepare final image copy
            final_image = base_image.copy()
            print(f"🎨 [PosterAgent] Created final image copy: {final_image.size}")

            # Create enhanced background for better logo visibility
            logo_bg = self._create_logo_background((logo_size[0] + padding * 2, logo_size[1] + padding * 2))

            # Paste background and logo with transparency
            final_image.paste(logo_bg, bg_position, logo_bg)
            final_image.paste(logo_image, (bg_position[0] + padding, bg_position[1] + padding), logo_image)

            print(f"✅ [PosterAgent] Logo successfully added at {self.context.logo_position} position")
            print(f"✅ [PosterAgent] Final poster size: {final_image.size}")
            return final_image

        except Exception as e:
            print(f"❌ [PosterAgent] Error adding logo: {str(e)}")
            import traceback
            print(f"❌ [PosterAgent] Logo error traceback: {traceback.format_exc()}")
            raise RuntimeError("Failed to apply logo to poster") from e

    def _calculate_logo_size(self, poster_size: tuple) -> tuple:
        """Calculate appropriate logo size based on poster dimensions"""
        width, height = poster_size

        # Logo should be about 1/8 of the poster width, but not too large
        max_logo_width = min(width // 6, 200)
        max_logo_height = min(height // 8, 150)

        # Maintain aspect ratio
        if width > height:
            # Landscape poster - use height-based sizing
            logo_height = int(max_logo_height * (width / height))
            return (min(width // 8, max_logo_width), min(logo_height, max_logo_height))
        else:
            # Square or portrait poster - use width-based sizing
            logo_width = int(max_logo_width * (height / width))
            return (min(logo_width, max_logo_width), min(height // 10, max_logo_height))

    def _get_logo_position(self, poster_size: tuple, logo_size: tuple, position: str) -> tuple:
        """Calculate logo position based on specified location"""
        poster_width, poster_height = poster_size
        logo_width, logo_height = logo_size

        margin = 20  # Margin from edges

        positions = {
            "top-left": (margin, margin),
            "top-right": (poster_width - logo_width - margin, margin),
            "bottom-left": (margin, poster_height - logo_height - margin),
            "bottom-right": (poster_width - logo_width - margin, poster_height - logo_height - margin),
            "center": ((poster_width - logo_width) // 2, (poster_height - logo_height) // 2)
        }

        return positions.get(position, positions["top-right"])

    def _create_logo_background(self, bg_size: tuple) -> Image.Image:
        """Create a semi-transparent background for better logo visibility"""
        width, height = bg_size

        # Base background with rounded corners
        bg = Image.new('RGBA', (width, height), (24, 24, 27, 180))  # semi-transparent dark backdrop
        draw = ImageDraw.Draw(bg)

        # Draw rounded rectangle border
        radius = 12
        draw.rounded_rectangle(
            [(2, 2), (width - 2, height - 2)],
            radius=radius,
            outline=(255, 255, 255, 200),
            width=2
        )

        print(f"🎨 [PosterAgent] Created logo background: {(width, height)} with transparency")
        return bg

    async def _create_fallback_poster(self) -> Image.Image:
        """Create a fallback poster when generation fails"""
        print("🎨 [PosterAgent] _create_fallback_poster: Starting fallback poster creation")

        try:
            # Get platform-specific dimensions for fallback
            width, height = self.context.get_platform_dimensions()
            print(f"🎨 [PosterAgent] _create_fallback_poster: Using dimensions {width}x{height}")

            # Create a simple gradient background
            print("🎨 [PosterAgent] _create_fallback_poster: Creating simple gradient background")
            image = Image.new('RGB', (width, height), color=(59, 130, 246))  # Blue background
            print(f"🎨 [PosterAgent] _create_fallback_poster: Created base image {image.size}")

            # Add a simple gradient effect
            draw = ImageDraw.Draw(image)
            for y in range(height):
                # Create a vertical gradient
                r = int(59 + (y / height) * 20)
                g = int(130 + (y / height) * 20)
                b = int(246 + (y / height) * 10)
                draw.line([(0, y), (width, y)], fill=(r, g, b))

            print(f"🎨 [PosterAgent] _create_fallback_poster: Added gradient effect")

            # Try to add simple text without font loading
            try:
                print("🎨 [PosterAgent] _create_fallback_poster: Adding simple text")
                # Use default font
                font = ImageFont.load_default()

                # Add title
                title_text = f"{self.context.platform} Poster"
                draw.text((width//2 - 100, height//3), title_text, fill=(255, 255, 255), font=font)

                # Add subtitle
                subtitle_text = f"{self.context.tone.title()} • Fallback"
                draw.text((width//2 - 100, height//2), subtitle_text, fill=(255, 255, 255), font=font)

                print(f"🎨 [PosterAgent] _create_fallback_poster: Added text overlay")

            except Exception as text_error:
                print(f"⚠️ [PosterAgent] _create_fallback_poster: Text overlay failed: {str(text_error)}")
                # Continue without text - still return the image

            print(f"🎨 [PosterAgent] _create_fallback_poster: Fallback poster created successfully")
            return image

        except Exception as e:
            print(f"❌ [PosterAgent] _create_fallback_poster: Failed to create fallback poster: {str(e)}")
            import traceback
            print(f"❌ [PosterAgent] _create_fallback_poster: Traceback: {traceback.format_exc()}")

            # Last resort - create a very basic image
            try:
                print(f"🎨 [PosterAgent] _create_fallback_poster: Creating basic fallback image")
                basic_image = Image.new('RGB', (400, 400), color=(128, 128, 128))
                return basic_image
            except Exception as basic_error:
                print(f"❌ [PosterAgent] _create_fallback_poster: Even basic image failed: {str(basic_error)}")
                raise e

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
