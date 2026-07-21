from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from decouple import config

SECRET_KEY = config('JWT_SECRET_KEY')
ALGORITHM = config('JWT_ALGORITHM', default='HS256')
EXPIRE_MINS = config('JWT_EXPIRE_MINUTES', default=60, cast=int)

# Le dice a FastAPI dónde está el endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT con los datos del usuario."""
    payload = data.copy()
    expira = datetime.utcnow() + (expires_delta or timedelta(minutes=EXPIRE_MINS))
    payload.update({'exp': expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_actual(token: str = Depends(oauth2_scheme)):
    """
    Dependencia que protege cualquier endpoint.
    Extrae y valida el token JWT, luego devuelve el usuario de Django.
    """
    credenciales_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Token inválido o expirado',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credenciales_error
    except JWTError:
        raise credenciales_error
    
    #Busca el usuario en la base de datos de Django
    from apps.usuarios.models import Usuario
    try:
        return Usuario.objects.get(username=username, is_active=True)
    except Usuario.DoesNotExist:
        raise credenciales_error