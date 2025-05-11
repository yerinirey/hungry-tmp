import requests
from flask import current_app
from typing import List, Dict

def fetch_from_naver(board) -> List[Dict]:

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": current_app.config['NAVER_CLIENT_ID'],
        "X-Naver-Client-Secret":  current_app.config['NAVER_CLIENT_SECRET'],
    }
    query_dict = {
        'cafe': '숭실대학교 카페',
        'restaurant': '숭실대학교 음식',
        'free': '상도 고기'
    }
    query = query_dict[board]
    print(query)
    #query = query or "숭실대학교 음식"

    params = {
        "query": query,
        "display": 10,
    }

    resp = requests.get(url, headers=headers, params=params)
    print(resp)
    resp.raise_for_status()
    items = resp.json().get("items", [])

    restaurants = [
        {
            "name":        item.get("title", "").replace("<b>", "").replace("</b>", ""),
            "category":    board,
            "address":     item.get("roadAddress") or item.get("address"),
            "latitude":        item.get("mapx"),
            "longitude":        item.get("mapy"),
            "phone":   item.get("telephone") or "",
            
        }
        for item in items
    ]
    for r in restaurants:
        print(r)
    return restaurants