import re
from typing import Dict, Tuple, List
from datetime import datetime

class IntentClassifier:
    def __init__(self):
        # Define patterns for different intents
        self.greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening|greetings)\b',
            r'\b(how are you|how do you do|what\'s up|sup)\b',
            r'\b(nice to meet you|pleased to meet you)\b',
            r'\b(good day|good night)\b',
            r'^[!]*[hH][eE][lL][lL][oO][!]*$',
            r'^[!]*[hH][iI][!]*$',
            r'^[!]*[hH][eE][yY][!]*$'
        ]
        
        self.query_patterns = [
            r'\b(what|how|why|when|where|who|which|can you|could you|would you)\b',
            r'\b(explain|describe|tell me|show me|help me)\b',
            r'\b(how to|how do|how can|how does)\b',
            r'\b(what is|what are|what does|what do)\b',
            r'\b(why is|why are|why does|why do)\b',
            r'\b(when is|when are|when does|when do)\b',
            r'\b(where is|where are|where does|where do)\b',
            r'\b(who is|who are|who does|who do)\b',
            r'\b(which is|which are|which does|which do)\b',
            r'\b(can you|could you|would you|will you)\b',
            r'\b(please|help|assist|support)\b'
        ]
        
        self.information_patterns = [
            r'\b(here is|here are|let me tell you|i want to tell you)\b',
            r'\b(i have|i know|i think|i believe|i feel)\b',
            r'\b(in my opinion|according to|based on)\b',
            r'\b(i want to share|i\'d like to share|let me share)\b',
            r'\b(this is|these are|that is|those are)\b',
            r'\b(i found|i discovered|i learned)\b',
            r'\b(update|news|information|data|fact)\b'
        ]
        
        self.feedback_patterns = [
            r'\b(thank you|thanks|thx|thank)\b',
            r'\b(great|awesome|excellent|amazing|wonderful|fantastic)\b',
            r'\b(good|nice|cool|sweet|perfect|brilliant)\b',
            r'\b(bad|terrible|awful|horrible|disappointing)\b',
            r'\b(wrong|incorrect|not right|not correct)\b',
            r'\b(like|love|enjoy|appreciate)\b',
            r'\b(dislike|hate|don\'t like|not good)\b',
            r'\b(helpful|useful|useless|not helpful)\b',
            r'\b(clear|confusing|unclear|understand|don\'t understand)\b',
            r'\b(agree|disagree|correct|incorrect)\b',
            r'\b(rate|rating|score|review|feedback)\b',
            r'\b(improve|better|worse|change)\b'
        ]
        
        # Compile patterns for better performance
        self.greeting_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.greeting_patterns]
        self.query_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.query_patterns]
        self.information_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.information_patterns]
        self.feedback_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.feedback_patterns]
    
    def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify the intent of a user message.
        
        Args:
            message: The user's message text
            
        Returns:
            Tuple of (intent, confidence_score)
            Intent can be: 'greetings', 'query', 'information', 'feedback'
            Confidence score is between 0.0 and 1.0
        """
        if not message or not message.strip():
            return 'query', 0.0
        
        message = message.strip().lower()
        
        # Calculate scores for each intent
        greeting_score = self._calculate_score(message, self.greeting_regex)
        query_score = self._calculate_score(message, self.query_regex)
        information_score = self._calculate_score(message, self.information_regex)
        feedback_score = self._calculate_score(message, self.feedback_regex)
        
        # Get the highest scoring intent
        scores = {
            'greetings': greeting_score,
            'query': query_score,
            'information': information_score,
            'feedback': feedback_score
        }
        
        max_intent = max(scores, key=scores.get)
        max_score = scores[max_intent]
        
        # If no clear intent is detected, default to query
        if max_score < 0.1:
            return 'query', 0.1
        
        return max_intent, max_score
    
    def _calculate_score(self, message: str, patterns: list) -> float:
        """Calculate confidence score for a specific intent"""
        matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if pattern.search(message):
                matches += 1
        
        # Calculate score based on number of matches and message length
        base_score = matches / total_patterns if total_patterns > 0 else 0
        
        # Boost score for shorter messages (more likely to be clear intent)
        length_factor = max(0.5, 1.0 - (len(message) / 200))
        
        return min(1.0, base_score * length_factor)
    
    def get_intent_description(self, intent: str) -> str:
        """Get a human-readable description of the intent"""
        descriptions = {
            'greetings': 'User is greeting or starting a conversation',
            'query': 'User is asking a question or seeking information',
            'information': 'User is providing information or sharing knowledge',
            'feedback': 'User is giving feedback, thanks, or expressing opinion'
        }
        return descriptions.get(intent, 'Unknown intent')
    
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
    
    def extract_keywords(self, message: str) -> list:
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
        """Get which patterns matched for each intent type"""
        message_lower = message.lower()
        
        pattern_matches = {
            'greetings': [],
            'query': [],
            'information': [],
            'feedback': []
        }
        
        # Check greeting patterns
        for i, pattern in enumerate(self.greeting_regex):
            if pattern.search(message_lower):
                pattern_matches['greetings'].append(f"Pattern {i+1}: {self.greeting_patterns[i]}")
        
        # Check query patterns
        for i, pattern in enumerate(self.query_regex):
            if pattern.search(message_lower):
                pattern_matches['query'].append(f"Pattern {i+1}: {self.query_patterns[i]}")
        
        # Check information patterns
        for i, pattern in enumerate(self.information_regex):
            if pattern.search(message_lower):
                pattern_matches['information'].append(f"Pattern {i+1}: {self.information_patterns[i]}")
        
        # Check feedback patterns
        for i, pattern in enumerate(self.feedback_regex):
            if pattern.search(message_lower):
                pattern_matches['feedback'].append(f"Pattern {i+1}: {self.feedback_patterns[i]}")
        
        return pattern_matches

# Global intent classifier instance
intent_classifier = IntentClassifier()
