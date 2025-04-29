
from fastapi import FastAPI, HTTPException
from calculate import optimal_calc_prices, PriceRequest, PriceResponse



app = FastAPI(
    title="Optimal CalcPrices API",
    description="Решение расчёта цен с НДС, использующее минимально допустимый шаг дискретизации.",
    version="1.0",
)

@app.get("/")
async def root():
    pass

@app.post("/optimal_calc_prices", response_model=PriceResponse)
def calc_prices_endpoint(req: PriceRequest):
    """
    Эндпоинт для расчёта цен:
      - input_price_with_nds: рекомендованная цена с НДС (до 20 знаков после запятой)
      - proc_nds: процент НДС от 0 до 99
    Возвращает:
      - corrected_price_with_nds: рассчитанная цена с НДС (ровно 2 знака после запятой)
      - corrected_price_without_nds: рассчитанная цена без НДС (ровно 2 знака после запятой)
    """
    try:
        cp_with, cp_without = optimal_calc_prices(
            req.input_price_with_nds, req.proc_nds
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return PriceResponse(
        corrected_price_with_nds=cp_with, corrected_price_without_nds=cp_without
    )


# Для запуска через uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
