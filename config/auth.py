# config/auth.py
from fastapi import Request, HTTPException

def get_current_user(request: Request) -> str:
    """Returns user_id or raises 401"""
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401)
    return user_id

from fastapi import Request
from fastapi.responses import RedirectResponse

def get_current_user(request: Request) -> str | None:
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return user_id