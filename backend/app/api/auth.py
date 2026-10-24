from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, Verify2FARequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth & 2FA"])

@router.post("/request-code", summary="Запрос одноразового кода 2FA")
def request_code(data: LoginRequest):
    # Логируем в консоль бэкенда для демо
    print(f"\n=============================")
    print(f"[*] 2FA CODE ДЛЯ {data.email}: 123456")
    print(f"=============================\n")
    return {"message": "Код подтверждения отправлен (проверьте консоль бэкенда)"}

@router.post("/login-2fa", response_model=TokenResponse, summary="Проверка 2FA кода и выдача JWT")
def login_2fa(data: Verify2FARequest):
    # Детерминированный хакатон-код 123456
    if data.code == "123456":
        return TokenResponse(
            access_token="mocked-jwt-token-hackathon-rtk-2024",
            token_type="bearer"
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Неверный код 2FA. Используйте резервный код: 123456"
    )