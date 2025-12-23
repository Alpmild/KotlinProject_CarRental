from controller import client_router, car_router, user_router, rental_router, auth_router

from fastapi import FastAPI

app = FastAPI(
    title="Car Rental API ",
    description="Управление автомобилями и клиентами",
    version="1.3.3.7"
)

app.include_router(auth_router)
app.include_router(car_router)
app.include_router(client_router)
app.include_router(user_router)
app.include_router(rental_router)
