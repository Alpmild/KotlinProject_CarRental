from .AuthController import router as auth_router
from .CarController import router as car_router
from .ClientController import router as client_router
from .UserController import router as user_router
from .RentalController import router as rental_router

__all__ = [
    'auth_router',
    'car_router',
    'client_router',
    'user_router',
    'rental_router'
]

