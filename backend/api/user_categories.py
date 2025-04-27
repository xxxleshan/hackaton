from fastapi import APIRouter, HTTPException, Depends, Body
from db.queries import get_user_by_id, get_category, add_user_category
from api.auth import login  # for Depends? or import dependency
def get_current_user_id(authorization: str = Depends(lambda: None)):
    # TODO: вынести в общий модуль; здесь заглушка для Depends
    return 1

router = APIRouter(prefix="/users/{user_id}/categories", tags=["user_categories"])

@router.post("/", summary="Добавить новую категорию кешбэка для пользователя")
def assign_cashback_category(
    user_id: int,
    body: dict = Body(...)
):
    cat_id = body.get("category_id")
    if not cat_id:
        raise HTTPException(400, "category_id обязателен")

    if not get_user_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")
    if not get_category(cat_id):
        raise HTTPException(404, "Категория не найдена")

    add_user_category(user_id, cat_id)
    return {"status": "ok", "message": f"Категория {cat_id} добавлена для пользователя {user_id}"}
