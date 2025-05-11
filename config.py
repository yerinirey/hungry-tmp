import os

class Config:
    BASE_DIR = os.path.dirname(__file__)
    DB_NAME = "hungry_aix"
    # 데이터베이스 접속 주소
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:1234@localhost/{DB_NAME}'
    # SQLAlchemy의 이벤트를 처리하는 옵션
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'dev'

    # 네이버 지역 검색 API 인증 정보
    NAVER_CLIENT_ID = 'YOUR_CLIENT_ID'
    NAVER_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
    NAVER_API_URL = 'https://openapi.naver.com/v1/search/local.json'
