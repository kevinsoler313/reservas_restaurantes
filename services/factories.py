from models import User, db

class UserFactory:
    @staticmethod
    def create_user(role: str, email: str, password: str) -> User:
        role = role.upper()
        if role not in ('CLIENTE', 'ADMIN'):
            raise ValueError('Rol desconocido')
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
