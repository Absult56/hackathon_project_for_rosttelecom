import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Настройки безопасности для хакатона
SECRET_KEY = "rostelecom-hackathon-super-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Токен на 24 часа, чтобы не слетал во время тестов

# Swagger UI добавит кнопку "Authorize" (Bearer токен)
security_scheme = HTTPBearer()

# Временное in-memory хранилище одноразовых кодов: { "email": "123456" }
TEMP_2FA_CODES: Dict[str, str] = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Генерация JWT-токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Валидация и расшифровка JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_scheme)) -> dict:
    """Dependency: проверяет Bearer-токен в заголовке Authorization."""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не идентифицирован"
        )
    return {"email": user_email}