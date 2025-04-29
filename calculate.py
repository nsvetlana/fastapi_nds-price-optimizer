import math
from decimal import Decimal, getcontext, localcontext, ROUND_FLOOR
from pydantic import BaseModel, Field

# Устанавливаем высокую точность для вычислений с Decimal
getcontext().prec = 28

class PriceRequest(BaseModel):
    input_price_with_nds: Decimal = Field(
        ..., description="Рекомендованная цена с НДС (до 20 знаков после запятой)"
    )
    proc_nds: int = Field(..., ge=0, le=99, description="Процент НДС (от 0 до 99)")


class PriceResponse(BaseModel):
    corrected_price_with_nds: Decimal = Field(
        ..., description="Рассчитанная цена с НДС (ровно 2 знака после запятой)"
    )
    corrected_price_without_nds: Decimal = Field(
        ..., description="Рассчитанная цена без НДС (ровно 2 знака после запятой)"
    )


def optimal_calc_prices(input_price: Decimal, proc_nds: int) -> (Decimal, Decimal):
    """
    Оптимальное решение:
     - Вычисляем g = gcd(100, 100 + proc_nds)
     - Определяем шаг дискретизации: d = 100 // g.
     - Все допустимые значения цены без НДС имеют вид: m * d / 100, где m — целое число.
     - Тогда цена с НДС равна: (m * d * (100 + proc_nds)) / 10000.

    Находим вещественное m_ideal, затем сравниваем кандидатов:
      m_floor = floor(m_ideal) и m_ceil = m_floor + 1.
    Выбирается тот m, при котором ~|CPWith - InputPriceWithNDS| минимальна.
    """
    # Вычисляем НОД (g) для 100 и (100 + proc_nds)
    g = math.gcd(100, 100 + proc_nds)
    # Минимальный шаг: d
    d = 100 // g

    with localcontext() as ctx:
        ctx.prec = 28
        # Идеальное значение m как вещественное
        m_ideal = input_price * Decimal(10000) / Decimal(d * (100 + proc_nds))
        m_floor = int(m_ideal.to_integral_value(rounding=ROUND_FLOOR))
        m_ceil = m_floor + 1

        def candidate(m: int):
            cp_with = (Decimal(m * d * (100 + proc_nds)) / Decimal(10000)).quantize(
                Decimal("0.01")
            )
            cp_without = (Decimal(m * d) / Decimal(100)).quantize(Decimal("0.01"))
            return cp_with, cp_without

        cand_floor = candidate(m_floor)
        cand_ceil = candidate(m_ceil)

        err_floor = abs(cand_floor[0] - input_price)
        err_ceil = abs(cand_ceil[0] - input_price)

        if err_floor <= err_ceil:
            return cand_floor
        else:
            return cand_ceil

