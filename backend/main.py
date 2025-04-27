from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, upload, stats, recommend, user_categories

app = FastAPI(title="Smart Purchases API")

# --- CORS настройка ---
origins = [
    "http://localhost:3000",   # если фронт запускается на порту 3000
    "http://127.0.0.1:3000",
    "http://localhost:8000",   # можно добавить сам backend для тестов
    "*"                        # или просто "*", если неважно
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # откуда разрешаем запросы
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, OPTIONS…
    allow_headers=["*"],          # заголовки, которые допускаются
)
# --- Конец CORS настройки ---

# Регистрируем роутеры
app.include_router(auth.router)
app.include_router(user_categories.router)
app.include_router(upload.router)
app.include_router(stats.router)
app.include_router(recommend.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
