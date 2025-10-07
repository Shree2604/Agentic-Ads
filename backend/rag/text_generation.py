"""
Text generation service using Hugging Face Inference API
"""

import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import time

load_dotenv()

class TextGenerationService:
    """Handles text generation using Hugging Face Inference API"""
    
    def __init__(self):
        # Try to get API token
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        if not self.api_token or len(self.api_token.strip()) < 10:
            print("WARNING: HuggingFace API token not set.")
            print("TIP: Get a free token at: https://huggingface.co/settings/tokens")
            print("   Then add to .env: HUGGINGFACE_API_TOKEN=your_token_here")
            self.api_token = None
        
        # Find working model
        self.api_url = None
        self.model_name = None
        
        # Try HuggingFace API first
        if self.api_token:
            working_model = self._find_working_model()
            if working_model:
                self.api_url = f"https://api-inference.huggingface.co/models/{working_model}"
                self.model_name = working_model
                print("SUCCESS: Using HuggingFace model: " + working_model)
            else:
                print("WARNING: No accessible HuggingFace models found.")
        
        # If API doesn't work, try local transformers
        if not self.api_url:
            try:
                from transformers import pipeline
                self.local_generator = pipeline('text-generation', model='gpt2')
                print("SUCCESS: Using local GPT-2 model")
            except ImportError:
                self.local_generator = None
                print("WARNING: Using template-based generation (no AI model active)")

    def _find_working_model(self) -> Optional[str]:
        """Find a working model from the list"""
        models = [
            "gpt2",
            "distilgpt2",
            "gpt2-medium",
            "EleutherAI/gpt-neo-125M",
            "google/flan-t5-small",
            "facebook/opt-125m"
        ]
        for model in models:
            if self._test_model(model):
                return model
        return None

    def _test_model(self, model_name: str) -> bool:
        """Test if a model is available and accessible"""
        if not self.api_token:
            return False
            
        try:
            url = f"https://api-inference.huggingface.co/models/{model_name}"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json={"inputs": "test"}, 
                timeout=8
            )
            
            if response.status_code == 200:
                return True
            elif response.status_code == 503:
                # Model loading - wait briefly and retry once
                time.sleep(3)
                response = requests.post(
                    url, 
                    headers=headers, 
                    json={"inputs": "test"}, 
                    timeout=8
                )
                return response.status_code == 200
            
            return False
            
        except:
            return False

    def generate_ad(self, 
                   context: List[Dict[str, Any]], 
                   platform: str,
                   tone: str,
                   input_text: Optional[str] = None,
                   max_length: int = 150) -> str:
        """Generate ad content using available methods"""
        
        # Try HuggingFace API first
        if self.api_url and self.api_token:
            api_result = self._generate_with_api(context, platform, tone, input_text, max_length)
            if api_result:
                return api_result
        
        # Try local transformers
        if self.local_generator:
            local_result = self._generate_with_local(context, platform, tone, input_text, max_length)
            if local_result:
                return local_result
        
        # Fallback to template-based generation
        return self._generate_fallback_response(platform, tone, input_text)

    def _generate_with_api(self, context, platform, tone, input_text, max_length):
        """Generate using HuggingFace API"""
        try:
            prompt = self._construct_prompt(context, platform, tone, input_text)
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
            }
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": min(max_length, 100),
                    "temperature": 0.8,
                    "top_p": 0.92,
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=25)
            
            if response.status_code == 200:
                result = response.json()
                
                generated_text = ""
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    generated_text = result.get('generated_text', '')
                
                if generated_text:
                    cleaned = self._clean_generated_text(generated_text, prompt)
                    if len(cleaned.strip()) >= 20:
                        return cleaned
            
        except Exception as e:
            print(f"API generation error: {str(e)[:100]}")
        
        return None

    def _generate_with_local(self, context, platform, tone, input_text, max_length):
        """Generate using local transformers"""
        try:
            prompt = self._construct_prompt(context, platform, tone, input_text)
            
            # Truncate prompt if too long
            if len(prompt) > 200:
                prompt = prompt[:200] + "..."
            
            result = self.local_generator(
                prompt,
                max_length=min(len(prompt) + 50, 150),
                temperature=0.8,
                do_sample=True,
                num_return_sequences=1
            )
            
            if result and len(result) > 0:
                generated_text = result[0]['generated_text']
                cleaned = self._clean_generated_text(generated_text, prompt)
                if len(cleaned.strip()) >= 20:
                    return cleaned
                    
        except Exception as e:
            print(f"Local generation error: {str(e)[:100]}")
        
        return None

    def _construct_prompt(self, 
                         context: List[Dict[str, Any]], 
                         platform: str,
                         tone: str,
                         input_text: Optional[str] = None) -> str:
        """Construct simple, effective prompt"""
        
        # Simple prompt that works well with GPT-2 style models
        prompt = f"Write a {tone} advertisement for {platform}.\n\n"
        
        if input_text:
            prompt += f"Topic: {input_text}\n\n"
        
        # Add one good example if available
        if context and len(context) > 0:
            best_example = context[0]['content']
            # Truncate if too long
            if len(best_example) > 200:
                best_example = best_example[:200] + "..."
            prompt += f"Example style: {best_example}\n\n"
        
        prompt += f"New {tone} {platform} ad:"
        
        return prompt

    def _clean_generated_text(self, generated_text: str, prompt: str) -> str:
        """Clean up the generated text"""
        
        text = generated_text.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Advertisement:", "Ad:", "Here's", "Here is", "Sure,", 
            "Certainly", "Of course", "Let me", "I'll", "I will",
            "New", "Sample:", "Example:", "Post:"
        ]
        
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                text = text.lstrip(':,.-').strip()
        
        # Split into sentences and take only complete ones
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            text = ' '.join(lines[:3])  # Max 3 lines
        
        # Remove incomplete sentences at the end
        if text and not text[-1] in '.!?':
            # Find last complete sentence
            for delimiter in ['. ', '! ', '? ']:
                if delimiter in text:
                    text = text.rsplit(delimiter, 1)[0] + delimiter.strip()
                    break
        
        # Limit total length
        if len(text) > 400:
            text = text[:400].rsplit(' ', 1)[0].rsplit('.', 1)[0] + '.'
        
        # Remove any repeated phrases (common in generated text)
        words = text.split()
        if len(words) > 10:
            # Check for repetitions
            for i in range(len(words) - 5):
                chunk = ' '.join(words[i:i+3])
                rest = ' '.join(words[i+3:])
                if chunk in rest:
                    # Found repetition, cut it off
                    text = ' '.join(words[:i+3])
                    break
        
        return text.strip()

    def _generate_fallback_response(self, platform: str, tone: str, input_text: Optional[str] = None) -> str:
        """Generate smart template-based response"""
        
        content = input_text or "something amazing"
        
        # Platform-specific templates
        templates = {
            "instagram": {
                "professional": f"✨ Discover {content}. Excellence in every detail. #InstaGood #Quality #Professional",
                "casual": f"Hey! 👋 Check out {content}! You're gonna love this! #InstaDaily #MustSee #Trending",
                "energetic": f"🚀 WOW! {content} is HERE! Get ready to be amazed! 💥 #Viral #Trending #Amazing",
                "fun": f"🎉 Fun time! {content} is waiting for you! Let's go! 🌟 #Fun #Happy #GoodVibes",
                "witty": f"Plot twist: {content} is actually genius. 🧠✨ #Clever #SmartChoice #ThinkAboutIt",
            },
            "facebook": {
                "professional": f"Introducing {content} - designed for professionals who demand excellence. Learn more! 💼 #Business #Professional",
                "casual": f"Hey friends! 👋 Just discovered {content} and had to share! What do you think? 💭 #Community #Share",
                "energetic": f"🔥 ATTENTION EVERYONE! {content} is absolutely incredible! Don't miss this! 🎯 #Viral #MustSee",
                "fun": f"🎈 Having fun yet? Because {content} is about to make your day! 😊 #Fun #Happy #Smile",
                "witty": f"Breaking: Local area discovers {content}, productivity drops to zero. 😏 #Funny #Relatable",
            },
            "twitter": {
                "professional": f"Elevate your game with {content}. Excellence delivered. 💼 #Professional #Quality #Success",
                "casual": f"ngl {content} hits different 👀 check it out #Trending",
                "energetic": f"🚀 YOOO {content} IS INSANE!! 🔥🔥 #Viral #Trending #OMG",
                "fun": f"✨ {content} = instant happiness ✨ you're welcome 😊 #Fun #Happy",
                "witty": f"me: need {content}\nalso me: *gets {content}*\nme: 🤯 #Relatable",
            },
            "linkedin": {
                "professional": f"Transform your business with {content}. Proven results, exceptional value. #Business #Innovation #Growth",
                "casual": f"Excited to share {content} with my network. This could be valuable for your team! #Professional #Networking",
                "energetic": f"🎯 Game-changer alert! {content} is revolutionizing the industry! #Innovation #Disruption #Future",
                "fun": f"Work doesn't have to be boring! {content} proves it. 🌟 #WorkLife #Innovation #Team",
                "witty": f"Everyone: impossible\n{content}: hold my coffee ☕ #Innovation #Disruption",
            },
            "youtube": {
                "professional": f"🎬 New video: Exploring {content}. Professional insights you need. SUBSCRIBE! #YouTube #Educational",
                "casual": f"📹 Hey guys! New video about {content}! Link in description! 👇 #YouTube #NewVideo",
                "energetic": f"🔥 WHAT'S UP EVERYBODY! Today's video: {content} - IT'S EPIC! 🎮 SMASH SUBSCRIBE! #YouTube #Viral",
                "fun": f"🎥 Fun new video alert! {content} is hilarious! 😂 Watch now! #YouTube #Fun #Entertainment",
                "witty": f"📺 Made a video about {content}. It's either genius or I need sleep. Probably both. #YouTube #Content",
            }
        }
        
        # Get template for platform and tone
        platform_templates = templates.get(platform.lower(), templates["instagram"])
        template = platform_templates.get(tone.lower(), platform_templates["casual"])
        
        return template

# Global instance
text_generator = None

def get_text_generator() -> TextGenerationService:
    """Get or create global text generator instance"""
    global text_generator
    if text_generator is None:
        text_generator = TextGenerationService()
    return text_generator