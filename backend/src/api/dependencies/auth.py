from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.application.utils.token import decode_token
from src.domain.entities.user import Role
from src.domain.exceptions import InsufficientPermissionsError, TokenInvalidError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/swagger")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise TokenInvalidError()
    return {"user_id": int(payload["sub"]), "role": payload["role"]}


def require_role(*roles: Role) -> Callable[..., Coroutine[Any, Any, dict]]:
    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in [r.value for r in roles]:
            raise InsufficientPermissionsError()
        return current_user

    return checker
