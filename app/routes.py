from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import mysql.connector

api_ns = Namespace('members', description='Member operations')

# Request and Response Model
member_model = api_ns.model('Member', {
    'user_id': fields.String(required=True, description='The unique ID of the member'),
    'password': fields.String(required=True, description='The password of the member'),
    'name': fields.String(required=True, description='The name of the member'),
    'nickname': fields.String(required=True, description='The nickname of the member'),
    'email': fields.String(required=True, description='The email of the member'),
    'grade': fields.String(required=True, description='The grade of the member'),
})

def get_db_cursor():
    """데이터베이스 연결에서 커서 반환"""
    connection = current_app.db_connection
    return connection.cursor(dictionary=True)

@api_ns.route('/')
class MemberList(Resource):
    @api_ns.doc('get_members')
    def get(self):
        """모든 회원 조회"""
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        cursor.close()
        return {"data": members, "message": "success"}, 200

    @api_ns.expect(member_model)
    @api_ns.doc('create_member')
    def post(self):
        """회원 추가"""
        data = request.get_json()
        if not data:
            return {"message": "잘못된 데이터 형식입니다. JSON 형식이어야 합니다."}, 400

        if not data.get('user_id') or not data.get('email'):
            return {"message": "user_id와 email은 필수 항목입니다."}, 400

        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM members WHERE user_id = %s", (data['user_id'],))
        if cursor.fetchone():
            cursor.close()
            return {"message": f"이미 존재하는 회원 ID입니다: {data['user_id']}"}, 400

        query = """
            INSERT INTO members (user_id, password, name, nickname, email, grade)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['user_id'],
            data['password'],
            data['name'],
            data['nickname'],
            data['email'],
            data['grade']
        ))
        current_app.db_connection.commit()
        cursor.close()
        return {"message": "회원이 성공적으로 추가되었습니다."}, 201

@api_ns.route('/<int:id>')
class Member(Resource):
    @api_ns.doc('get_member')
    def get(self, id):
        """특정 회원 조회"""
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM members WHERE id = %s", (id,))
        member = cursor.fetchone()
        cursor.close()
        if not member:
            return {"message": f"ID {id}에 해당하는 회원을 찾을 수 없습니다."}, 404
        return {"data": member, "message": "success"}, 200

    @api_ns.expect(member_model)
    @api_ns.doc('update_member')
    def put(self, id):
        """회원 정보 수정"""
        data = request.get_json()
        if not data:
            return {"message": "잘못된 데이터 형식입니다. JSON 형식이어야 합니다."}, 400

        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM members WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return {"message": f"ID {id}에 해당하는 회원을 찾을 수 없습니다."}, 404

        query = """
            UPDATE members
            SET user_id = %s, password = %s, name = %s, nickname = %s, email = %s, grade = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            data['user_id'],
            data['password'],
            data['name'],
            data['nickname'],
            data['email'],
            data['grade'],
            id
        ))
        current_app.db_connection.commit()
        cursor.close()
        return {"message": "회원 정보가 성공적으로 수정되었습니다."}, 200

    @api_ns.doc('delete_member')
    def delete(self, id):
        """회원 삭제"""
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM members WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return {"message": f"ID {id}에 해당하는 회원을 찾을 수 없습니다."}, 404

        cursor.execute("DELETE FROM members WHERE id = %s", (id,))
        current_app.db_connection.commit()
        cursor.close()
        return {"message": f"회원(ID: {id})이 성공적으로 삭제되었습니다."}, 200
