from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.qr_scanner import scan_qr_code
from services.receipt_fetch import fetch_receipt_data
from services.receipt_fetch import get_store_info
# from services.receipt_parser import recognize_store
from db.queries import insert_receipt, insert_receipt_item,get_store_by_name
from api.auth import login  # placeholder
from api.auth import get_current_user_id
import os
from datetime import datetime


# def get_current_user_id(authorization: str = Depends(lambda: None)):
#     return 1

script_path = os.path.abspath(__file__)


router = APIRouter(prefix="/receipts", tags=["receipts"])

@router.post("/upload", summary="Загрузить и обработать чек")
async def upload_receipt(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    # Сохранение файла
    print(os.getcwd())
    temp_path = f"{os.getcwd()}/backend/receipts/{file.filename}"
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    # Сканируем QR
    qr = scan_qr_code(temp_path)
    if not qr:
        raise HTTPException(422, "QR-код не найден или не распознан")

    # Получаем данные из внешнего API
    data = fetch_receipt_data(qr)
    print(data)

    total = data["s"]
    date = datetime.strptime(data["t"], "%Y%m%dT%H%M%S")

    data = get_store_info(data["fn"], data["i"], data["fp"], data["t"], data["n"], data["s"])
    
    store_id = get_store_by_name(data["store"].replace("\"","'"))[0]

    receipt_id = insert_receipt(user_id, store_id, total, date, temp_path)


    # # # # Вставляем товары
    for item in data.get("items", []):
        name = item.get("name")
        qty = item.get("quantity", 1)
        price = item.get("price")
        insert_receipt_item(receipt_id, name, qty, price)

    # return {"status": "ok", "receipt_id": receipt_id}