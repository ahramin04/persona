#!/usr/bin/env python3
"""
Simple script to run the Offline LLM Chat application
"""

import uvicorn
import sys
import os

def main():
    """Run the FastAPI application"""
    print("Starting Offline LLM Chat Application...")
    print("Make sure LM Studio is running on http://127.0.0.1:1234")
    print("Application will be available at http://localhost:8000")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down application...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
