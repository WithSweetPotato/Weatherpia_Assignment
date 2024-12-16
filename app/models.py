from app import db

class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    grade = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "password": self.password,
            "name": self.name,
            "nickname": self.nickname,
            "email": self.email,
            "grade": self.grade
        }
