# File: backend/services/receipt_parser.py
from typing import List, Dict, Any
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def parse_receipt(
    fn: str,
    fd: str,
    fp: str,
    total: float,
    date_time_str: str,
    receipt_type: int = 1
) -> Dict[str, Any]:
    """
    Парсит чек через proverkacheka.com по параметрам ФН, ФД, ФП, общей сумме и дате-времени.

    :param fn: фискальный накопитель
    :param fd: фискальный документ
    :param fp: фискальный признак
    :param total: общая сумма чека
    :param date_time_str: в формате YYYYMMDDTHHMM, например 20250419T1314
    :param receipt_type: тип чека (1 — приход)
    :return: словарь с данными чека
    """
    # 1. Разбираем date_time_str
    # dt = datetime.strptime(date_time_str, "%Y%m%dT%H%M")
    if len(date_time_str.split('T')[1]) > 4:
        dt = datetime.strptime(date_time_str, "%Y%m%dT%H%M%S")
    else:
        dt = datetime.strptime(date_time_str, "%Y%m%dT%H%M")
    
    date = dt.strftime("%d.%m.%Y")
    time = dt.strftime("%H:%M")


    # 2. Запускаем браузер
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.get("https://proverkacheka.com/")

    # 3. Заполняем форму
    driver.find_element(By.ID, "b-checkform_fn").send_keys(fn)
    driver.find_element(By.ID, "b-checkform_fd").send_keys(fd)
    driver.find_element(By.ID, "b-checkform_fp").send_keys(fp)
    driver.find_element(By.ID, "b-checkform_s").send_keys(str(total))
    driver.find_element(By.ID, "b-checkform_date").send_keys(date)
    driver.find_element(By.ID, "b-checkform_time").send_keys(time)
    driver.find_element(By.CSS_SELECTOR, f"#b-checkform_n option[value='{receipt_type}']").click()
    driver.find_element(By.CSS_SELECTOR, ".b-checkform_btn-send").click()

    # 4. Ждём результат
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "b-check_place"))
    )

    # 5. Парсим HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # 6. Таблица чека
    table = soup.select_one(".b-check_place .b-check_table-place table")
    rows = table.find_all("tr")

    # 7. Общие данные
    store    = rows[0].td.get_text(strip=True)
    address  = rows[1].td.get_text(strip=True)
    inn_text = rows[2].td.get_text(strip=True)
    inn      = inn_text.replace("ИНН", "").strip()
    check_no = rows[5].td.get_text(strip=True).replace("Чек №", "").strip()
    shift_no = rows[6].td.get_text(strip=True).replace("Смена №", "").strip()

    # 8. Вид чека
    receipt_kind = rows[8].td.get_text(strip=True)

    # 9. Товары
    items: List[Dict[str, Any]] = []
    for item_row in table.find_all("tr", class_="b-check_item"):
        cols = item_row.find_all("td")
        items.append({
            "name":     cols[1].get_text(strip=True),
            "price":    float(cols[2].get_text(strip=True).replace(",", ".")),
            "quantity": float(cols[3].get_text(strip=True).replace(",", ".")),
            "sum":      float(cols[4].get_text(strip=True).replace(",", "."))
        })

    # 10. Итоги и платежи
    total_row = next(tr for tr in table.find_all("tr") if tr.find("td", class_="b-check_itogo"))
    total_val = total_row.find_all("td")[-1].get_text(strip=True)
    total_parsed = float(total_val.replace(",", "."))

    def get_sum(label: str) -> float:
        tr = next(tr for tr in table.find_all("tr") if tr.find("td") and tr.find("td").get_text(strip=True) == label)
        return float(tr.find_all("td")[-1].get_text(strip=True).replace(",", "."))

    cash = get_sum("Наличные")
    card = get_sum("Карта")

    vat_row = next(tr for tr in table.find_all("tr") if "НДС итога" in tr.find("td").get_text())
    vat = float(vat_row.find_all("td")[-1].get_text(strip=True).replace(",", "."))

    tax_row = next(tr for tr in table.find_all("tr", class_="b-check_vblock-last") if "ВИД НАЛОГООБЛЖЕНИЯ" in tr.get_text())
    taxation = tax_row.get_text(strip=True).split(":", 1)[1].strip()

    return {
        "store":        store,
        "address":      address,
        "inn":          inn,
        "check_number": check_no,
        "shift":        shift_no,
        "receipt_kind": receipt_kind,
        "items":        items,
        "total":        total_parsed,
        "cash":         cash,
        "card":         card,
        "vat":          vat,
        "taxation":     taxation,
    }









import requests



