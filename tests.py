# import math
import sys
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

# Импортируем наше приложение
from main import app

client = TestClient(app)

def test_typical_value_1():
    """
    Проверка типового примера:
      InputPriceWithNDS = 1.81, proc_nds = 20
    Ожидаемые результаты (как в примере задания):
      CorrectedPriceWithNDS = 1.80
      CorrectedPriceWithoutNDS = 1.50
    """
    response = client.post("/optimal_calc_prices", json={
        "input_price_with_nds": "1.81",
        "proc_nds": 20
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["corrected_price_with_nds"] == "1.80", f"Получено {data['corrected_price_with_nds']}"
    assert data["corrected_price_without_nds"] == "1.50", f"Получено {data['corrected_price_without_nds']}"

def test_typical_value_2():
    """
    Проверка типового примера:
      InputPriceWithNDS = 1.81, proc_nds = 18
    Ожидаемые результаты:
      CorrectedPriceWithNDS = 1.77
      CorrectedPriceWithoutNDs = 1.50
    """
    response = client.post("/optimal_calc_prices", json={
        "input_price_with_nds": "1.81",
        "proc_nds": 18
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["corrected_price_with_nds"] == "1.77"
    assert data["corrected_price_without_nds"] == "1.50"

def test_zero_tax():
    """
    Если процент НДС равен 0, то цена с НДС и без НДС должны совпадать с исходным значением.
    """
    response = client.post("/optimal_calc_prices", json={
        "input_price_with_nds": "1.81",
        "proc_nds": 0
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["corrected_price_with_nds"] == "1.81"
    assert data["corrected_price_without_nds"] == "1.81"

def test_max_tax():
    """
    Проверка с максимальным значением ставки НДС (proc_nds = 99).
    Пример: InputPriceWithNDS = 100.00.
    Здесь важно проверить, что результаты имеют ровно 2 знака после запятой.
    """
    response = client.post("/optimal_calc_prices", json={
        "input_price_with_nds": "100.00",
        "proc_nds": 99
    })
    assert response.status_code == 200, response.text
    data = response.json()
    cp_with = Decimal(data["corrected_price_with_nds"])
    cp_without = Decimal(data["corrected_price_without_nds"])
    # Проверяем наличие ровно двух десятичных знаков:
    assert cp_with.as_tuple().exponent == -2
    assert cp_without.as_tuple().exponent == -2

def test_extreme_large_price():
    """
    Тестирование с очень большим значением цены.
    """
    large_price = "12345678901234567890.12"
    response = client.post("/optimal_calc_prices", json={
        "input_price_with_nds": large_price,
        "proc_nds": 50
    })
    assert response.status_code == 200, response.text
    data = response.json()
    cp_with = Decimal(data["corrected_price_with_nds"])
    cp_without = Decimal(data["corrected_price_without_nds"])
    # Проверяем, что оба результата имеют ровно 2 знака после запятой
    assert cp_with.as_tuple().exponent == -2, f"CPWith = {data['corrected_price_with_nds']}"
    assert cp_without.as_tuple().exponent == -2, f"CPWithout = {data['corrected_price_without_nds']}"

def test_extreme_high_precision_price():
    """
    Тестирование с ценой, заданной с максимальной точностью (до 20 знаков после запятой).
    """
    high_precision = "1.00000000000000000001"
    response = client.post("/optimal_calc_prices", json={
        "input_price_with_nds": high_precision,
        "proc_nds": 18
    })
    assert response.status_code == 200, response.text
    data = response.json()
    cp_with = Decimal(data["corrected_price_with_nds"])
    cp_without = Decimal(data["corrected_price_without_nds"])
    assert cp_with.as_tuple().exponent == -2
    assert cp_without.as_tuple().exponent == -2

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
