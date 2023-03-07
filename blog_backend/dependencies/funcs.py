import time
import re
import logging
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, Request, Header, HTTPException

from ..middlewares import Config


JWT_ALGORITHM = 'HS256'

CUSTOM_KEY = 'I_AM'
CUSTOM_VALUE = 'ENDAAMAN'


logger = logging.getLogger('uvicorn')


async def get_is_bearer_token(
    request: Request,
    authorization: str|None = Header(default=None),
) -> str|None:
    token = None
    if authorization:
        m = re.match(r'Bearer\s+(.*)$', authorization)
        if m:
            token = m[1]
    return token


async def get_is_authorized(
    request:Request,
    config:Config=Depends(),
    token:str|None=Depends(get_is_bearer_token),
) -> bool:
    if not token:
        return False

    try:
        decoded = jwt.decode(token, config.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail='Invalid authorization') from e

    exp = decoded.get('exp', None)
    if not exp:
        raise HTTPException(status_code=401, detail='Invalid payload in JWT')

    if decoded.get(CUSTOM_KEY) == CUSTOM_VALUE:
        raise HTTPException(status_code=401, detail='You are not me')

    diff = datetime.now() - datetime.fromtimestamp(exp)
    if diff > config.expiration_duration():
        raise HTTPException(status_code=401, detail='Your JWT token is expired')
    return True
