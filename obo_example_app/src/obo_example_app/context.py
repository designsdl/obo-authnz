from contextvars import ContextVar
from typing import Optional

_current_user_token: ContextVar[Optional[str]] = ContextVar("current_user_token", default=None)

def get_current_user_id() -> Optional[str]:
    """
    Returns the current user Identity (owner_id).
    In this simplified app, the Token IS the UserID.
    """
    return _current_user_token.get()

def set_current_user_id(user_id: str):
    return _current_user_token.set(user_id)
