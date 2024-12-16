from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_migrate import Migrate
from flask_cors import CORS
import os  # 환경 변수 사용을 위한 모듈

# Extensions 초기화
db = SQLAlchemy()
migrate = Migrate()
api = Api(version='1.0', title='Member Management API', description='API for managing members')

def create_app():
    """Flask 애플리케이션을 생성하고 구성합니다."""
    app = Flask(__name__)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 
        'mariadb+mariadbconnector://root:0408@localhost/member_db'  # 기본값 설정
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Secret Key 설정
    app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

    # Extensions 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # 모든 요청 허용 (특정 도메인 허용은 필요 시 수정 가능)
    api.init_app(app)

    # Register routes (API 엔드포인트 등록)
    from app.routes import api_ns
    api.add_namespace(api_ns, path='/api/members')

    return app
