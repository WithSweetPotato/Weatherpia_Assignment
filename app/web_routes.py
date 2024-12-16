from flask import Blueprint, render_template
from app.models import Member

# 웹페이지 라우트를 위한 Blueprint
web_bp = Blueprint('web', __name__)

@web_bp.route('/members/edit/<int:id>')
def edit_member(id):
    """회원 수정 페이지"""
    # 데이터베이스에서 회원 정보 조회
    connection = current_app.db_connection
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE id = %s", (id,))
    member = cursor.fetchone()
    cursor.close()

    if not member:
        return "해당 회원을 찾을 수 없습니다.", 404

    # HTML 페이지 렌더링
    return render_template(
        'edit_member.html',
        member=member  # 회원 정보를 템플릿에 전달
    )
