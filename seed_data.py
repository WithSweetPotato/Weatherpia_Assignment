#100명 DB에 추가하는 코드

# seed_data.py
import random
import pymysql
from pymysql.cursors import DictCursor

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

def seed_members(num=100):
    """
    num 명수만큼 임의 회원을 DB에 삽입한다.
    """
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "함", "임"]
    first_names = ["상욱", "정수", "서영", "우솔", "학준", "시온", "가영", "현우", "영희", "철수"]

    grades = ["BRONZE", "SILVER", "GOLD", "PLATINUM", "DIA"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # (선택) 기존 dummy 데이터 삭제를 원하면 주석 해제
    # cursor.execute("DELETE FROM members WHERE user_id LIKE 'dummy%'")
    # conn.commit()

    for i in range(1, num+1):
        full_name = random.choice(last_names) + random.choice(first_names)
        user_id = f"dummy{i}"
        password = "1234"
        nickname = "닉네임" + str(i)
        email = f"dummy{i}@test.com"
        grade = random.choice(grades)

        sql_insert = """
        INSERT INTO members (user_id, password, name, nickname, email, grade)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql_insert, (user_id, password, full_name, nickname, email, grade))
        except Exception as e:
            print("Error inserting dummy data:", e)

    conn.commit()
    conn.close()
    print(f"{num}명의 회원 더미 데이터가 생성되었습니다.")

if __name__ == "__main__":
    seed_members(100)
