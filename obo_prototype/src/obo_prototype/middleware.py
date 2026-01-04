from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from .context import set_current_user_token

class OBOContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Extract Authorization Header
        auth_header = request.headers.get("Authorization")
        token = None
        
        if auth_header:
            # Expecting "Bearer <token>"
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        
        # 2. Bind to ContextVar
        # Even if token is None, we might want to proceed (for public endpoints)
        # But for this prototype, we'll just set what we have.
        # The ContextVar is thread-safe and asyncio-safe.
        # It scopes this value *only* to this specific async task loop.
        if token:
            token_setter = set_current_user_token(token)
        
        try:
            # 3. Process Request
            response = await call_next(request)
            return response
        finally:
            # 4. Cleanup (Optional but good practice if pooling is involved, 
            # though contextvars usually handle scope exit automatically in asyncio)
            pass 
