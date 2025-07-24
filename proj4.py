# # nfl_api.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import requests
# from bs4 import BeautifulSoup
# import uvicorn
#
# app = FastAPI()
#
# # Allow all origins (for local use)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# @app.get("/get_nfl_stats")
# def get_nfl_stats(year: int):
#     try:
#         url = f"https://www.pro-football-reference.com/years/{year}/rushing.htm"
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#         }
#         res = requests.get(url, headers=headers)
#         res.raise_for_status()
#
#         soup = BeautifulSoup(res.text, "lxml")
#         table = soup.find("table")
#
#         if not table:
#             return {"error": "Table not found"}
#
#         return {"html": str(table)}
#     except Exception as e:
#         return {"error": str(e)}
#
# # Run using: uvicorn nfl_api:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
from bs4 import BeautifulSoup

app = FastAPI()

# CORS settings
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_nfl_stats")
def get_nfl_stats(year: int = 2019):
    try:
        url = f"https://www.pro-football-reference.com/years/{year}/rushing.htm"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://www.google.com",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"id": "rushing"})

        if table is None:
            return {"error": "Table not found. Site structure may have changed."}

        df = pd.read_html(str(table))[0]
        df = df.dropna(how="all")
        data = df.to_dict(orient="records")

        return {"data": data}

    except requests.exceptions.RequestException as e:
        return {"error": f"Backend Error: {str(e)}"}
