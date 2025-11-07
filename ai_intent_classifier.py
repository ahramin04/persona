import json
import re
from typing import Dict, Tuple, List
from datetime import datetime
import asyncio

from lm_studio_client import LMStudioClient

class AIIntentClassifier:
    def __init__(self):
        self.lm_client = LMStudioClient()
        
        # Define intent categories with detailed descriptions
        self.intent_categories = {
            "greetings": {
                "description": "Messages that are greetings, salutations, or ways to start a conversation",
                "examples": [
                    "Hello", "Hi there", "Good morning", "Hey", "How are you?", 
                    "What's up?", "Nice to meet you", "Good day", "Greetings",
                    "Howdy", "Sup", "Yo", "Good evening", "Good afternoon"
                ]
            },
            "query": {
                "description": "Messages that ask questions, seek information, or request help",
                "examples": [
                    "What is...", "How do I...", "Can you help me...", "Explain...",
                    "Tell me about...", "I need help with...", "How does... work?",
                    "What do you think about...", "Can you explain...", "I'm wondering...",
                    "Do you know...", "Could you tell me...", "I want to know..."
                ]
            },
            "information": {
                "description": "Messages that provide information, share knowledge, or make statements",
                "examples": [
                    "I want to tell you...", "Here's what I know...", "Let me share...",
                    "I think that...", "In my opinion...", "I believe...", "I feel...",
                    "This is...", "That's interesting because...", "I found out that...",
                    "I learned that...", "I discovered...", "I know that..."
                ]
            },
            "feedback": {
                "description": "Messages that give feedback, express opinions, thanks, or reactions",
                "examples": [
                    "Thank you", "That's helpful", "I like this", "Great job",
                    "That's awesome", "I love it", "This is terrible", "I hate this",
                    "That's wrong", "I disagree", "I agree", "That's correct",
                    "This is confusing", "I don't understand", "That makes sense",
                    "Thanks a lot", "Much appreciated", "That's amazing", "This sucks"
                ]
            }
        }
        
        # Create the classification prompt
        self.classification_prompt = self._create_classification_prompt()
    
    def _create_classification_prompt(self) -> str:
        """Create a comprehensive prompt for intent classification"""
        prompt = """You are an expert at classifying user messages into intent categories. 

INTENT CATEGORIES:
"""
        
        for intent, info in self.intent_categories.items():
            prompt += f"""
{intent.upper()}:
- Description: {info['description']}
- Examples: {', '.join(info['examples'][:5])}...
"""
        
        prompt += """

TASK:
Classify the given user message into ONE of the four intent categories above.

RULES:
1. Choose the MOST APPROPRIATE category based on the message's primary purpose
2. Consider the context and underlying meaning, not just keywords
3. If a message could fit multiple categories, choose the most dominant one
4. Be flexible with language variations, slang, and informal expressions
5. Consider the user's intent, not just the literal words

RESPONSE FORMAT:
Respond with ONLY a JSON object in this exact format:
{
    "intent": "category_name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this category was chosen"
}

EXAMPLES:
Message: "Hi there!"
Response: {"intent": "greetings", "confidence": 0.98, "reasoning": "Direct greeting"}

Message: "What's the weather like?"
Response: {"intent": "query", "confidence": 0.95, "reasoning": "Asking for information"}

Message: "I think this is a great idea"
Response: {"intent": "information", "confidence": 0.90, "reasoning": "Sharing an opinion"}

Message: "Thanks for your help!"
Response: {"intent": "feedback", "confidence": 0.95, "reasoning": "Expressing gratitude"}

Now classify this message:"""
        
        return prompt
    
    async def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify the intent of a user message using AI.
        
        Args:
            message: The user's message text
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        if not message or not message.strip():
            return 'query', 0.1
        
        try:
            # Prepare the full prompt
            full_prompt = f"{self.classification_prompt}\n\nMessage: \"{message}\"\n\nResponse:"
            
            # Send to LM Studio
            response = await self.lm_client.chat_completion(
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=200
            )
            
            # Parse the response
            intent_result = self._parse_ai_response(response)
            
            if intent_result:
                return intent_result['intent'], intent_result['confidence']
            else:
                # Fallback to default if parsing fails
                return 'query', 0.5
                
        except Exception as e:
            print(f"Error in AI intent classification: {e}")
            # Fallback to query if AI fails
            return 'query', 0.3
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse the AI response and extract intent information"""
        try:
            # Clean the response
            response = response.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]*"intent"[^}]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Validate the result
                if (isinstance(result, dict) and 
                    'intent' in result and 
                    result['intent'] in self.intent_categories and
                    'confidence' in result and
                    isinstance(result['confidence'], (int, float))):
                    
                    # Ensure confidence is between 0 and 1
                    confidence = max(0.0, min(1.0, float(result['confidence'])))
                    result['confidence'] = confidence
                    
                    return result
            
            # If no valid JSON found, try to extract intent from text
            return self._extract_intent_from_text(response)
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return None
    
    def _extract_intent_from_text(self, response: str) -> Dict:
        """Extract intent from non-JSON response"""
        response_lower = response.lower()
        
        # Look for intent keywords in the response
        for intent in self.intent_categories.keys():
            if intent in response_lower:
                # Try to extract confidence if mentioned
                confidence_match = re.search(r'(\d+\.?\d*)', response)
                confidence = 0.8  # Default confidence
                if confidence_match:
                    try:
                        conf_val = float(confidence_match.group(1))
                        if conf_val > 1:
                            confidence = conf_val / 100
                        else:
                            confidence = conf_val
                    except:
                        pass
                
                return {
                    'intent': intent,
                    'confidence': confidence,
                    'reasoning': 'Extracted from text response'
                }
        
        return None
    
    def get_intent_description(self, intent: str) -> str:
        """Get a human-readable description of the intent"""
        return self.intent_categories.get(intent, {}).get('description', 'Unknown intent')
    
    def analyze_message_complexity(self, message: str) -> str:
        """Analyze the complexity of the message"""
        word_count = len(message.split())
        char_count = len(message)
        
        if word_count <= 3:
            return 'simple'
        elif word_count <= 10:
            return 'moderate'
        else:
            return 'complex'
    
    def extract_keywords(self, message: str) -> List[str]:
        """Extract potential keywords from the message"""
        # Simple keyword extraction (can be enhanced with NLP libraries)
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]  # Return top 10 keywords
    
    def get_pattern_matches(self, message: str) -> Dict[str, List[str]]:
        """Get pattern matches for detailed analysis (simplified for AI approach)"""
        return {
            'greetings': ['AI-based classification'],
            'query': ['AI-based classification'],
            'information': ['AI-based classification'],
            'feedback': ['AI-based classification']
        }

# Global AI intent classifier instance
ai_intent_classifier = AIIntentClassifier()
