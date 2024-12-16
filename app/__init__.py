from flask import Flask
from flask_restx import Api
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os
from pathlib import Path

# .env 파일 로드
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)

api = Api(version='1.0', title='Member Management API', description='API for managing members')

def create_db_connection():
    """MySQL 데이터베이스 연결 생성"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '0408'),
            database=os.getenv('DB_NAME', 'member_db'),
            port=3306,
            charset='utf8mb4',  # Character set 설정
            collation='utf8mb4_general_ci'  # Collation 명시
        )
        print("Database connection successful")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise RuntimeError("Database connection failed") from err

def create_app():
    """Flask 애플리케이션을 생성하고 구성합니다."""
    app = Flask(__name__)

    # Secret Key 설정
    app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')  # .env에서 로드

    # Extensions 초기화
    CORS(app)  # 모든 요청 허용
    api.init_app(app)

    # Database 연결 초기화
    app.db_connection = create_db_connection()

    # DB 연결 테스트
    if not app.db_connection.is_connected():
        raise RuntimeError("Database is not connected. Please check your settings.")

    # Register API routes (REST API 엔드포인트 등록)
    from app.routes import api_ns
    api.add_namespace(api_ns, path='/api/members')

    # Register web routes (HTML 페이지 라우트 등록)
    from app.web_routes import web_bp
    app.register_blueprint(web_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
