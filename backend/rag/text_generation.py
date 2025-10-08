"""
Text generation service using Google Gemini 1.5 Flash
"""

import os
import warnings
import logging

# MUST be set BEFORE importing google.generativeai
os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)
logging.getLogger('absl').setLevel(logging.ERROR)

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import random

class TextGenerationService:
    """Handles text generation using Google Gemini 1.5 Flash"""
    
    def __init__(self, api_key: Optional[str] = None):
        print("🔍 Initializing Gemini 1.5 Flash text generation...")
        
        self.model = None
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # FIXED: Use 'gemini-1.5-flash-latest' or 'gemini-1.5-flash-001' for stable API
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                print("✅ SUCCESS: Gemini 1.5 Flash initialized!\n")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {str(e)[:100]}")
                print("ℹ️  Falling back to template-based generation\n")
        else:
            print("⚠️  No API key provided (set GOOGLE_API_KEY environment variable)")
            print("ℹ️  Using smart template-based generation\n")

    def generate_ad(self, 
                   context: List[Dict[str, Any]], 
                   platform: str,
                   tone: str,
                   input_text: Optional[str] = None,
                   max_length: int = 150) -> str:
        """Generate ad content"""
        
        # Try Gemini first
        if self.model:
            result = self._generate_with_gemini(context, platform, tone, input_text, max_length)
            if result:
                return result
        
        # Smart template fallback
        return self._generate_smart_template(platform, tone, input_text, context)

    async def _generate_with_gemini_async(self, context, platform, tone, input_text, max_length):
        """Async wrapper for Gemini generation"""
        return self._generate_with_gemini(context, platform, tone, input_text, max_length)
    
    def _generate_with_gemini(self, context, platform, tone, input_text, max_length):
        """Generate using Gemini 1.5 Flash"""
        try:
            prompt = self._construct_gemini_prompt(platform, tone, input_text, context, max_length)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=0.9,
                top_p=0.95,
                top_k=40,
                max_output_tokens=200,
            )
            
            # Add safety settings to reduce content filtering
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response has valid parts before accessing text
            if response and response.parts:
                try:
                    text_content = response.text
                    cleaned = self._clean_text(text_content)
                    if len(cleaned) > 20:
                        return cleaned
                except ValueError:
                    # Response was blocked or has no valid text
                    print("⚠️  Response blocked by safety filters or empty")
                    if hasattr(response, 'prompt_feedback'):
                        print(f"   Feedback: {response.prompt_feedback}")
            elif response:
                # Check if blocked
                if hasattr(response, 'prompt_feedback'):
                    print(f"⚠️  Content blocked: {response.prompt_feedback}")
                else:
                    print("⚠️  No valid response parts returned")
            
        except ValueError as e:
            error_msg = str(e)
            if "response.text" in error_msg or "valid `Part`" in error_msg:
                print(f"⚠️  Response structure issue - content may be blocked")
            else:
                print(f"Gemini value error: {error_msg[:100]}")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                print(f"⚠️  Model not found. Try using 'gemini-1.5-flash-001' or 'gemini-pro'")
            else:
                print(f"Gemini generation failed: {error_msg[:100]}")
        
        return None

    def _construct_gemini_prompt(self, platform: str, tone: str, input_text: Optional[str], 
                                 context: List[Dict[str, Any]], max_length: int) -> str:
        """Construct detailed prompt for Gemini"""
        
        topic = input_text or "an amazing product"
        
        # Analyze context for style guidance
        context_examples = ""
        if context and len(context) > 0:
            samples = [item.get('content', '') for item in context[:2]]
            if samples:
                context_examples = "\n\nExample style from previous posts:\n" + "\n".join(f"- {s[:100]}" for s in samples if s)
        
        # Platform-specific guidelines
        platform_guides = {
            "instagram": "Use emojis, hashtags, and engaging visual language. 2-3 sentences max.",
            "facebook": "Conversational and community-focused. 2-4 sentences. May include emojis.",
            "twitter": "Concise and punchy. Max 2-3 sentences. Use relevant hashtags.",
            "linkedin": "Professional yet approachable. 2-4 sentences. Focus on value and insights.",
            "youtube": "Enthusiastic and engaging. Include call-to-action. 2-3 sentences with emojis."
        }
        
        platform_guide = platform_guides.get(platform.lower(), platform_guides["instagram"])
        
        prompt = f"""Create a {tone} social media post for {platform} about: {topic}

Guidelines:
- Platform: {platform} - {platform_guide}
- Tone: {tone} (be authentic and match this tone naturally)
- Length: Keep it concise, around {max_length} characters or less
- Make it engaging and platform-appropriate
- Don't include meta-commentary or explanations
- Output ONLY the post content, nothing else{context_examples}

Write the post now:"""
        
        return prompt

    def _clean_text(self, text: str) -> str:
        """Clean generated text"""
        
        text = text.strip()
        
        # Remove common prefixes and meta-commentary
        bad_starts = [
            "Advertisement:", "Ad:", "Post:", "Caption:", "Here's", "Sure", "Okay", 
            "Alright", "Sample:", "Example:", "Text:", "Here is", "This is",
            "I've created", "I've written", "Here you go", "Check out"
        ]
        
        for prefix in bad_starts:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].lstrip(':,.- ').strip()
        
        # Remove quotes if the entire text is wrapped in them
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()
        
        # Remove any trailing meta-commentary
        bad_endings = [
            "Let me know if",
            "Would you like",
            "Feel free to",
            "I hope this",
            "Does this work"
        ]
        
        for ending in bad_endings:
            if ending.lower() in text.lower():
                text = text[:text.lower().find(ending.lower())].strip()
        
        # Ensure proper ending punctuation
        if text and text[-1] not in '.!?':
            if len(text.split()) > 5:
                text += '.'
        
        # Limit length
        if len(text) > 350:
            text = text[:350].rsplit(' ', 1)[0]
            if not text.endswith(('.', '!', '?')):
                text += '.'
        
        return text

    def _generate_smart_template(self, platform: str, tone: str, input_text: Optional[str], 
                                 context: List[Dict[str, Any]]) -> str:
        """Generate smart template-based content as fallback"""
        
        topic = input_text or "something amazing"
        
        # Analyze context for better templates
        uses_emojis = False
        uses_hashtags = False
        if context and len(context) > 0:
            sample = context[0].get('content', '')
            uses_emojis = any(char for char in sample if ord(char) > 127)
            uses_hashtags = '#' in sample
        
        # Platform-specific templates with variations
        templates = {
            "instagram": {
                "professional": [
                    f"Discover {topic}. Excellence redefined. #Quality #Professional",
                    f"✨ Introducing {topic}. Where quality meets innovation. #Excellence",
                    f"Elevate your experience with {topic}. Premium quality guaranteed. #InstaGood"
                ],
                "casual": [
                    f"Hey! 👋 You need to see {topic}! Trust me on this one 😊 #InstaDaily",
                    f"Just found {topic} and I'm obsessed! 🙌 Check it out! #MustSee",
                    f"Okay but {topic} is actually perfect? 💯 You're welcome! #Trending"
                ],
                "energetic": [
                    f"🚀 OMG! {topic} is INCREDIBLE! This is what we've been waiting for! 💥 #Viral",
                    f"🔥 STOP SCROLLING! {topic} is absolutely INSANE! 😱 #Amazing #Trending",
                    f"💥 BOOM! {topic} just dropped and it's EVERYTHING! Let's GO! 🎉 #Epic"
                ],
                "fun": [
                    f"🎉 Party time! {topic} is here and it's SO much fun! 🥳 #GoodVibes",
                    f"Smile! 😊 Because {topic} exists and it's AWESOME! ✨ #Happy #Fun",
                    f"🌈 Bringing you {topic} and all the happy vibes! ☀️ #JoyfulMoments"
                ],
                "witty": [
                    f"Me: I don't need {topic}\nAlso me: *gets {topic}* 🤯 #Relatable",
                    f"Breaking: Local person discovers {topic}, productivity drops 99% 📉 #Worth",
                    f"Plot twist: {topic} is actually genius. Who knew? 🧠 #Clever"
                ]
            },
            "facebook": {
                "professional": [
                    f"Introducing {topic} - where innovation meets excellence. Learn more today! 💼",
                    f"Experience {topic}. Professional quality, exceptional results. Discover more!",
                    f"Transform your approach with {topic}. Excellence delivered. 🎯"
                ],
                "casual": [
                    f"Hey friends! 👋 Just discovered {topic} and had to share with you all! Thoughts? 💭",
                    f"Anyone else tried {topic} yet? It's really good! Let me know what you think! 😊",
                    f"Sharing this because {topic} is actually amazing! Check it out! 🌟"
                ],
                "energetic": [
                    f"🔥 EVERYONE! You NEED to see {topic}! This is HUGE! Share this! 🎯",
                    f"⚡ ATTENTION! {topic} is absolutely INCREDIBLE! Don't miss out! 💥",
                    f"🚀 WOW WOW WOW! {topic} is BLOWING MY MIND! Tag someone! 🤯"
                ],
                "fun": [
                    f"🎈 Happy news! {topic} is here to make your day brighter! 😄 Who's ready?",
                    f"🎉 Fun alert! {topic} is exactly what we needed! Join the fun! 🥳",
                    f"☀️ Spreading joy with {topic}! Life just got more fun! 😊"
                ],
                "witty": [
                    f"Therapist: And what's making you happy?\nMe: {topic} 😏 #Priorities",
                    f"Update: {topic} exists, everything else is irrelevant. That's the post. 🎯",
                    f"Science: Impossible\n{topic}: Hold my coffee ☕ *does it anyway*"
                ]
            },
            "twitter": {
                "professional": [
                    f"Elevate your standards with {topic}. Excellence delivered. 💼 #Quality",
                    f"{topic}: Where professionalism meets innovation. #Business #Success",
                    f"Transform your game with {topic}. Results that matter. 🎯"
                ],
                "casual": [
                    f"just discovered {topic} and yeah it's pretty great ngl 👀",
                    f"okay so {topic} is actually really good? who knew 🤷‍♂️",
                    f"{topic} hits different tbh 💯 highly recommend"
                ],
                "energetic": [
                    f"🚀 YOOO {topic} IS INSANE!! 🔥🔥 RT IF YOU AGREE",
                    f"⚡ {topic} JUST BROKE THE INTERNET 💥 THIS IS NOT A DRILL",
                    f"🔥 EVERYONE STOP!! {topic} IS HERE AND IT'S WILD 🤯"
                ],
                "fun": [
                    f"✨ {topic} = pure happiness ✨ you're welcome 😊",
                    f"🎉 life hack: get {topic}, be happy 🥳 simple!",
                    f"🌈 {topic} making everything better since [today] ☀️"
                ],
                "witty": [
                    f"me: don't need it\n*sees {topic}*\nme: NEED IT 🛒",
                    f"{topic} really said 'i'm about to change everything' and did 💯",
                    f"therapist: what made you smile?\nme: {topic}\ntherapist: understandable 😌"
                ]
            },
            "linkedin": {
                "professional": [
                    f"Excited to introduce {topic} - driving innovation and results. #Leadership #Growth",
                    f"Transform your business with {topic}. Proven excellence. #Innovation #Success",
                    f"Discover {topic}: Where strategy meets execution. #Business #Professional"
                ],
                "casual": [
                    f"Wanted to share {topic} with my network. Could be valuable for your team! 💡",
                    f"Recently discovered {topic} - thought it might interest my connections! #Networking",
                    f"Quick share: {topic} has been really helpful. Worth checking out! 🎯"
                ],
                "energetic": [
                    f"🎯 Game-changer alert! {topic} is revolutionizing the industry! #Innovation #Disruption",
                    f"🚀 HUGE NEWS! {topic} is transforming how we work! Don't miss this! #Future",
                    f"⚡ Industry breakthrough! {topic} is changing everything! #Innovation"
                ],
                "fun": [
                    f"Who says work can't be fun? {topic} proves otherwise! 🌟 #WorkLife #Innovation",
                    f"Making work better with {topic}! 😊 #TeamSuccess #Positive",
                    f"Bringing positive energy with {topic}! Work smarter, not harder! ✨"
                ],
                "witty": [
                    f"Everyone: It can't be done\n{topic}: Challenge accepted ✅ #Innovation",
                    f"Conventional wisdom: Follow the rules\n{topic}: *rewrites the rules* 📝",
                    f"Status quo: We've always done it this way\n{topic}: Not anymore 🎯"
                ]
            },
            "youtube": {
                "professional": [
                    f"🎬 NEW VIDEO: In-depth look at {topic}. Professional insights. SUBSCRIBE for more! #Educational",
                    f"📺 Latest upload: Everything you need to know about {topic}. Quality content! #YouTube",
                    f"🎥 New: Comprehensive guide to {topic}. Expert analysis. Hit that subscribe! #Tutorial"
                ],
                "casual": [
                    f"📹 Hey everyone! New video about {topic}! Link in description 👇 #YouTuber",
                    f"🎬 What's up! Just posted about {topic}! Go check it out! 😊 #NewVideo",
                    f"📺 New vid is up! All about {topic}! Let me know what you think! #Content"
                ],
                "energetic": [
                    f"🔥 WHAT'S UP FAM! NEW VIDEO: {topic} - IT'S INSANE! SMASH LIKE & SUBSCRIBE! 💥",
                    f"⚡ YO GUYS! {topic} VIDEO IS LIVE! THIS ONE'S CRAZY! GO WATCH NOW! 🚀",
                    f"💥 NEW VIDEO ALERT! {topic} - YOU'RE NOT READY FOR THIS! SUBSCRIBE! 🔥"
                ],
                "fun": [
                    f"🎉 Fun new video! All about {topic}! It's hilarious! 😂 Watch now! #Entertainment",
                    f"🥳 Happy video time! {topic} edition! You'll love this! 🌟 #Fun #YouTube",
                    f"😄 Made a fun video about {topic}! Good vibes only! Check it out! ☀️"
                ],
                "witty": [
                    f"📺 Made a video about {topic}. It's either genius or I need sleep. Probably both. 😴",
                    f"🎬 New video: {topic} explained. Warning: may contain dad jokes. You've been warned. 😏",
                    f"📹 {topic} video is up! Spent 10 hours editing, 30 seconds watching. Worth it? 🤔"
                ]
            }
        }
        
        # Get platform templates
        platform_key = platform.lower()
        if platform_key not in templates:
            platform_key = "instagram"
        
        platform_templates = templates[platform_key]
        
        # Get tone templates
        tone_key = tone.lower()
        if tone_key not in platform_templates:
            tone_key = "casual"
        
        tone_templates = platform_templates[tone_key]
        
        # Pick random variation for variety
        return random.choice(tone_templates)


# Global instance
text_generator = None

def get_text_generator(api_key: Optional[str] = None) -> TextGenerationService:
    """Get or create global text generator instance"""
    global text_generator
    if text_generator is None:
        text_generator = TextGenerationService(api_key=api_key)
    return text_generator