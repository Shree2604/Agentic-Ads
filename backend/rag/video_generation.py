"""Video GIF generation utilities for AgenticAds RAG system."""

import os
import io
import uuid
import asyncio
import aiohttp
import tempfile
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


@dataclass
class VideoGenerationContext:
    """Context data required to generate a short-form video GIF."""

    platform: str
    tone: str
    brand_guidelines: Optional[str]
    input_text: str
    video_script: str
    logo_data: Optional[bytes] = None
    logo_position: str = "top-right"
    frame_count: int = 5
    frame_duration_ms: int = 1100

    def get_dimensions(self) -> Tuple[int, int]:
        """Return optimal dimensions (width, height) for vertical short-form video."""
        platform_dimensions = {
            "Instagram": (720, 1280),       # 9:16 reels
            "Facebook": (720, 1280),
            "YouTube": (720, 1280),
            "TikTok": (720, 1280),
            "LinkedIn": (720, 1280)
        }
        return platform_dimensions.get(self.platform, (720, 1280))


class VideoGIFGenerationAgent:
    """Generates animated GIF reels using text prompts and optional logo overlays."""

    def __init__(self, context: VideoGenerationContext):
        self.context = context
        self.huggingface_api_key = (
            os.getenv("HUGGINGFACE_API_TOKEN")
            or os.getenv("HUGGINGFACE_API_KEY")
            or ""
        )
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.temp_dir = Path(tempfile.gettempdir()) / "agentic_ads_videos"
        self.temp_dir.mkdir(exist_ok=True, parents=True)

        print("🎬 [VideoGIF] Initialized Video GIF Generation Agent")
        print(f"🎬 [VideoGIF] Platform: {context.platform}")
        print(f"🎬 [VideoGIF] Tone: {context.tone}")
        print(f"🎬 [VideoGIF] HF key present: {bool(self.huggingface_api_key)}")
        print(f"🎬 [VideoGIF] Logo provided: {bool(context.logo_data)}")
        print(f"🎬 [VideoGIF] Output directory: {self.temp_dir}")

    async def generate_gif(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a GIF reel and return the updated workflow state."""
        video_script = state.get("video_script", "")
        
        print(f"🎬 [VideoGIF] Received video_script length: {len(video_script)}")
        print(f"🎬 [VideoGIF] Video_script content preview: '{video_script[:100]}...'")
        
        if not video_script or video_script.strip() == "":
            print("⚠️ [VideoGIF] Missing or empty video script. Generating fallback GIF.")
        else:
            print(f"✅ [VideoGIF] Valid video script found, length: {len(video_script)}")

        prompts = self._build_frame_prompts(state.get("video_script", ""))
        print(f"🎬 [VideoGIF] Prepared {len(prompts)} frame prompts")

        try:
            frames = await self._generate_frames(prompts)
            if not frames:
                raise RuntimeError("No frames generated")

            file_path, download_url = await self._save_frames_to_gif(frames)
            return {
                **state,
                "video_gif_url": download_url,
                "video_gif_file_path": str(file_path),
                "video_gif_filename": file_path.name,
                "video_generation_notes": "Video GIF generated successfully",
                "video_error": None,
                "video_frame_prompts": prompts,
            }
        except Exception as exc:
            print(f"❌ [VideoGIF] Failed to generate GIF: {exc}")
            import traceback
            print(traceback.format_exc())

            fallback_frame = self._create_fallback_frame("Video preview unavailable", 0)
            file_path, download_url = await self._save_frames_to_gif([fallback_frame])
            return {
                **state,
                "video_gif_url": download_url,
                "video_gif_file_path": str(file_path),
                "video_gif_filename": file_path.name,
                "video_generation_notes": "Fallback GIF generated due to error",
                "video_error": str(exc),
                "video_frame_prompts": prompts,
            }

    def _build_frame_prompts(self, script: str) -> List[str]:
        """Create Stable Diffusion friendly prompts from the video script."""
        if not script:
            script = self.context.input_text

        sections = []
        current = []
        for line in script.splitlines():
            clean_line = line.strip()
            if not clean_line:
                continue
            if clean_line.upper().startswith("SCENE") and current:
                sections.append(" ".join(current))
                current = [clean_line]
            else:
                current.append(clean_line)
        if current:
            sections.append(" ".join(current))

        if not sections:
            sections = [script]

        enhancers = "cinematic lighting, high detail, vibrant colors, 4k, dynamic angle"
        prompts = []
        for raw in sections[: self.context.frame_count]:
            prompt = (
                f"{raw} | Social media vertical video frame, {self.context.tone} tone, "
                f"{self.context.platform} audience, {enhancers}"
            )
            prompts.append(prompt)

        while len(prompts) < self.context.frame_count:
            prompts.append(
                f"Dynamic shot related to {self.context.input_text}, engaging composition,"
                f" {self.context.tone} mood, {enhancers}"
            )

        return prompts[: self.context.frame_count]

    async def _generate_frames(self, prompts: List[str]) -> List[Image.Image]:
        width, height = self.context.get_dimensions()
        tasks = [self._generate_single_frame(prompt, idx, width, height) for idx, prompt in enumerate(prompts)]
        frames = await asyncio.gather(*tasks)
        return [frame for frame in frames if frame is not None]

    async def _generate_single_frame(self, prompt: str, index: int, width: int, height: int) -> Image.Image:
        print(f"🎬 [VideoGIF] Generating frame {index + 1}")
        if self.huggingface_api_key:
            image = await self._generate_with_huggingface(prompt, width, height)
            if image is not None:
                return self._apply_logo(image)

        print(f"⚠️ [VideoGIF] Using fallback frame for index {index}")
        fallback = self._create_fallback_frame(prompt, index, width=width, height=height)
        return self._apply_logo(fallback)

    async def _generate_with_huggingface(self, prompt: str, width: int, height: int) -> Optional[Image.Image]:
        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.0,
                "width": width,
                "height": height,
                "negative_prompt": "text, watermark, blurry, low quality, distorted, deformed",
            },
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers, timeout=90) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        return Image.open(io.BytesIO(image_bytes))
                    else:
                        error_text = await response.text()
                        print(f"❌ [VideoGIF] HuggingFace error {response.status}: {error_text[:200]}")
        except Exception as exc:
            print(f"❌ [VideoGIF] HuggingFace exception: {exc}")

        return None

    def _create_fallback_frame(self, prompt: str, index: int, width: Optional[int] = None, height: Optional[int] = None) -> Image.Image:
        if width is None or height is None:
            width, height = self.context.get_dimensions()

        background_colors = [
            (78, 205, 196),
            (255, 107, 107),
            (255, 204, 92),
            (147, 196, 125),
            (118, 171, 174),
        ]
        color = background_colors[index % len(background_colors)]
        image = Image.new("RGB", (width, height), color=color)
        draw = ImageDraw.Draw(image)

        message = "AI Video Preview"
        subtext = prompt[:120] + ("..." if len(prompt) > 120 else "")

        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            body_font = ImageFont.truetype("arial.ttf", 28)
        except IOError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

        text_w, text_h = draw.textsize(message, font=title_font)
        draw.text(((width - text_w) / 2, height * 0.25), message, fill=(255, 255, 255), font=title_font)
        draw.multiline_text(
            (width * 0.1, height * 0.45),
            subtext,
            fill=(255, 255, 255),
            font=body_font,
            align="center",
            spacing=8,
        )

        return image

    def _apply_logo(self, frame: Image.Image) -> Image.Image:
        if not self.context.logo_data:
            return frame

        try:
            if frame.mode != "RGBA":
                frame = frame.convert("RGBA")

            logo = Image.open(io.BytesIO(self.context.logo_data))
            if logo.mode != "RGBA":
                logo = logo.convert("RGBA")

            logo_size = self._calculate_logo_size(frame.size)
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            position = self._get_logo_position(frame.size, logo_size, self.context.logo_position)

            padding = 16
            bg_size = (logo_size[0] + padding * 2, logo_size[1] + padding * 2)
            logo_bg = self._create_logo_background(bg_size)

            frame_copy = frame.copy()
            bg_position = (max(position[0] - padding, 0), max(position[1] - padding, 0))
            frame_copy.paste(logo_bg, bg_position, logo_bg)
            frame_copy.paste(logo, (bg_position[0] + padding, bg_position[1] + padding), logo)
            return frame_copy
        except Exception as exc:
            print(f"⚠️ [VideoGIF] Logo application failed: {exc}")
            return frame

    def _calculate_logo_size(self, frame_size: Tuple[int, int]) -> Tuple[int, int]:
        width, height = frame_size
        target_width = min(width // 5, 220)
        target_height = min(height // 8, 180)
        return target_width, target_height

    def _get_logo_position(self, frame_size: Tuple[int, int], logo_size: Tuple[int, int], position: str) -> Tuple[int, int]:
        frame_w, frame_h = frame_size
        logo_w, logo_h = logo_size
        margin = 24
        mapping = {
            "top-left": (margin, margin),
            "top-right": (frame_w - logo_w - margin, margin),
            "bottom-left": (margin, frame_h - logo_h - margin),
            "bottom-right": (frame_w - logo_w - margin, frame_h - logo_h - margin),
            "center": ((frame_w - logo_w) // 2, (frame_h - logo_h) // 2),
        }
        return mapping.get(position, mapping["top-right"])

    def _create_logo_background(self, size: Tuple[int, int]) -> Image.Image:
        bg = Image.new("RGBA", size, (15, 17, 26, 180))
        draw = ImageDraw.Draw(bg)
        draw.rounded_rectangle([(1, 1), (size[0] - 2, size[1] - 2)], radius=16, outline=(255, 255, 255, 200), width=2)
        return bg

    async def _save_frames_to_gif(self, frames: List[Image.Image]) -> Tuple[Path, str]:
        if not frames:
            raise ValueError("No frames to save")

        filename = f"video_{uuid.uuid4().hex[:12]}.gif"
        file_path = self.temp_dir / filename

        first_frame, *additional_frames = frames
        first_frame.save(
            file_path,
            format="GIF",
            save_all=True,
            append_images=additional_frames,
            duration=self.context.frame_duration_ms,
            loop=0,
        )

        download_url = f"/api/videos/download/{filename}"
        print(f"✅ [VideoGIF] GIF saved to {file_path}")
        return file_path, download_url
