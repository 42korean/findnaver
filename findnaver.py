from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="주식 현재가 백엔드 서버")

# 웹 브라우저에서 다른 도메인(HTML 페이지 등)으로 접근할 때 CORS 에러가 나지 않도록 허용
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


@app.get("/api/stock/{stock_code}")
def get_naver_stock_price(stock_code: str):
  """네이버 모바일 금융 API를 통해 종목 코드(예: 삼성전자 005930)의 현재가를 조회합니다."""
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
          status_code=404, detail="종목 정보를 가져오지 못했습니다."
      )

    data = response.json()

    # 네이버 API 응답 데이터에서 필요한 정보 추출
    stock_name = data.get("stockName", "알 수 없음")
    close_price = data.get("closePrice", "0")  # 현재가 (문자열 형태)

    return {
        "stockCode": stock_code,
        "stockName": stock_name,
        "currentPrice": close_price,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))