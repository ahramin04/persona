from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
import os
import json
import aiofiles
import uuid
from datetime import datetime

from lm_studio_client import LMStudioClient
from models import ChatMessage, ChatSession, ChatRequest, ContinueChatRequest, ChatResponse, SessionResponse, IntentAnalysis
from logger_config import logger_config
from ai_intent_classifier import ai_intent_classifier
from chain_query_generator import chain_query_generator

# Create router for API endpoints
router = APIRouter(prefix="/api", tags=["Chat API"])

# Initialize LM Studio client
lm_client = LMStudioClient()

@router.post("/chat", 
             response_model=ChatResponse,
             summary="Start a new chat",
             description="Send a message to start a new chat session. A new session ID will be automatically created.")
async def chat_endpoint(chat_request: ChatRequest):
    """
    Start a new chat session with the AI.
    
    - **message**: The user's message to send to the AI
    
    Returns a new session ID and AI response.
    """
    session_id = None
    try:
        session_id = str(uuid.uuid4())
        
        # Log the incoming request
        logger_config.log_info(f"New chat request received: {chat_request.message[:100]}...", session_id)
        
        # Classify user intent using AI
        intent, confidence = await ai_intent_classifier.classify_intent(chat_request.message)
        keywords = ai_intent_classifier.extract_keywords(chat_request.message)
        complexity = ai_intent_classifier.analyze_message_complexity(chat_request.message)
        
        # Log intent analysis
        logger_config.log_intent(
            chat_request.message, 
            intent, 
            confidence, 
            session_id
        )
        
        logger_config.log_debug(f"Intent analysis - Intent: {intent}, Confidence: {confidence:.2f}, Keywords: {keywords[:5]}", session_id)
        
        # Create new session
        session = ChatSession(
            session_id=session_id,
            created_at=datetime.now(),
            messages=[]
        )
        logger_config.log_info(f"New session created: {session_id}", session_id)
        
        # Add user message to session with intent information
        user_message = ChatMessage(
            role="user",
            content=chat_request.message,
            timestamp=datetime.now(),
            intent=intent,
            intent_confidence=confidence,
            keywords=keywords,
            complexity=complexity
        )
        session.messages.append(user_message)
        
        # Prepare messages for LM Studio (include conversation history)
        lm_messages = []
        for msg in session.messages:
            lm_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Log the request to LM Studio
        logger_config.log_debug(f"Sending {len(lm_messages)} messages to LM Studio", session_id)
        
        # Get response from LM Studio with default settings
        response = await lm_client.chat_completion(
            messages=lm_messages,
            temperature=0.7,
            max_tokens=-1
        )
        
        # Log the response
        logger_config.log_info(f"Received response from LM Studio: {response[:100]}...", session_id)
        
        # Add assistant response to session
        assistant_message = ChatMessage(
            role="assistant",
            content=response,
            timestamp=datetime.now()
        )
        session.messages.append(assistant_message)
        
        # Enhance response with follow-up question
        if chain_query_generator.should_generate_follow_up(intent, len(response)):
            try:
                response = await chain_query_generator.append_best_follow_up_to_response(
                    chat_request.message, response, intent
                )
                logger_config.log_debug(f"Enhanced response with follow-up question", session_id)
            except Exception as e:
                logger_config.log_warning(f"Failed to enhance response with follow-up question: {e}", session_id)
        
        # Save session
        await save_session(session)
        logger_config.log_info(f"Session saved successfully", session_id)
        
        return ChatResponse(
            session_id=session_id,
            message=response,
            conversation_history=session.messages,
            user_intent=intent,
            intent_confidence=confidence
        )
        
    except Exception as e:
        logger_config.log_error(f"Error in chat endpoint: {str(e)}", session_id, exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/continue-chat", 
             response_model=ChatResponse,
             summary="Continue an existing chat",
             description="Send a message to continue an existing chat session using the session ID.")
async def continue_chat_endpoint(continue_request: ContinueChatRequest):
    """
    Continue an existing chat session with the AI.
    
    - **message**: The user's message to send to the AI
    - **session_id**: The session ID to continue the conversation
    
    Returns the AI response and updated conversation history.
    """
    try:
        session_id = continue_request.session_id
        
        # Log the incoming request
        logger_config.log_info(f"Continue chat request received: {continue_request.message[:100]}...", session_id)
        
        # Load existing session
        session = await load_session(session_id)
        if session is None:
            logger_config.log_warning(f"Session not found for continuation: {session_id}", session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger_config.log_info(f"Continuing existing session: {session_id}", session_id)
        
        # Classify user intent using AI
        intent, confidence = await ai_intent_classifier.classify_intent(continue_request.message)
        keywords = ai_intent_classifier.extract_keywords(continue_request.message)
        complexity = ai_intent_classifier.analyze_message_complexity(continue_request.message)
        
        # Log intent analysis
        logger_config.log_intent(
            continue_request.message, 
            intent, 
            confidence, 
            session_id
        )
        
        logger_config.log_debug(f"Intent analysis - Intent: {intent}, Confidence: {confidence:.2f}, Keywords: {keywords[:5]}", session_id)
        
        # Add user message to session with intent information
        user_message = ChatMessage(
            role="user",
            content=continue_request.message,
            timestamp=datetime.now(),
            intent=intent,
            intent_confidence=confidence,
            keywords=keywords,
            complexity=complexity
        )
        session.messages.append(user_message)
        
        # Prepare messages for LM Studio (include conversation history)
        lm_messages = []
        for msg in session.messages:
            lm_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Log the request to LM Studio
        logger_config.log_debug(f"Sending {len(lm_messages)} messages to LM Studio", session_id)
        
        # Get response from LM Studio with default settings
        response = await lm_client.chat_completion(
            messages=lm_messages,
            temperature=0.7,
            max_tokens=-1
        )
        
        # Log the response
        logger_config.log_info(f"Received response from LM Studio: {response[:100]}...", session_id)
        
        # Add assistant response to session
        assistant_message = ChatMessage(
            role="assistant",
            content=response,
            timestamp=datetime.now()
        )
        session.messages.append(assistant_message)
        
        # Enhance response with follow-up question
        if chain_query_generator.should_generate_follow_up(intent, len(response)):
            try:
                response = await chain_query_generator.append_best_follow_up_to_response(
                    continue_request.message, response, intent
                )
                logger_config.log_debug(f"Enhanced response with follow-up question", session_id)
            except Exception as e:
                logger_config.log_warning(f"Failed to enhance response with follow-up question: {e}", session_id)
        
        # Save session
        await save_session(session)
        logger_config.log_info(f"Session updated successfully", session_id)
        
        return ChatResponse(
            session_id=session_id,
            message=response,
            conversation_history=session.messages,
            user_intent=intent,
            intent_confidence=confidence
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger_config.log_error(f"Error in continue chat endpoint: {str(e)}", continue_request.session_id, exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", 
            response_model=ChatSession,
            summary="Get a specific chat session",
            description="Retrieve a complete chat session including all messages and timestamps.")
async def get_session(session_id: str):
    """
    Retrieve a specific chat session by its ID.
    
    - **session_id**: The unique identifier of the session to retrieve
    """
    try:
        logger_config.log_info(f"Retrieving session: {session_id}", session_id)
        session = await load_session(session_id)
        if session is None:
            logger_config.log_warning(f"Session not found: {session_id}", session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        logger_config.log_info(f"Session retrieved successfully: {len(session.messages)} messages", session_id)
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger_config.log_error(f"Error retrieving session: {str(e)}", session_id, exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", 
            response_model=List[str],
            summary="List all chat sessions",
            description="Get a list of all available chat session IDs, sorted by most recent first.")
async def list_sessions():
    """
    List all available chat sessions.
    
    Returns a list of session IDs that can be used to retrieve specific sessions.
    """
    try:
        logger_config.log_info("Listing all sessions")
        sessions_dir = "logs/sessions"
        if not os.path.exists(sessions_dir):
            logger_config.log_warning("Sessions directory does not exist")
            return []
        
        session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
        session_ids = [f.replace('.json', '') for f in session_files]
        result = sorted(session_ids, reverse=True)  # Most recent first
        logger_config.log_info(f"Found {len(result)} sessions")
        return result
    except Exception as e:
        logger_config.log_error(f"Error listing sessions: {str(e)}", exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}", 
               summary="Delete a chat session",
               description="Permanently delete a chat session and all its messages.")
async def delete_session(session_id: str):
    """
    Delete a specific chat session.
    
    - **session_id**: The unique identifier of the session to delete
    
    Returns success message if deletion was successful.
    """
    try:
        logger_config.log_info(f"Delete session requested: {session_id}", session_id)
        session_file = f"logs/sessions/{session_id}.json"
        if os.path.exists(session_file):
            os.remove(session_file)
            logger_config.log_info(f"Session deleted successfully: {session_id}", session_id)
            return {"message": "Session deleted successfully", "session_id": session_id}
        else:
            logger_config.log_warning(f"Session not found for deletion: {session_id}", session_id)
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger_config.log_error(f"Error deleting session: {str(e)}", session_id, exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages", 
            response_model=List[ChatMessage],
            summary="Get session messages",
            description="Retrieve only the messages from a specific session without session metadata.")
async def get_session_messages(session_id: str):
    """
    Get only the messages from a specific session.
    
    - **session_id**: The unique identifier of the session
    
    Returns a list of messages in chronological order.
    """
    try:
        logger_config.log_info(f"Retrieving messages for session: {session_id}", session_id)
        session = await load_session(session_id)
        if session is None:
            logger_config.log_warning(f"Session not found for messages: {session_id}", session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        logger_config.log_info(f"Retrieved {len(session.messages)} messages for session: {session_id}", session_id)
        return session.messages
    except HTTPException:
        raise
    except Exception as e:
        logger_config.log_error(f"Error retrieving session messages: {str(e)}", session_id, exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze-intent", 
             response_model=IntentAnalysis,
             summary="Analyze message intent",
             description="Analyze the intent of a user message without sending it to the AI.")
async def analyze_intent(message: str):
    """
    Analyze the intent of a user message.
    
    - **message**: The message to analyze
    
    Returns detailed intent analysis including confidence, keywords, and complexity.
    """
    try:
        logger_config.log_info(f"Intent analysis requested for: {message[:50]}...")
        
        # Classify intent using AI
        intent, confidence = await ai_intent_classifier.classify_intent(message)
        keywords = ai_intent_classifier.extract_keywords(message)
        complexity = ai_intent_classifier.analyze_message_complexity(message)
        description = ai_intent_classifier.get_intent_description(intent)
        
        result = IntentAnalysis(
            intent=intent,
            confidence=confidence,
            description=description,
            keywords=keywords,
            complexity=complexity
        )
        
        logger_config.log_info(f"Intent analysis completed: {intent} (confidence: {confidence:.2f})")
        return result
        
    except Exception as e:
        logger_config.log_error(f"Error analyzing intent: {str(e)}", exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intents", 
            summary="Get all available intents",
            description="Retrieve a list of all available intent types with their descriptions.")
async def get_intents():
    """
    Get all available intent types and their descriptions.
    
    Returns a list of intent types with descriptions.
    """
    try:
        logger_config.log_info("Retrieving all available intents")
        
        intents = [
            {
                "intent": "greetings",
                "description": "User is greeting or starting a conversation",
                "examples": "Hello, Hi there, Good morning, How are you?"
            },
            {
                "intent": "query", 
                "description": "User is asking a question or seeking information",
                "examples": "What is..., How do I..., Can you help me..., Explain..."
            },
            {
                "intent": "information",
                "description": "User is providing information or sharing knowledge", 
                "examples": "I want to tell you..., Here's what I know..., Let me share..."
            },
            {
                "intent": "feedback",
                "description": "User is giving feedback, thanks, or expressing opinion",
                "examples": "Thank you, That's helpful, I like this, Great job"
            }
        ]
        
        logger_config.log_info(f"Returned {len(intents)} intent types")
        return intents
        
    except Exception as e:
        logger_config.log_error(f"Error retrieving intents: {str(e)}", exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intent-analysis", 
            response_model=IntentAnalysis,
            summary="Analyze message intent with detailed response",
            description="Analyze the intent of a user message and return detailed analysis including patterns matched.")
async def get_intent_analysis(message: str):
    """
    Analyze the intent of a user message with detailed information.
    
    - **message**: The message to analyze
    
    Returns detailed intent analysis including confidence, keywords, complexity, and matched patterns.
    """
    try:
        logger_config.log_info(f"Detailed intent analysis requested for: {message[:50]}...")
        
        # Classify intent using AI
        intent, confidence = await ai_intent_classifier.classify_intent(message)
        keywords = ai_intent_classifier.extract_keywords(message)
        complexity = ai_intent_classifier.analyze_message_complexity(message)
        description = ai_intent_classifier.get_intent_description(intent)
        
        # Get pattern matches for detailed analysis
        pattern_matches = ai_intent_classifier.get_pattern_matches(message)
        
        result = IntentAnalysis(
            intent=intent,
            confidence=confidence,
            description=description,
            keywords=keywords,
            complexity=complexity
        )
        
        # Add pattern matches to the result
        result_dict = result.dict()
        result_dict["pattern_matches"] = pattern_matches
        result_dict["message_length"] = len(message)
        result_dict["word_count"] = len(message.split())
        
        logger_config.log_info(f"Detailed intent analysis completed: {intent} (confidence: {confidence:.2f})")
        return result_dict
        
    except Exception as e:
        logger_config.log_error(f"Error in detailed intent analysis: {str(e)}", exception=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", 
            summary="Health check",
            description="Check if the application and LM Studio are running properly.")
async def health_check():
    """
    Check the health of the application and LM Studio connection.
    
    Returns status information about the service and LM Studio connectivity.
    """
    try:
        logger_config.log_debug("Health check requested")
        lm_studio_status = lm_client.test_connection()
        
        result = {
            "status": "healthy" if lm_studio_status else "degraded",
            "lm_studio_connected": lm_studio_status,
            "timestamp": datetime.now().isoformat(),
            "message": "Service is running" if lm_studio_status else "LM Studio connection failed"
        }
        
        logger_config.log_info(f"Health check completed: {result['status']}")
        return result
        
    except Exception as e:
        logger_config.log_error(f"Error in health check: {str(e)}", exception=e)
        return {
            "status": "error",
            "lm_studio_connected": False,
            "timestamp": datetime.now().isoformat(),
            "message": f"Health check failed: {str(e)}"
        }

# Helper functions (same as in main.py)
async def load_session(session_id: str) -> ChatSession:
    """Load a chat session from file"""
    session_file = f"logs/sessions/{session_id}.json"
    if not os.path.exists(session_file):
        return None
    
    try:
        async with aiofiles.open(session_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
            
            # Convert messages back to ChatMessage objects
            messages = []
            for msg_data in data.get('messages', []):
                # Handle both old and new message formats
                message = ChatMessage(
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=datetime.fromisoformat(msg_data['timestamp']),
                    intent=msg_data.get('intent'),
                    intent_confidence=msg_data.get('intent_confidence'),
                    keywords=msg_data.get('keywords'),
                    complexity=msg_data.get('complexity')
                )
                messages.append(message)
            
            return ChatSession(
                session_id=data['session_id'],
                created_at=datetime.fromisoformat(data['created_at']),
                messages=messages
            )
    except Exception as e:
        logger_config.log_error(f"Error loading session {session_id}: {e}", session_id, exception=e)
        return None

async def save_session(session: ChatSession):
    """Save a chat session to file"""
    session_file = f"logs/sessions/{session.session_id}.json"
    
    try:
        # Convert session to dictionary
        session_data = {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'intent': msg.intent,
                    'intent_confidence': msg.intent_confidence,
                    'keywords': msg.keywords,
                    'complexity': msg.complexity
                }
                for msg in session.messages
            ]
        }
        
        async with aiofiles.open(session_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(session_data, indent=2, ensure_ascii=False))
        
        logger_config.log_debug(f"Session saved: {session.session_id} with {len(session.messages)} messages", session.session_id)
        
    except Exception as e:
        logger_config.log_error(f"Error saving session {session.session_id}: {e}", session.session_id, exception=e)
        raise
