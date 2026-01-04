from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .context import set_current_user_id

class OBOContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        user_id = None
        
        if auth_header:
            # Format: "Bearer <username>"
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                user_id = parts[1]
                
        if user_id:
            set_current_user_id(user_id)
            
        response = await call_next(request)
        return response
