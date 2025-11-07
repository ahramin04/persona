# Offline LLM Chat Application

A web-based chat application that uses LM Studio with Mistral 7B v0.3 for offline AI conversations. The application maintains conversation history and allows users to continue chats using session IDs.

## Features

- 🤖 **Offline AI Chat**: Powered by Mistral 7B v0.3 via LM Studio
- 💾 **Session Management**: Save and continue conversations using session IDs
- 📝 **Conversation Logging**: All chats are logged with timestamps
- 🔄 **Conversation Continuity**: AI remembers context from previous messages
- 🌐 **Web Interface**: Beautiful, responsive chat interface
- 📊 **Session History**: View and manage all chat sessions

## Prerequisites

1. **LM Studio**: Download and install from [https://lmstudio.ai/](https://lmstudio.ai/)
2. **Mistral 7B v0.3**: Load the model in LM Studio
3. **Python 3.8+**: Required for the backend

## Installation

1. **Clone or download this project**
   ```bash
   cd mahindra-showroom
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start LM Studio**
   - Open LM Studio
   - Load the Mistral 7B v0.3 model
   - Start the local server (usually runs on http://127.0.0.1:1234)

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8000` for the chat interface
   - Visit `http://localhost:8000/docs` for interactive Swagger UI
   - Check `http://localhost:8000/api-docs` for comprehensive API documentation

## Usage

### Web Interface
1. **Chat Interface** (`http://localhost:8000`):
   - Start new conversations
   - Continue existing chats using session IDs
   - View conversation history

2. **API Documentation** (`http://localhost:8000/api-docs`):
   - Comprehensive endpoint documentation
   - Request/response examples
   - Parameter descriptions

3. **Interactive Swagger UI** (`http://localhost:8000/docs`):
   - Test all API endpoints directly
   - Try different parameters
   - View real-time responses

### Starting a New Chat
1. Open the web interface
2. Type your message in the input field
3. Press Enter or click "Send"
4. The AI will respond and create a new session

### Continuing a Chat
1. Enter a session ID in the "Session ID" field
2. Click "Load Session"
3. Continue the conversation from where you left off

### API Testing with Swagger
1. Go to `http://localhost:8000/docs`
2. Click on any endpoint to expand it
3. Click "Try it out" to test the endpoint
4. Fill in the required parameters
5. Click "Execute" to see the response

### Session Management
- **View Sessions**: All sessions are stored in `logs/sessions/`
- **Session Files**: Each session is saved as a JSON file with the session ID as filename
- **Session Format**: Includes messages, timestamps, and metadata

## API Endpoints

### Web Interfaces
- `GET /` - Main chat interface
- `GET /api-docs` - Comprehensive API documentation page
- `GET /docs` - Interactive Swagger UI for testing endpoints
- `GET /redoc` - ReDoc documentation interface

### Chat API
- `POST /api/chat` - Send a message and get AI response
- `GET /api/sessions/{session_id}` - Retrieve a specific session
- `GET /api/sessions` - List all available sessions
- `GET /api/sessions/{session_id}/messages` - Get only messages from a session
- `DELETE /api/sessions/{session_id}` - Delete a session
- `GET /api/health` - Health check and LM Studio status

## Configuration

### LM Studio Settings
The application is configured to work with LM Studio's default settings:
- **URL**: `http://127.0.0.1:1234`
- **Model**: `mistral-7b-instruct-v0.3`
- **Temperature**: 0.7 (adjustable)
- **Max Tokens**: -1 (unlimited)

### Customization
You can modify the LM Studio client settings in `lm_studio_client.py`:
- Change the base URL if LM Studio runs on a different port
- Adjust default temperature and token limits
- Modify the model name if using a different model

## File Structure

```
mahindra-showroom/
├── main.py                 # FastAPI application with Swagger setup
├── api_routes.py          # Separate API routes and endpoints
├── lm_studio_client.py     # LM Studio API client
├── models.py              # Pydantic models
├── requirements.txt       # Python dependencies
├── run.py                 # Simple run script
├── templates/
│   ├── chat.html         # Main chat interface
│   └── api_docs.html     # API documentation page
├── logs/
│   └── sessions/         # Session storage
└── README.md            # This file
```

## Troubleshooting

### LM Studio Connection Issues
- Ensure LM Studio is running and the server is started
- Check that the model is loaded and ready
- Verify the URL in `lm_studio_client.py` matches your LM Studio setup

### Session Loading Issues
- Check that session files exist in `logs/sessions/`
- Ensure proper file permissions for reading/writing session files
- Verify session ID format (should be a valid UUID)

### Performance Issues
- Adjust temperature and max_tokens in the chat request
- Consider using a smaller model if Mistral 7B is too slow
- Monitor system resources (CPU, RAM, GPU)

## Example Usage

1. **Ask about cotton candy**:
   - User: "What is cotton candy?"
   - AI: [Explains what cotton candy is]

2. **Continue the conversation**:
   - User: "How do you make it?"
   - AI: [Provides instructions, remembering the previous context about cotton candy]

3. **Save and resume later**:
   - Note the session ID from the interface
   - Later, enter the session ID to continue the conversation

## License

This project is open source and available under the MIT License.
