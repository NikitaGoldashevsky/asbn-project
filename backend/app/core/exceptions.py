"""
Кастомные исключения приложения
"""
from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Ошибка аутентификации"""
    def __init__(self, detail: str = "Неверный логин или пароль"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Ошибка авторизации"""
    def __init__(self, detail: str = "Недостаточно прав"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundError(HTTPException):
    """Ресурс не найден"""
    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ValidationError(HTTPException):
    """Ошибка валидации данных"""
    def __init__(self, detail: str = "Некорректные данные"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class BlockedUserError(HTTPException):
    """Пользователь заблокирован"""
    def __init__(self, detail: str = "Пользователь заблокирован. Повторите попытку через 10 минут"):
        super().__init__(
            status_code=status.HTTP_423_LOCKED,
            detail=detail,
        )