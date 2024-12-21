# app.py
import pymysql
from flask import Flask, render_template, request, redirect, url_for
from pymysql.cursors import DictCursor

app = Flask(__name__)

# -----------------------------
# 데이터베이스 연결 함수
# -----------------------------
def get_db_connection():
    """
    MariaDB 연결: 본인의 환경에 맞춰 host, user, password, db, port 등을 수정하세요.
    """
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='0408',
        db='members_db',        # 생성한 DB 이름
        port=3306,              # MariaDB 포트 (기본 3306)
        charset='utf8',
        cursorclass=DictCursor
    )


# -----------------------------
# 메인 페이지(회원 등록)
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        # templates/main.html 렌더링
        return render_template('main.html')
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '')
        nickname = request.form.get('nickname', '')
        email = request.form.get('email', '')
        grade = request.form.get('grade', '')

        # DB 연결
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # ID 중복 체크 (UNIQUE Key이므로 에러가 날 수도 있지만, 여기서는 사전 체크)
                sql_check = "SELECT COUNT(*) AS cnt FROM members WHERE user_id = %s"
                cursor.execute(sql_check, (user_id,))
                row = cursor.fetchone()
                
                if row['cnt'] > 0:
                    # 이미 존재한다면 팝업 후, 메인 페이지로 이동
                    conn.close()
                    return """
                    <script>
                    alert("이미 존재하는 회원 ID 입니다.");
                    history.back();
                    </script>
                    """
                
                # 회원 등록
                sql_insert = """
                INSERT INTO members (user_id, password, name, nickname, email, grade)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (user_id, password, name, nickname, email, grade))
                conn.commit()

        finally:
            conn.close()

        # 신규 회원 등록 성공
        return """
        <script>
        alert("신규 회원이 추가되었습니다.");
        window.location.href = "/members";
        </script>
        """


# -----------------------------
# 회원 목록 조회
# -----------------------------
@app.route('/members')
def get_members():
    """
    회원 전체 목록 조회 (간단히 페이지네이션 생략 or 구현)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM members ORDER BY member_no DESC"
            cursor.execute(sql)
            members_list = cursor.fetchall()
    finally:
        conn.close()

    return render_template('list.html', members=members_list)


# -----------------------------
# 회원 수정
# -----------------------------
@app.route('/update/<int:member_no>', methods=['GET', 'POST'])
def update_member(member_no):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 수정 대상 회원 정보 조회
            if request.method == 'GET':
                sql_select = "SELECT * FROM members WHERE member_no = %s"
                cursor.execute(sql_select, (member_no,))
                user_data = cursor.fetchone()
                if not user_data:
                    conn.close()
                    return "존재하지 않는 회원입니다.", 404

                return render_template('update.html', user=user_data)

            # POST(수정 폼 전송)
            if request.method == 'POST':
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


# -----------------------------
# 회원 삭제
# -----------------------------
@app.route('/delete/<int:member_no>', methods=['POST'])
def delete_member(member_no):
    """
    회원 삭제 후 목록 페이지로 이동
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql_delete = "DELETE FROM members WHERE member_no=%s"
            cursor.execute(sql_delete, (member_no,))
            conn.commit()
    finally:
        conn.close()

    return redirect(url_for('get_members'))


# -----------------------------
# Flask 실행
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
