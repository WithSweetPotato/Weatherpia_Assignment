# app.py
import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

############################################
# 1) Swagger UI 설정
############################################
SWAGGER_URL = '/apidocs'
API_URL = '/static/swagger.json'  # swagger.json 문서가 /static 에 있다고 가정
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Weatherpia Assignment REST API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


############################################
# 2) DB 연결
############################################
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',   # 본인의 MariaDB 호스트
        user='root',        # DB 유저
        password='0408',    # DB 패스워드
        db='members_db',    # DB 이름
        port=3306,          # MariaDB 포트 (기본 3306)
        charset='utf8',
        cursorclass=DictCursor
    )

############################################
# 3) HTML 페이지 라우트
############################################

# 3-1) 메인(회원 등록)
@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        return render_template('main.html')
    else:
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
                    return """
                    <script>
                    alert("이미 존재하는 회원 ID 입니다.");
                    history.back();
                    </script>
                    """

                # 신규 회원 등록
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

# 3-2) 회원 목록 조회 + 정렬 + 페이지네이션
@app.route('/members')
def get_members():
    """
    사용 예시:
      /members
      /members?page=2
      /members?sort=name&order=asc
      /members?sort=grade&order=desc&page=3
    등등
    """
    # 1) Query Param 파싱
    sort = request.args.get('sort', '')     # 'name' or 'grade' or ''
    order = request.args.get('order', '')   # 'asc' or 'desc' or ''
    page = request.args.get('page', 1, type=int)  # 페이지 번호 (기본 1)
    limit = 10  # 한 페이지에 보여줄 회원 수
    offset = (page - 1) * limit

    # 2) 정렬용 CASE WHEN 구문
    #    (DIA > PLATINUM > GOLD > SILVER > BRONZE)가 "높은 순",
    #    반대가 "낮은 순"
    grade_case_asc = """
        CASE grade
          WHEN 'BRONZE' THEN 1
          WHEN 'SILVER' THEN 2
          WHEN 'GOLD' THEN 3
          WHEN 'PLATINUM' THEN 4
          WHEN 'DIA' THEN 5
          ELSE 6
        END
    """
    grade_case_desc = """
        CASE grade
          WHEN 'DIA' THEN 1
          WHEN 'PLATINUM' THEN 2
          WHEN 'GOLD' THEN 3
          WHEN 'SILVER' THEN 4
          WHEN 'BRONZE' THEN 5
          ELSE 6
        END
    """

    # 3) 정렬 조건 만들기
    order_clause = "member_no DESC"  # 기본 정렬 (최근 생성 순)
    if sort == 'name':
        if order == 'asc':
            order_clause = "name ASC"
        elif order == 'desc':
            order_clause = "name DESC"
    elif sort == 'grade':
        if order == 'asc':
            order_clause = f"{grade_case_asc} ASC"
        elif order == 'desc':
            order_clause = f"{grade_case_desc} ASC"

    # 4) 전체 회원 수 구하기 (페이지네이션 계산)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_count FROM members")
            total_count = cursor.fetchone()['total_count']

            # 실제 회원 목록 쿼리
            sql = f"SELECT * FROM members ORDER BY {order_clause} LIMIT %s OFFSET %s"
            cursor.execute(sql, (limit, offset))
            members_list = cursor.fetchall()
    finally:
        conn.close()

    # 5) 페이지네이션 계산
    total_pages = (total_count // limit) + (1 if total_count % limit != 0 else 0)

    # 6) 템플릿으로 전달
    return render_template(
        'list.html',
        members=members_list,
        page=page,
        total_pages=total_pages,
        total_count=total_count,
        sort=sort,
        order=order
    )

# 3-3) 회원 수정
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

# 3-4) 회원 삭제
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


############################################
# 4) REST API (JSON)
############################################

@app.route('/api/members', methods=['GET'])
def api_get_all_members():
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
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # ID 중복 체크
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
                data.get('user_id'),
                data.get('password'),
                data.get('name', ''),
                data.get('nickname', ''),
                data.get('email', ''),
                data.get('grade', 'BRONZE')
            ))
            conn.commit()
            new_id = cursor.lastrowid
    finally:
        conn.close()

    return jsonify({"message": "신규 회원이 추가되었습니다.", "member_no": new_id}), 201

@app.route('/api/members/<int:member_no>', methods=['PUT'])
def api_update_member(member_no):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
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
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
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


############################################
# 5) Flask 실행
############################################
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
