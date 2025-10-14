from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import Config
from models import db, User, Restaurant, Table, Reservation
from services.auth_service import AuthService
from services.reservation_service import ReservationBuilder, ReservationService
from datetime import datetime, timedelta
from functools import wraps

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

app = create_app()

@app.context_processor
def inject_now():
    """Inyecta la variable 'now' en todas las plantillas Jinja2"""
    return {'now': datetime.now()}
# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rutas de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'ADMIN':
            flash('Acceso restringido: solo administradores', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    restaurantes = Restaurant.query.all()
    return render_template('index.html', restaurantes=restaurantes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = AuthService.authenticate(email, password)
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            flash('¡Bienvenido! Has iniciado sesión correctamente', 'success')
            if user.role == 'ADMIN':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('index'))
        flash('Credenciales inválidas. Por favor, verifica tu email y contraseña', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'CLIENTE')

        # Validaciones
        if not email or not password:
            flash('Email y contraseña son obligatorios', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
            return render_template('register.html')

        # Validar si ya existe el usuario
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Este email ya está registrado. Intenta con otro', 'danger')
            return render_template('register.html')

        # Crear y guardar el nuevo usuario
        new_user = User(email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('¡Cuenta creada exitosamente! Ya puedes iniciar sesión', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

@app.route('/perfil')
@login_required
def perfil():
    user = User.query.get(session['user_id'])
    reservas = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.fecha_hora.desc()).all()
    return render_template('perfil.html', user=user, reservas=reservas)

@app.route('/perfil/editar', methods=['POST'])
@login_required
def editar_perfil():
    user = User.query.get(session['user_id'])
    email = request.form.get('email')
    password_actual = request.form.get('password_actual')
    password_nueva = request.form.get('password_nueva')

    if email and email != user.email:
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Este email ya está en uso', 'danger')
            return redirect(url_for('perfil'))
        user.email = email
        session['email'] = email

    if password_nueva:
        if not password_actual or not user.check_password(password_actual):
            flash('Contraseña actual incorrecta', 'danger')
            return redirect(url_for('perfil'))
        user.set_password(password_nueva)
        flash('Contraseña actualizada correctamente', 'success')

    db.session.commit()
    flash('Perfil actualizado correctamente', 'success')
    return redirect(url_for('perfil'))

@app.route("/reserve", methods=["GET", "POST"])
@login_required
def reserve():
    from datetime import datetime
    restaurantes = Restaurant.query.all()
    mesas_disponibles = []
    selected_restaurant = None
    fecha_hora = None

    if request.method == "POST":
        selected_restaurant = request.form.get("restaurant_id")
        fecha_hora_str = request.form.get("fecha_hora")

        if not selected_restaurant or not fecha_hora_str:
            flash("Por favor selecciona un restaurante y una fecha válida", "warning")
            return render_template(
                "reserva_form.html",
                restaurantes=restaurantes,
                mesas_disponibles=mesas_disponibles,
                selected_restaurant=selected_restaurant,
                fecha_hora=fecha_hora,
                now=datetime.now()
            )

        # Convertir fecha y definir duración de la reserva
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora_str)
        except:
            flash("Formato de fecha inválido", "danger")
            return redirect(url_for('reserve'))

        # Validar que la fecha no sea en el pasado
        if fecha_hora < datetime.now():
            flash("No puedes hacer reservas en el pasado", "warning")
            return render_template(
                "reserva_form.html",
                restaurantes=restaurantes,
                mesas_disponibles=mesas_disponibles,
                selected_restaurant=int(selected_restaurant),
                fecha_hora=fecha_hora_str
            )

        duracion = timedelta(hours=2)
        fecha_fin = fecha_hora + duracion

        # Buscar mesas del restaurante
        mesas = Table.query.filter_by(restaurant_id=selected_restaurant).all()

        mesas_disponibles = []
        for mesa in mesas:
            conflicto = Reservation.query.filter(
                Reservation.table_id == mesa.id,
                Reservation.fecha_hora < fecha_fin,
                (Reservation.fecha_hora + timedelta(hours=2)) > fecha_hora,
                Reservation.estado != 'CANCELADA'
            ).first()
            if not conflicto:
                mesas_disponibles.append(mesa)

        mesa_id = request.form.get("mesa_id")
        num_personas = request.form.get("num_personas")

        # Si ya eligió una mesa (segunda parte del formulario)
        if mesa_id and num_personas:
            user_id = session.get("user_id")
            mesa_id = int(mesa_id)
            selected_restaurant = int(selected_restaurant)
            num_personas = int(num_personas)

            # Validar capacidad de la mesa
            mesa = Table.query.get(mesa_id)
            if mesa.capacidad < num_personas:
                flash(f"Esta mesa tiene capacidad para {mesa.capacidad} personas. Selecciona otra mesa", "warning")
                return render_template(
                    "reserva_form.html",
                    restaurantes=restaurantes,
                    mesas_disponibles=mesas_disponibles,
                    selected_restaurant=selected_restaurant,
                    fecha_hora=fecha_hora_str,
                    now=datetime.now()
                )

            # Buscar todas las reservas activas de esa mesa
            reservas_existentes = Reservation.query.filter(
                Reservation.table_id == mesa_id,
                Reservation.estado != 'CANCELADA'
            ).all()

            # Verificar si alguna se cruza con la nueva
            hay_conflicto = False
            for reserva in reservas_existentes:
                inicio_existente = reserva.fecha_hora
                fin_existente = inicio_existente + timedelta(hours=2)
                if fecha_hora < fin_existente and fecha_fin > inicio_existente:
                    hay_conflicto = True
                    break

            if hay_conflicto:
                flash("Lo sentimos, esa mesa ya está reservada en ese horario", "danger")
                return render_template(
                    "reserva_form.html",
                    restaurantes=restaurantes,
                    mesas_disponibles=mesas_disponibles,
                    selected_restaurant=selected_restaurant,
                    fecha_hora=fecha_hora_str
                )

            # Crear nueva reserva
            nueva_reserva = Reservation(
                user_id=user_id,
                restaurant_id=selected_restaurant,
                table_id=mesa_id,
                fecha_hora=fecha_hora,
                num_personas=num_personas,
                estado="PENDIENTE"
            )
            db.session.add(nueva_reserva)
            db.session.commit()
            flash("¡Reserva confirmada con éxito!", "success")
            return redirect(url_for("perfil"))

        # Si no hay mesas disponibles
        if not mesas_disponibles:
            flash("No hay mesas disponibles en ese horario para este restaurante", "warning")

        return render_template(
            "reserva_form.html",
            restaurantes=restaurantes,
            mesas_disponibles=mesas_disponibles,
            selected_restaurant=int(selected_restaurant),
            fecha_hora=fecha_hora_str,
            now=datetime.now()
        )

    # GET – primera vez
    return render_template(
        "reserva_form.html",
        restaurantes=restaurantes,
        mesas_disponibles=mesas_disponibles,
        now=datetime.now()
    )

@app.route('/reserva/cancelar/<int:reserva_id>', methods=['POST'])
@login_required
def cancelar_reserva(reserva_id):
    reserva = Reservation.query.get_or_404(reserva_id)
    
    # Verificar que la reserva pertenece al usuario
    if reserva.user_id != session['user_id'] and session.get('role') != 'ADMIN':
        flash('No tienes permiso para cancelar esta reserva', 'danger')
        return redirect(url_for('perfil'))
    
    reserva.estado = 'CANCELADA'
    db.session.commit()
    flash('Reserva cancelada correctamente', 'info')
    
    if session.get('role') == 'ADMIN':
        return redirect(url_for('admin_panel'))
    return redirect(url_for('perfil'))

# ============ RUTAS DE ADMINISTRACIÓN ============

@app.route('/admin')
@admin_required
def admin_panel():
    reservas = Reservation.query.order_by(Reservation.fecha_hora.desc()).all()
    restaurantes = Restaurant.query.all()
    usuarios = User.query.all()
    
    # Estadísticas
    total_reservas = Reservation.query.count()
    reservas_pendientes = Reservation.query.filter_by(estado='PENDIENTE').count()
    total_usuarios = User.query.count()
    total_restaurantes = Restaurant.query.count()
    
    return render_template('admin_panel.html', 
                         reservas=reservas,
                         restaurantes=restaurantes,
                         usuarios=usuarios,
                         total_reservas=total_reservas,
                         reservas_pendientes=reservas_pendientes,
                         total_usuarios=total_usuarios,
                         total_restaurantes=total_restaurantes)

@app.route('/admin/reservas/eliminar/<int:reserva_id>', methods=['POST'])
@admin_required
def eliminar_reserva(reserva_id):
    reserva = Reservation.query.get_or_404(reserva_id)
    db.session.delete(reserva)
    db.session.commit()
    flash(f'Reserva #{reserva.id} eliminada correctamente', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/reservas/actualizar/<int:reserva_id>', methods=['POST'])
@admin_required
def actualizar_reserva(reserva_id):
    reserva = Reservation.query.get_or_404(reserva_id)
    estado = request.form.get('estado')
    if estado in ['PENDIENTE', 'ACEPTADA', 'CANCELADA']:
        reserva.estado = estado
        db.session.commit()
        flash(f'Reserva actualizada a {estado}', 'success')
    return redirect(url_for('admin_panel'))

# ============ GESTIÓN DE RESTAURANTES ============

@app.route('/admin/restaurantes')
@admin_required
def admin_restaurantes():
    restaurantes = Restaurant.query.all()
    return render_template('admin_restaurantes.html', restaurantes=restaurantes)

@app.route('/admin/restaurantes/crear', methods=['GET', 'POST'])
@admin_required
def crear_restaurante():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre del restaurante es obligatorio', 'danger')
            return render_template('crear_restaurante.html')
        
        nuevo_restaurante = Restaurant(
            nombre=nombre,
            direccion=direccion,
            descripcion=descripcion
        )
        db.session.add(nuevo_restaurante)
        db.session.commit()
        
        flash(f'Restaurante "{nombre}" creado exitosamente', 'success')
        return redirect(url_for('admin_restaurantes'))
    
    return render_template('crear_restaurante.html')

@app.route('/admin/restaurantes/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_restaurante(id):
    restaurante = Restaurant.query.get_or_404(id)
    
    if request.method == 'POST':
        restaurante.nombre = request.form.get('nombre')
        restaurante.direccion = request.form.get('direccion')
        restaurante.descripcion = request.form.get('descripcion')
        
        db.session.commit()
        flash(f'Restaurante "{restaurante.nombre}" actualizado correctamente', 'success')
        return redirect(url_for('admin_restaurantes'))
    
    return render_template('editar_restaurante.html', restaurante=restaurante)

@app.route('/admin/restaurantes/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_restaurante(id):
    restaurante = Restaurant.query.get_or_404(id)
    nombre = restaurante.nombre
    db.session.delete(restaurante)
    db.session.commit()
    flash(f'Restaurante "{nombre}" eliminado correctamente', 'success')
    return redirect(url_for('admin_restaurantes'))

# ============ GESTIÓN DE MESAS ============

@app.route('/admin/restaurantes/<int:restaurant_id>/mesas')
@admin_required
def admin_mesas(restaurant_id):
    restaurante = Restaurant.query.get_or_404(restaurant_id)
    mesas = Table.query.filter_by(restaurant_id=restaurant_id).order_by(Table.numero).all()
    return render_template('admin_mesas.html', restaurante=restaurante, mesas=mesas)

@app.route('/admin/restaurantes/<int:restaurant_id>/mesas/crear', methods=['POST'])
@admin_required
def crear_mesa(restaurant_id):
    numero = request.form.get('numero', type=int)
    capacidad = request.form.get('capacidad', type=int)
    
    if not numero or not capacidad:
        flash('Número y capacidad son obligatorios', 'danger')
        return redirect(url_for('admin_mesas', restaurant_id=restaurant_id))
    
    # Verificar que no exista una mesa con ese número
    existing = Table.query.filter_by(restaurant_id=restaurant_id, numero=numero).first()
    if existing:
        flash(f'Ya existe una mesa con el número {numero}', 'danger')
        return redirect(url_for('admin_mesas', restaurant_id=restaurant_id))
    
    nueva_mesa = Table(
        numero=numero,
        capacidad=capacidad,
        restaurant_id=restaurant_id
    )
    db.session.add(nueva_mesa)
    db.session.commit()
    
    flash(f'Mesa #{numero} creada exitosamente', 'success')
    return redirect(url_for('admin_mesas', restaurant_id=restaurant_id))

@app.route('/admin/mesas/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_mesa(id):
    mesa = Table.query.get_or_404(id)
    restaurant_id = mesa.restaurant_id
    numero = mesa.numero
    
    # Verificar si hay reservas activas
    reservas_activas = Reservation.query.filter_by(table_id=id, estado='PENDIENTE').count()
    if reservas_activas > 0:
        flash(f'No se puede eliminar la mesa #{numero} porque tiene {reservas_activas} reservas activas', 'danger')
        return redirect(url_for('admin_mesas', restaurant_id=restaurant_id))
    
    db.session.delete(mesa)
    db.session.commit()
    flash(f'Mesa #{numero} eliminada correctamente', 'success')
    return redirect(url_for('admin_mesas', restaurant_id=restaurant_id))

# ============ GESTIÓN DE USUARIOS ============

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    users = User.query.all()
    return render_template('admin_usuarios.html', users=users)

@app.route('/admin/usuarios/eliminar/<int:user_id>', methods=['POST'])
@admin_required
def eliminar_usuario(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == 'ADMIN':
        flash('No se pueden eliminar otros administradores', 'warning')
        return redirect(url_for('admin_usuarios'))

    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {email} eliminado correctamente', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/restaurante/<int:id>')
def detalle_restaurante(id):
    restaurante = Restaurant.query.get_or_404(id)
    mesas = Table.query.filter_by(restaurant_id=id).all()
    return render_template('detalle_restaurante.html', restaurante=restaurante, mesas=mesas)

if __name__ == '__main__':
    app.run(debug=True)