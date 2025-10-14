from models import User

class AuthService:
    @staticmethod
    def authenticate(email: str, password: str):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
