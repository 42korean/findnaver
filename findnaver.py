from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="네이버 주식 시세 조회 백엔드")

# CORS 설정 (프론트엔드 웹에서 호출할 수 있도록 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
  return {"message": "주식 백엔드 서버가 정상적으로 작동 중입니다!"}


@app.get("/api/stock/{query}")
def get_naver_stock_price(query: str):
  """종목코드(6자리) 또는 종목명(예: 삼성전자)으로 네이버 금융에서 현재가를 조회합니다."""
  stock_code = query

  # 1. 입력된 값이 6자리 숫자가 아니라 종목명인 경우, 네이버 검색 API로 코드를 자동 검색
  if not (query.isdigit() and len(query) == 6):
    search_url = f"https://ac.stock.naver.com/ac?q={query}&target=stock"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    try:
      search_res = requests.get(search_url, headers=headers)
      if search_res.status_code == 200:
        search_data = search_res.json()
        items = search_data.get("items", [])
        if items and len(items) > 0 and len(items[0]) > 0:
          # 검색된 결과 중 첫 번째 항목의 종목 코드 추출
          stock_code = items[0][0].get("code")
    except Exception:
      pass  # 검색 실패 시 입력된 query 그대로 조회 시도

  # 2. 확정된 종목 코드로 네이버 금융 basic API 호출
  url = f"https://m.stock.naver.com/api/stock/{stock_code}/basic"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise HTTPException(
          status_code=404,
          detail=(
              f"'{query}'에 해당하는 주식 정보를 찾을 수 없습니다. 올바른"
              " 종목명이나 코드를 입력해주세요."
          ),
      )

    data = response.json()
    stock_name = data.get("stockName", query)
    close_price = data.get("closePrice", "0")

    return {
        "stockCode": stock_code,
        "stockName": stock_name,
        "currentPrice": close_price,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))