from app import create_app
from models import db, User, Restaurant, Table
from services.factories import UserFactory

app = create_app()
app.app_context().push()

# Crear tablas
db.create_all()

# Crear usuario admin por defecto (si no existe) usando Factory Pattern
if not User.query.filter_by(email='admin@example.com').first():
    try:
        # ✅ Uso del patrón Factory para crear usuario
        admin_user = UserFactory.create_user('ADMIN', 'admin@example.com', 'admin123')
        print('✅ Admin creado usando Factory Pattern: admin@example.com / admin123')
    except Exception as e:
        print('❌ Error creando admin:', e)

# Crear restaurante de ejemplo (si no existe)
if not Restaurant.query.first():
    r = Restaurant(nombre='La Parrilla', direccion='Calle 123', descripcion='Restaurante de prueba')
    db.session.add(r)
    db.session.commit()
    
    # Crear algunas mesas
    db.session.add(Table(numero=1, capacidad=2, restaurant_id=r.id))
    db.session.add(Table(numero=2, capacidad=4, restaurant_id=r.id))
    db.session.add(Table(numero=3, capacidad=6, restaurant_id=r.id))
    db.session.commit()
    print('✅ Restaurante de ejemplo creado con mesas')

print('\n' + '='*60)
print('🎉 Base de datos inicializada correctamente')
print('='*60)
print('\n📝 Credenciales de acceso:')
print('   Email:    admin@example.com')
print('   Password: admin123')
print('\n💡 Patrones implementados:')
print('   ✅ Factory Pattern: UserFactory (factories.py)')
print('   ✅ Builder Pattern: ReservationBuilder (reservation_service.py)')
print('='*60 + '\n')