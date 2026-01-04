from contextvars import ContextVar
from typing import Optional

# The ContextVar that will hold the Auth Token for the current request.
# It is type-hinted as Optional[str] but in a protected context it should always be present.
# We store the raw "Bearer <token>" value or just the <token> depending on preference.
# For this prototype, we'll store the raw token string.
_current_user_token: ContextVar[Optional[str]] = ContextVar("current_user_token", default=None)

def get_current_user_token() -> Optional[str]:
    """Retrieves the token for the current context."""
    return _current_user_token.get()

def set_current_user_token(token: str):
    """Sets the token for the current context. Returns a token to reset if needed."""
    return _current_user_token.set(token)
