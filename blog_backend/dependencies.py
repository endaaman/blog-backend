import re
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, Request, Header, HTTPException

from .config import Config, acquire_config


JWT_ALGORITHM = 'HS256'

CUSTOM_KEY = 'I_AM'
CUSTOM_VALUE = 'ENDAAMAN'


def get_config():
    return acquire_config()

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
    request: Request,
    config: Config = Depends(get_config),
    token: str|None = Depends(get_is_bearer_token),
) -> bool:
    if not token:
        return False

    try:
        decoded = jwt.decode(token, config.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail='Invalid authorization') from e

    print(decoded)

    exp = decoded.get('exp', None)
    if not exp:
        raise HTTPException(status_code=401, detail='Invalid payload in JWT')

    if decoded.get(CUSTOM_KEY) == CUSTOM_VALUE:
        raise HTTPException(status_code=401, detail='You are not me')

    diff = datetime.now() - datetime.fromtimestamp(exp)
    if diff > config.expiration_duration():
        raise HTTPException(status_code=401, detail='Your JWT token is expired')
    return True

class BaseService:
    def __init__(self, config: Config = Depends(get_config)):
        self.config = config

class LoginService(BaseService):
    def login(self, password) -> bool:
        ok = bcrypt.checkpw(password.encode('utf-8'), self.config.PASSWORD_HASH.encode('utf-8'))
        if not ok:
            return None

        data = {
            CUSTOM_KEY: CUSTOM_VALUE,
            'exp': datetime.utcnow() + self.config.expiration_duration()
        }

        return jwt.encode(data, self.config.SECRET_KEY, algorithm=JWT_ALGORITHM)
