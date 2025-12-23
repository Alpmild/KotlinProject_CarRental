from service import get_current_user, create_access_token, UserDetailsService, get_auth_service
from dto import UserLoginResponseDTO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Применяем авторизацию КО ВСЕМ маршрутам этого роутера
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: UserDetailsService = Depends(get_auth_service)
):
    # 1. Проверяем учетные данные через ваш сервис
    email, password = form_data.username, form_data.password
    is_valid = auth_service.check_authorization(email, password)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Получаем пользователя из репозитория, чтобы взять его ID
    # В вашем UserDetailsService стоит добавить метод получения по email
    user_record = auth_service.get_user_by_email(email)

    if not user_record:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # 3. Создаем JWT токен, передавая ID пользователя в поле "sub"
    access_token = create_access_token(data={"sub": str(user_record.user_id)})

    return dict(access_token=access_token, token_type="bearer")



@router.get("/me", response_model=UserLoginResponseDTO)
def get_me(current_user: UserLoginResponseDTO = Depends(get_current_user)):
    """
    Пример защищенного эндпоинта, который возвращает данные
    текущего пользователя из токена.
    """
    return current_user