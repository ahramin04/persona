import requests
import json
from typing import List, Dict, Any
import asyncio
import aiohttp

class LMStudioClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        self.base_url = base_url
        self.model = "mistral-7b-instruct-v0.3"
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7, 
        max_tokens: int = -1,
        stream: bool = False
    ) -> str:
        """
        Send chat completion request to LM Studio
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"LM Studio API error {response.status}: {error_text}")
                    
                    if stream:
                        return await self._handle_streaming_response(response)
                    else:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
        
        except aiohttp.ClientError as e:
            raise Exception(f"Connection error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error calling LM Studio: {str(e)}")
    
    async def _handle_streaming_response(self, response) -> str:
        """
        Handle streaming response from LM Studio
        """
        full_content = ""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                if data == '[DONE]':
                    break
                try:
                    json_data = json.loads(data)
                    if 'choices' in json_data and len(json_data['choices']) > 0:
                        delta = json_data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            full_content += delta['content']
                except json.JSONDecodeError:
                    continue
        
        return full_content
    
    def test_connection(self) -> bool:
        """
        Test if LM Studio is running and accessible
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False
