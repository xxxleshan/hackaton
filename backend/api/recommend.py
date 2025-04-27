from fastapi import APIRouter, Depends
from db.queries import get_spending_with_cashback, get_top_categories
from api.auth import get_current_user_id

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/", summary="Рекомендации категорий по ожидаемому кешбэку")
def recommend_categories(user_id: int = Depends(get_current_user_id)):
    """
    Возвращает рекомендации по категориям:
      1) Сначала категории, отсортированные по ожидаемому кешбэку (spent * percent).
      2) Затем (если необходимо) категории с наивысшим процентом кешбэка,
         чтобы в сумме рекомендаций было ровно 5.
    """
    # 1) Получаем траты и проценты для пользователя
    rows = get_spending_with_cashback(user_id)
    recs = []

    # Преобразуем в список рекомендаций по expected cashback
    expected_list = []
    for cat_id, name, percent, spent in rows:
        spent_f = float(spent)
        percent_f = float(percent)
        expected_cashback = spent_f * percent_f / 100.0
        expected_list.append({
            "category_id":        cat_id,
            "category_name":      name,
            "total_spent":        round(spent_f, 2),
            "cashback_percent":   round(percent_f, 2),
            "expected_cashback":  round(expected_cashback, 2)
        })
    # Сортируем по убыванию возможного кешбэка
    expected_list.sort(key=lambda x: x["expected_cashback"], reverse=True)

    # 2) Включаем top expected cashback
    recs.extend(expected_list[:5])

    # 3) Если меньше 5, добираем по проценту кешбэка
    if len(recs) < 5:
        # получаем top категории по проценту
        top_percent = get_top_categories(limit=5)
        # исключаем уже включенные категории
        existing_ids = {r["category_id"] for r in recs}
        for cat_id, name, percent in top_percent:
            if len(recs) >= 5:
                break
            if cat_id in existing_ids:
                continue
            recs.append({
                "category_id":        cat_id,
                "category_name":      name,
                "total_spent":        0.0,
                "cashback_percent":   float(percent),
                "expected_cashback":  0.0
            })

    return {"recommendations": recs}