from app import create_app
from models import db, User, Restaurant, Table
from services.factories import UserFactory

app = create_app()
app.app_context().push()

# Crear tablas
db.create_all()

# Crear usuario admin por defecto (si no existe)
if not User.query.filter_by(email='admin@example.com').first():
    try:
        UserFactory.create_user('ADMIN', 'admin@example.com', 'admin123')
        print('Admin creado: admin@example.com / admin123')
    except Exception as e:
        print('Error creando admin:', e)

# Crear restaurante de ejemplo (si no existe)
if not Restaurant.query.first():
    r = Restaurant(nombre='La Parrilla', direccion='Calle 123', descripcion='Restaurante de prueba')
    db.session.add(r)
    db.session.commit()
    # crear algunas mesas
    db.session.add(Table(numero=1, capacidad=2, restaurant_id=r.id))
    db.session.add(Table(numero=2, capacidad=4, restaurant_id=r.id))
    db.session.add(Table(numero=3, capacidad=6, restaurant_id=r.id))
    db.session.commit()
    print('Restaurante de ejemplo creado con mesas')
