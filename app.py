# app.py
import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# -----------------------------
# 1) Swagger UI 설정
# -----------------------------
SWAGGER_URL = '/apidocs'  # Swagger UI에 접속할 URL prefix
API_URL = '/static/swagger.json'  # Swagger 문서(JSON) 파일 경로
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Weatherpia Assignment REST API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# -----------------------------
# 2) DB 연결 함수
# -----------------------------
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='0408',
        db='members_db',        
        port=3306,
        charset='utf8',
        cursorclass=DictCursor
    )

# -------------------------------------------------
# 3) 기존: HTML 화면 라우트 (main, /members, /update, /delete)
# -------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        return render_template('main.html')
    else:
        # 회원 등록 로직
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '')
        nickname = request.form.get('nickname', '')
        email = request.form.get('email', '')
        grade = request.form.get('grade', '')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 중복 체크
                sql_check = "SELECT COUNT(*) AS cnt FROM members WHERE user_id = %s"
                cursor.execute(sql_check, (user_id,))
                row = cursor.fetchone()
                if row['cnt'] > 0:
                    conn.close()
                    return """
                    <script>
                    alert("이미 존재하는 회원 ID 입니다.");
                    history.back();
                    </script>
                    """

                # 등록
                sql_insert = """
                INSERT INTO members (user_id, password, name, nickname, email, grade)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (user_id, password, name, nickname, email, grade))
                conn.commit()
        finally:
            conn.close()

        return """
        <script>
        alert("신규 회원이 추가되었습니다.");
        window.location.href = "/members";
        </script>
        """

@app.route('/members')
def get_members():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM members ORDER BY member_no DESC"
            cursor.execute(sql)
            members_list = cursor.fetchall()
    finally:
        conn.close()

    return render_template('list.html', members=members_list)

@app.route('/update/<int:member_no>', methods=['GET', 'POST'])
def update_member(member_no):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                sql_select = "SELECT * FROM members WHERE member_no = %s"
                cursor.execute(sql_select, (member_no,))
                user_data = cursor.fetchone()
                if not user_data:
                    return "존재하지 않는 회원입니다.", 404
                return render_template('update.html', user=user_data)
            else:
                user_id = request.form.get('user_id', '').strip()
                password = request.form.get('password', '')
                name = request.form.get('name', '')
                nickname = request.form.get('nickname', '')
                email = request.form.get('email', '')
                grade = request.form.get('grade', '')

                sql_update = """
                UPDATE members
                SET user_id=%s, password=%s, name=%s, nickname=%s, email=%s, grade=%s
                WHERE member_no=%s
                """
                cursor.execute(sql_update, (user_id, password, name, nickname, email, grade, member_no))
                conn.commit()
                return redirect(url_for('get_members'))
    finally:
        conn.close()

@app.route('/delete/<int:member_no>', methods=['POST'])
def delete_member(member_no):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql_delete = "DELETE FROM members WHERE member_no=%s"
            cursor.execute(sql_delete, (member_no,))
            conn.commit()
    finally:
        conn.close()

    return redirect(url_for('get_members'))

# -------------------------------------------------
# 4) 추가: REST API (JSON 응답) 라우트
# -------------------------------------------------

@app.route('/api/members', methods=['GET'])
def api_get_all_members():
    """
    GET /api/members
    - 모든 회원 목록 조회
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM members ORDER BY member_no DESC"
            cursor.execute(sql)
            rows = cursor.fetchall()
    finally:
        conn.close()

    return jsonify(rows)

@app.route('/api/members/<int:member_no>', methods=['GET'])
def api_get_member(member_no):
    """
    GET /api/members/<member_no>
    - 특정 회원 정보 조회
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM members WHERE member_no=%s"
            cursor.execute(sql, (member_no,))
            row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "Member not found"}), 404

    return jsonify(row)

@app.route('/api/members', methods=['POST'])
def api_create_member():
    """
    POST /api/members
    - 회원 생성
    JSON Body 예시:
    {
      "user_id": "testuser",
      "password": "1234",
      "name": "홍길동",
      "nickname": "길동이",
      "email": "hong@test.com",
      "grade": "silver"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    # 필수 값 체크 (간단 예시)
    if "user_id" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 중복 체크
            sql_check = "SELECT COUNT(*) AS cnt FROM members WHERE user_id = %s"
            cursor.execute(sql_check, (data['user_id'],))
            row = cursor.fetchone()
            if row['cnt'] > 0:
                return jsonify({"error": "이미 존재하는 회원 ID 입니다."}), 400

            sql_insert = """
            INSERT INTO members (user_id, password, name, nickname, email, grade)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (
                data['user_id'],
                data['password'],
                data.get('name', ''),
                data.get('nickname', ''),
                data.get('email', ''),
                data.get('grade', 'silver')
            ))
            conn.commit()
            new_id = cursor.lastrowid  # 방금 insert된 PK (member_no)
    finally:
        conn.close()

    return jsonify({"message": "신규 회원이 추가되었습니다.", "member_no": new_id}), 201

@app.route('/api/members/<int:member_no>', methods=['PUT'])
def api_update_member(member_no):
    """
    PUT /api/members/<member_no>
    - 회원 수정
    JSON Body 예시:
    {
      "user_id": "updated_user",
      "password": "abcd",
      "name": "김수정",
      "nickname": "수정이",
      "email": "update@test.com",
      "grade": "gold"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 해당 회원이 존재하는지 체크
            sql_select = "SELECT * FROM members WHERE member_no=%s"
            cursor.execute(sql_select, (member_no,))
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": "Member not found"}), 404

            sql_update = """
            UPDATE members
            SET user_id=%s, password=%s, name=%s, nickname=%s, email=%s, grade=%s
            WHERE member_no=%s
            """
            cursor.execute(sql_update, (
                data.get('user_id', row['user_id']),
                data.get('password', row['password']),
                data.get('name', row['name']),
                data.get('nickname', row['nickname']),
                data.get('email', row['email']),
                data.get('grade', row['grade']),
                member_no
            ))
            conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "회원 정보가 수정되었습니다."}), 200

@app.route('/api/members/<int:member_no>', methods=['DELETE'])
def api_delete_member(member_no):
    """
    DELETE /api/members/<member_no>
    - 특정 회원 삭제
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 존재 여부 확인
            sql_select = "SELECT * FROM members WHERE member_no=%s"
            cursor.execute(sql_select, (member_no,))
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": "Member not found"}), 404

            sql_delete = "DELETE FROM members WHERE member_no=%s"
            cursor.execute(sql_delete, (member_no,))
            conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "회원이 삭제되었습니다."}), 200

# -------------------------------------------------
# 5) Flask 실행
# -------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
