from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn
import os

from api_routes import router

app = FastAPI(
    title="Offline LLM Chat API",
    description="A comprehensive API for offline AI chat using Mistral 7B via LM Studio with session management and conversation continuity",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Create templates directory
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/api-docs", response_class=HTMLResponse)
async def api_documentation(request: Request):
    """Serve the API documentation page"""
    return templates.TemplateResponse("api_docs.html", {"request": request})

@app.get("/docs", response_class=HTMLResponse)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 1,
            "defaultModelExpandDepth": 1,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": False,
            "showCommonExtensions": False,
            "tryItOutEnabled": True,
            "docExpansion": "list",
            "operationsSorter": "method",
            "tagsSorter": "alpha"
        }
    )

@app.get("/redoc", response_class=HTMLResponse)
async def redoc_html():
    """ReDoc documentation"""
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"
    )

def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    # Filter out non-API routes (web pages, docs, etc.)
    # Only include routes that start with /api and exclude root, docs, and other UI routes
    excluded_paths = {'/', '/docs', '/redoc', '/api-docs', '/openapi.json'}
    api_routes = [
        route for route in app.routes 
        if hasattr(route, 'path') and route.path.startswith('/api') and route.path not in excluded_paths
    ]
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=api_routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "Chat API",
            "description": "AI chat functionality with session management and conversation continuity"
        }
    ]
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    # Add contact information
    openapi_schema["info"]["contact"] = {
        "name": "Offline LLM Chat API",
        "url": "http://localhost:8000",
        "email": "support@example.com"
    }
    
    # Add license information
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)