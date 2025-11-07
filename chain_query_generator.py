import re
from typing import List, Optional, Dict
from lm_studio_client import LMStudioClient
from logger_config import logger_config

class ChainQueryGenerator:
    def __init__(self):
        self.lm_client = LMStudioClient()
        self.follow_up_templates = {
            "general": [
                "Would you like to dive deeper into this topic?",
                "Do you want to know more about this?",
                "Should I tell you more about this?",
                "Would you like to explore this further?",
                "Are you interested in learning more about this?"
            ],
            "technical": [
                "Would you like me to explain this in more detail?",
                "Do you want to see some examples of this?",
                "Should I break this down into simpler terms?",
                "Would you like to know how this works in practice?",
                "Do you want to explore the technical aspects further?"
            ],
            "practical": [
                "Would you like to see how to apply this?",
                "Do you want some practical examples?",
                "Should I show you how this works in real life?",
                "Would you like to try this yourself?",
                "Do you want to see some use cases?"
            ],
            "comparative": [
                "Would you like to compare this with other options?",
                "Do you want to know the differences between these approaches?",
                "Should I explain the pros and cons?",
                "Would you like to see alternatives?",
                "Do you want to understand the trade-offs?"
            ]
        }

    async def generate_follow_up_questions(self, user_message: str, ai_response: str, intent: str) -> List[str]:
        """
        Generate relevant follow-up questions based on the user's message, AI's response, and intent.
        """
        try:
            # Analyze the response to determine the best follow-up approach
            response_analysis = await self._analyze_response(ai_response, intent)
            
            # Generate follow-up questions based on the analysis
            follow_ups = await self._generate_questions(user_message, ai_response, response_analysis)
            
            logger_config.log_debug(f"Generated {len(follow_ups)} follow-up questions for intent: {intent}")
            return follow_ups
            
        except Exception as e:
            logger_config.log_error(f"Error generating follow-up questions: {str(e)}", exception=e)
            return self._get_fallback_questions(intent)

    async def append_best_follow_up_to_response(self, user_message: str, ai_response: str, intent: str) -> str:
        """
        Generate follow-up questions and append the best one directly to the AI response.
        """
        try:
            # Generate follow-up questions
            follow_ups = await self.generate_follow_up_questions(user_message, ai_response, intent)
            
            if not follow_ups:
                return ai_response
            
            # Select the best follow-up question (first one is usually the most relevant)
            best_follow_up = follow_ups[0].strip('"')  # Remove quotes if present
            
            # Append the follow-up question to the response
            enhanced_response = f"{ai_response}\n\n{best_follow_up}"
            
            logger_config.log_debug(f"Appended follow-up question to response: {best_follow_up[:50]}...")
            return enhanced_response
            
        except Exception as e:
            logger_config.log_error(f"Error appending follow-up question: {str(e)}", exception=e)
            return ai_response

    async def _analyze_response(self, ai_response: str, intent: str) -> Dict[str, any]:
        """Analyze the AI response to determine the best follow-up strategy."""
        prompt = f"""Analyze this AI response and determine the best follow-up approach:

AI Response: "{ai_response[:500]}"
User Intent: {intent}

Determine:
1. Response type: technical, practical, general, comparative, or educational
2. Main topics mentioned (list 2-3 key topics)
3. Complexity level: simple, moderate, or complex
4. Whether it's a complete answer or needs more detail
5. What aspects could be explored further

Respond in this format:
Type: [response_type]
Topics: [topic1, topic2, topic3]
Complexity: [complexity_level]
Completeness: [complete/partial/overview]
Exploration: [what can be explored further]
"""
        
        try:
            response = await self.lm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            # Parse the response
            analysis = self._parse_analysis(response)
            logger_config.log_debug(f"Response analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger_config.log_warning(f"Failed to analyze response: {e}")
            return {
                "type": "general",
                "topics": ["general information"],
                "complexity": "moderate",
                "completeness": "complete",
                "exploration": "general aspects"
            }

    def _parse_analysis(self, response: str) -> Dict[str, any]:
        """Parse the analysis response from the AI."""
        analysis = {
            "type": "general",
            "topics": ["general information"],
            "complexity": "moderate",
            "completeness": "complete",
            "exploration": "general aspects"
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith('Type:'):
                analysis["type"] = line.split(':', 1)[1].strip().lower()
            elif line.startswith('Topics:'):
                topics = line.split(':', 1)[1].strip()
                analysis["topics"] = [t.strip() for t in topics.split(',')]
            elif line.startswith('Complexity:'):
                analysis["complexity"] = line.split(':', 1)[1].strip().lower()
            elif line.startswith('Completeness:'):
                analysis["completeness"] = line.split(':', 1)[1].strip().lower()
            elif line.startswith('Exploration:'):
                analysis["exploration"] = line.split(':', 1)[1].strip()
        
        return analysis

    async def _generate_questions(self, user_message: str, ai_response: str, analysis: Dict[str, any]) -> List[str]:
        """Generate specific follow-up questions based on the analysis."""
        response_type = analysis.get("type", "general")
        topics = analysis.get("topics", ["general information"])
        complexity = analysis.get("complexity", "moderate")
        
        # Create a focused prompt for question generation
        prompt = f"""Based on this conversation, generate 2-3 engaging follow-up questions:

User asked: "{user_message[:200]}"
AI responded about: {', '.join(topics[:3])}
Response type: {response_type}
Complexity: {complexity}

Generate follow-up questions that:
1. Are natural and conversational
2. Encourage deeper exploration
3. Match the user's interest level
4. Are specific to the topics discussed
5. Use varied question formats (would you like, do you want, should I, etc.)

Examples of good follow-up questions:
- "Would you like to dive deeper into [specific topic]?"
- "Do you want to know more about [specific aspect]?"
- "Should I explain [related concept] in more detail?"
- "Would you like to see some examples of [topic]?"
- "Do you want to explore [specific area] further?"

Generate 2-3 questions, one per line, without numbering or bullet points.
"""
        
        try:
            response = await self.lm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            # Parse questions from response
            questions = self._parse_questions(response)
            logger_config.log_debug(f"Generated questions: {questions}")
            return questions
            
        except Exception as e:
            logger_config.log_warning(f"Failed to generate questions: {e}")
            return self._get_fallback_questions(response_type)

    def _parse_questions(self, response: str) -> List[str]:
        """Parse questions from the AI response."""
        questions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or line.endswith('?')):
                # Clean up the question
                question = line.strip('•-*123456789. ')
                if question and len(question) > 10:  # Filter out very short responses
                    questions.append(question)
        
        # If no questions found, try to extract from the text
        if not questions:
            sentences = response.split('.')
            for sentence in sentences:
                if '?' in sentence:
                    question = sentence.strip()
                    if len(question) > 10:
                        questions.append(question)
        
        return questions[:3]  # Return max 3 questions

    def _get_fallback_questions(self, intent: str) -> List[str]:
        """Get fallback questions based on intent."""
        if intent == "query":
            return [
                "Would you like to know more about this?",
                "Do you want me to explain this in more detail?",
                "Should I tell you more about this topic?"
            ]
        elif intent == "information":
            return [
                "Would you like to explore this further?",
                "Do you want to know more about this?",
                "Should I dive deeper into this topic?"
            ]
        else:
            return [
                "Would you like to know more about this?",
                "Do you want to explore this further?",
                "Should I tell you more about this?"
            ]

    def should_generate_follow_up(self, intent: str, response_length: int) -> bool:
        """Determine if follow-up questions should be generated."""
        # Don't generate for greetings or very short responses
        if intent == "greetings" or response_length < 50:
            return False
        
        # Generate for queries, information, and feedback
        return intent in ["query", "information", "feedback"]

# Create a global instance
chain_query_generator = ChainQueryGenerator()
