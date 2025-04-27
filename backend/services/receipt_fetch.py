import requests
from config import CHECK_API_TOKEN
# from config import JWT_SECRET


# def fetch_receipt_data(qr_string: str) -> dict:
#     # Здесь можно добавить авторизацию, подпись запроса и т.п.
#     response = requests.get(f"https://external.api/receipt?qr={qr_string}")
#     response.raise_for_status()
#     return response.json()



def fetch_receipt_data(data):
    if not data:
        return None

    result = {}
    try:
        pairs = data.split('&')
        for pair in pairs:
            if '=' not in pair:
                return None
            key, value = pair.split('=', 1)
            result[key] = value
        return result
    except Exception:
        return None



import requests

def get_store_info(fn, fd, fp, t, n, s):
    """
    Получение информации о магазине по реквизитам чека через API проверки чека.

    :param fn: Номер фискального накопителя
    :param fd: Номер фискального документа
    :param fp: Фискальный признак документа
    :param t: Дата и время чека в формате 'YYYYMMDDTHHMM'
    :param n: Тип операции (1 - приход, 2 - возврат прихода, 3 - расход, 4 - возврат расхода)
    :param s: Сумма чека
    :return: Словарь с данными о магазине, товарах и сумме
    """
    url = 'https://proverkacheka.com/api/v1/check/get'
    data = {
        'token': CHECK_API_TOKEN,
        'fn': fn,
        'fd': fd,
        'fp': fp,
        't': t,
        'n': n,
        's': s,
        'qr': '0'
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 1:
            json_data = result['data']['json']

            store = json_data.get('user', 'Неизвестно')
            address = json_data.get('retailPlaceAddress', 'Неизвестно')
            inn = json_data.get('userInn', 'Неизвестно').strip()

            items = []
            for item in json_data.get('items', []):
                items.append({
                    'name': item.get('name', ''),
                    'price': item.get('price', 0)/100,     # без деления на 100
                    'quantity': item.get('quantity', 0),
                    'sum': item.get('sum', 0)/100          # без деления на 100
                })

            total_sum = json_data.get('totalSum', 0)  # без деления на 100

            return {
                "store": store,
                "address": address,
                "inn": inn,
                "items": items,
                "total": total_sum/100
            }
        else:
            return {'error': f"Ошибка API, код: {result.get('code')}"}

    except Exception as e:
        return {'error': str(e)}



if __name__ == "__main__":
    fetch_receipt_data()