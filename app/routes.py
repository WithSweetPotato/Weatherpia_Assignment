from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from app.models import db, Member

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

@api_ns.route('/')
class MemberList(Resource):
    @api_ns.doc('get_members')
    def get(self):
        """모든 회원 조회"""
        members = Member.query.all()
        return jsonify([member.to_dict() for member in members])

    @api_ns.expect(member_model)
    @api_ns.doc('create_member')
    def post(self):
        """회원 추가"""
        data = request.json
        if Member.query.filter_by(user_id=data['user_id']).first():
            return {"message": "이미 존재하는 회원 ID입니다."}, 400

        new_member = Member(
            user_id=data['user_id'],
            password=data['password'],
            name=data['name'],
            nickname=data['nickname'],
            email=data['email'],
            grade=data['grade']
        )
        db.session.add(new_member)
        db.session.commit()
        return {"message": "회원이 성공적으로 추가되었습니다."}, 201

@api_ns.route('/<int:id>')
class Member(Resource):
    @api_ns.doc('get_member')
    def get(self, id):
        """특정 회원 조회"""
        member = Member.query.get_or_404(id)
        return jsonify(member.to_dict())

    @api_ns.expect(member_model)
    @api_ns.doc('update_member')
    def put(self, id):
        """회원 정보 수정"""
        data = request.json
        member = Member.query.get_or_404(id)

        member.user_id = data['user_id']
        member.password = data['password']
        member.name = data['name']
        member.nickname = data['nickname']
        member.email = data['email']
        member.grade = data['grade']

        db.session.commit()
        return {"message": "회원 정보가 성공적으로 수정되었습니다."}

    @api_ns.doc('delete_member')
    def delete(self, id):
        """회원 삭제"""
        member = Member.query.get_or_404(id)
        db.session.delete(member)
        db.session.commit()
        return {"message": "회원이 성공적으로 삭제되었습니다."}
