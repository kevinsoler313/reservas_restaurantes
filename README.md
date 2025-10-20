# 🍽️ RestauBook - Sistema de Gestión de Reservas

Sistema completo de gestión de reservas para restaurantes desarrollado con Flask, con diseño moderno y responsivo.

## Características Principales

### Para Clientes
- **Registro e inicio de sesión seguro**
- **Sistema de reservas intuitivo** con selección de fecha, hora y mesa
- **Perfil de usuario** con gestión de reservas
- **Notificaciones en tiempo real** de confirmaciones y cambios
- **Diseño 100% responsivo** para móviles, tablets y desktop

### Para Administradores
- **CRUD completo de restaurantes** (Crear, Leer, Actualizar, Eliminar)
- **Gestión de mesas** por restaurante
- **Panel de administración** con estadísticas en tiempo real
- **Gestión de usuarios** del sistema
- **Control de reservas** con actualización de estados
- **Dashboard intuitivo** con métricas clave

### Características Técnicas
- Diseño moderno con **Tailwind CSS**
- Animaciones y transiciones suaves
- Autenticación segura con **hash de contraseñas**
- Validaciones robustas en frontend y backend
- Base de datos **SQLite** fácil de configurar
- Arquitectura modular y escalable

## Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos e inicializar

```bash
python create_db.py
```

Este comando creará:
- La base de datos SQLite (`reservas.db`)
- Un usuario administrador por defecto
- Un restaurante de ejemplo con mesas

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://127.0.0.1:5000**

## Credenciales por Defecto

### Administrador
- **Email:** admin@example.com
- **Contraseña:** admin123

## Estructura del Proyecto

```
restaurant-booking/
│
├── app.py                      # Aplicación principal Flask
├── config.py                   # Configuraciones
├── models.py                   # Modelos de base de datos
├── create_db.py               # Script de inicialización
├── requirements.txt           # Dependencias
│
├── services/                  # Lógica de negocio
│   ├── __init__.py
│   ├── auth_service.py       # Servicio de autenticación
│   ├── factories.py          # Factories para creación
│   └── reservation_service.py # Servicio de reservas
│
└── templates/                 # Templates HTML
    ├── base.html             # Template base
    ├── index.html            # Página principal
    ├── login.html            # Login
    ├── register.html         # Registro
    ├── perfil.html           # Perfil usuario
    ├── reserva_form.html     # Formulario reservas
    ├── detalle_restaurante.html
    ├── admin_panel.html      # Panel admin
    ├── admin_restaurantes.html
    ├── admin_mesas.html
    ├── admin_usuarios.html
    ├── crear_restaurante.html
    └── editar_restaurante.html
```

## Uso del Sistema

### Como Cliente

1. **Registro:**
   - Click en "Registrarse"
   - Completa el formulario con email y contraseña
   - Selecciona rol "Cliente"

2. **Hacer una Reserva:**
   - Navega a "Reservar"
   - Selecciona un restaurante
   - Elige fecha y hora
   - Selecciona una mesa disponible
   - Confirma tu reserva

3. **Gestionar Reservas:**
   - Ve a "Mi Perfil"
   - Visualiza todas tus reservas
   - Cancela si es necesario

### Como Administrador

1. **Gestionar Restaurantes:**
   - Accede al "Panel de Administración"
   - Click en "Gestionar Restaurantes"
   - Crear, editar o eliminar restaurantes

2. **Gestionar Mesas:**
   - Desde la lista de restaurantes
   - Click en "Gestionar Mesas"
   - Agregar o eliminar mesas según necesidad

3. **Gestionar Reservas:**
   - Panel principal muestra todas las reservas
   - Cambiar estados: PENDIENTE → ACEPTADA → CANCELADA
   - Eliminar reservas si es necesario

4. **Gestionar Usuarios:**
   - Click en "Gestionar Usuarios"
   - Ver todos los usuarios registrados
   - Eliminar usuarios (excepto administradores)

## Configuración Avanzada

### Cambiar la Clave Secreta

En `config.py`, modifica:
```python
SECRET_KEY = 'tu_clave_secreta_aqui'
```

O usa variables de entorno:
```bash
export SECRET_KEY='tu_clave_super_secreta'
```

### Base de Datos

Por defecto usa SQLite. Para cambiar a PostgreSQL u otra:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://usuario:password@localhost/dbname'
```

## Características de Diseño

- **Paleta de colores:** Gradientes púrpura modernos
- **Iconografía:** Font Awesome 6.4.0
- **Tipografía:** Inter (Google Fonts)
- **Framework CSS:** Tailwind CSS vía CDN
- **Efectos:** Animaciones fade-in, hover effects, shadows
- **Responsive:** Mobile-first design

## Notas Importantes

- **Duración de reservas:** Todas las reservas tienen 2 horas de duración
- **Conflictos:** El sistema valida automáticamente conflictos de horarios
- **Mesas:** No se pueden eliminar mesas con reservas activas
- **Administradores:** No se pueden eliminar cuentas de administrador

## Solución de Problemas

### Error al ejecutar create_db.py
```bash
# Asegúrate de estar en el entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstala dependencias
pip install -r requirements.txt
```

### Puerto 5000 ocupado
```python
# En app.py, cambia:
app.run(debug=True, port=5001)
```

### Base de datos corrupta
```bash
# Elimina y recrea
rm reservas.db
python create_db.py
```

Desarrollado con Flask y Tailwind CSS
