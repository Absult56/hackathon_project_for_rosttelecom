import random
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, Verify2FARequest, TokenResponse
from app.core.security import create_access_token, TEMP_2FA_CODES

router = APIRouter(prefix="/auth", tags=["Auth & 2FA"])


@router.post(
    "/request-code",
    summary="Шаг 1: Запрос 6-значного кода 2FA",
    description="Генерирует код, сохраняет в сессии и выводит в консоль бэкенда для демо-защиты"
)
def request_code(data: LoginRequest):
    # Генерация случайного 6-значного кода
    code = f"{random.randint(100000, 999999)}"
    TEMP_2FA_CODES[data.email] = code

    # Видимый лог для спикера хакатона
    print("\n" + "=" * 45)
    print(f"[*] ДЕМО-КОД 2FA ДЛЯ [{data.email}]: {code}")
    print(f"[*] РЕЗЕРВНЫЙ МАСТЕР-КОД ДЛЯ ЖЮРИ: 123456")
    print("=" * 45 + "\n")

    return {
        "status": "success",
        "message": f"Код подтверждения отправлен на {data.email} (код также выведен в консоль сервера)",
        "demo_hint": "Проверьте консоль бэкенда или введите 123456"
    }


@router.post(
    "/verify-2fa",
    response_model=TokenResponse,
    summary="Шаг 2: Валидация кода и выдача боевого JWT токена"
)
def verify_2fa(data: Verify2FARequest):
    expected_code = TEMP_2FA_CODES.get(data.email)

    # Отказоустойчивая валидация: либо сгенерированный код, либо мастер-код 123456
    is_valid = (data.code == expected_code) or (data.code == "123456")

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код подтверждения. Для демо введите: 123456"
        )

    # Очищаем временный код
    if data.email in TEMP_2FA_CODES:
        del TEMP_2FA_CODES[data.email]

    access_token = create_access_token(data={"sub": data.email})
    return TokenResponse(access_token=access_token, token_type="bearer")