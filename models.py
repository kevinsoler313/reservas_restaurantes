# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'CLIENTE' o 'ADMIN'

    def set_password(self, password: str):
        """Guarda el hash de la contraseña (no la contraseña en texto claro)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica una contraseña con el hash guardado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    tables = db.relationship('Table', backref='restaurant', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Restaurant {self.nombre}>"

class Table(db.Model):
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    def __repr__(self):
        return f"<Table {self.numero} cap={self.capacidad}>"

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    num_personas = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default='PENDIENTE')  # PENDIENTE, ACEPTADA, CANCELADA

    user = db.relationship('User')
    restaurant = db.relationship('Restaurant')
    table = db.relationship('Table')

    def __repr__(self):
        return f"<Reservation {self.id} {self.fecha_hora} personas={self.num_personas} estado={self.estado}>"
