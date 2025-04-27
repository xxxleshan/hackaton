from fastapi import APIRouter, Depends
from db.queries import get_spending_by_category, get_spending_by_month
from api.auth import login
def get_current_user_id(authorization: str = Depends(lambda: None)):
    return 1

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/categories", summary="Статистика трат по категориям")
def stats_categories(user_id: int = Depends(get_current_user_id)):
    rows = get_spending_by_category(user_id)
    return {"stats": [{"category_id": r[0], "category": r[1], "total": float(r[2])} for r in rows]}

@router.get("/monthly", summary="Статистика трат по месяцам")
def stats_monthly(user_id: int = Depends(get_current_user_id)):
    rows = get_spending_by_month(user_id)
    return {"stats": [{"month": r[0].strftime("%Y-%m-%d"), "total": float(r[1])} for r in rows]}

