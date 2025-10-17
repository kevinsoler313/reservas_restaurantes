# 🎨 Patrones Creacionales Implementados en RestauBook

## 📋 Índice
1. [Factory Method Pattern](#factory-method-pattern)
2. [Builder Pattern](#builder-pattern)
3. [Comparación y Casos de Uso](#comparación)

---

## 1️⃣ Factory Method Pattern

### 📍 Ubicación
**Archivo:** `services/factories.py`

### 🎯 Propósito
Encapsular la creación compleja de objetos `User`, centralizando la lógica de validación, encriptación de contraseñas y persistencia en la base de datos.

### 💻 Implementación

```python
class UserFactory:
    @staticmethod
    def create_user(role: str, email: str, password: str) -> User:
        # Validación del rol
        role = role.upper()
        if role not in ('CLIENTE', 'ADMIN'):
            raise ValueError('Rol desconocido')
        
        # Creación del objeto
        user = User(email=email, role=role)
        
        # Hash de la contraseña (seguridad)
        user.set_password(password)
        
        # Persistencia
        db.session.add(user)
        db.session.commit()
        
        return user
```

### 📍 Dónde se Usa

#### 1. En `create_db.py` (Inicialización)
```python
# Crear usuario admin
admin_user = UserFactory.create_user(
    'ADMIN', 
    'admin@example.com', 
    'admin123'
)
```

#### 2. En `app.py` - Ruta `/register`
```python
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    role = request.form.get('role', 'CLIENTE')
    
    # Uso del Factory
    new_user = UserFactory.create_user(role, email, password)
    
    flash('¡Cuenta creada exitosamente!', 'success')
    return redirect(url_for('login'))
```

### ✅ Ventajas Obtenidas

1. **Encapsulación:** Toda la lógica de creación en un solo lugar
2. **Validación centralizada:** El rol se valida antes de crear
3. **Seguridad:** Hash de contraseña automático
4. **Mantenibilidad:** Cambios en la creación se hacen en un solo lugar
5. **Reutilización:** Mismo código para admin y cliente

### 🎯 Principios SOLID Aplicados

- **Single Responsibility:** La clase tiene una única responsabilidad (crear usuarios)
- **Open/Closed:** Abierta para extensión (nuevos roles), cerrada para modificación

---

## 2️⃣ Builder Pattern

### 📍 Ubicación
**Archivo:** `services/reservation_service.py`

### 🎯 Propósito
Construir objetos `Reservation` complejos paso a paso, permitiendo una construcción flexible y validada con interfaz fluida (method chaining).

### 💻 Implementación

```python
class ReservationBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia todos los valores"""
        self._user_id = None
        self._restaurant_id = None
        self._fecha_hora = None
        self._num_personas = 1
        self._table_id = None
        self._estado = 'PENDIENTE'
        return self

    def set_user(self, user_id):
        """Establece el usuario"""
        self._user_id = user_id
        return self  # ✅ Method chaining

    def set_restaurant(self, restaurant_id):
        """Establece el restaurante"""
        self._restaurant_id = restaurant_id
        return self

    def set_datetime(self, fecha_hora):
        """Establece la fecha y hora"""
        self._fecha_hora = fecha_hora
        return self

    def set_num_personas(self, n):
        """Establece el número de personas"""
        self._num_personas = n
        return self

    def set_table(self, table_id):
        """Establece la mesa"""
        self._table_id = table_id
        return self

    def set_estado(self, estado):
        """Establece el estado"""
        if estado in ['PENDIENTE', 'ACEPTADA', 'CANCELADA']:
            self._estado = estado
        return self

    def build(self):
        """Construye y retorna el objeto Reservation"""
        # Validación de campos obligatorios
        if not all([self._user_id, self._restaurant_id, self._fecha_hora]):
            raise ValueError('Faltan datos obligatorios')
        
        return Reservation(
            user_id=self._user_id,
            restaurant_id=self._restaurant_id,
            table_id=self._table_id,
            fecha_hora=self._fecha_hora,
            num_personas=self._num_personas,
            estado=self._estado
        )
```

### 📍 Dónde se Usa

#### En `app.py` - Ruta `/reserve` (POST)
```python
@app.route("/reserve", methods=["POST"])
@login_required
def reserve():
    # ... validaciones previas ...
    
    # ✅ Uso del patrón Builder
    builder = ReservationBuilder()
    nueva_reserva = (builder
        .reset()
        .set_user(user_id)
        .set_restaurant(selected_restaurant)
        .set_table(mesa_id)
        .set_datetime(fecha_hora)
        .set_num_personas(num_personas)
        .build())
    
    nueva_reserva.estado = "PENDIENTE"
    db.session.add(nueva_reserva)
    db.session.commit()
    
    flash("¡Reserva confirmada con éxito!", "success")
    return redirect(url_for("perfil"))
```

### ✅ Ventajas Obtenidas

1. **Interfaz Fluida:** Method chaining hace el código más legible
2. **Construcción Flexible:** Puedes omitir parámetros opcionales
3. **Validación Controlada:** Solo `build()` valida campos obligatorios
4. **Inmutabilidad del Builder:** Cada `set_*` retorna `self`
5. **Código Limpio:** Más expresivo que constructor con muchos parámetros

### 🆚 Comparación: Sin Builder vs Con Builder

#### ❌ Sin Builder (Constructor Directo)
```python
# Difícil de leer, orden de parámetros confuso
nueva_reserva = Reservation(
    user_id=1,
    restaurant_id=2,
    table_id=5,
    fecha_hora=datetime.now(),
    num_personas=4,
    estado="PENDIENTE"
)
```

#### ✅ Con Builder (Interfaz Fluida)
```python
# Legible, claro, flexible
nueva_reserva = (builder
    .set_user(1)
    .set_restaurant(2)
    .set_table(5)
    .set_datetime(datetime.now())
    .set_num_personas(4)
    .build())
```

### 🎯 Principios SOLID Aplicados

- **Single Responsibility:** Solo construye objetos Reservation
- **Open/Closed:** Fácil agregar nuevos campos sin romper código existente
- **Dependency Inversion:** Depende de abstracciones, no implementaciones

---

## 3️⃣ Comparación y Casos de Uso

### 📊 Factory vs Builder

| Aspecto | Factory Method | Builder |
|---------|---------------|---------|
| **Propósito** | Crear objetos de una familia | Construir objetos complejos paso a paso |
| **Complejidad** | Objetos simples/medianos | Objetos complejos con muchos parámetros |
| **Flexibilidad** | Baja (todos los parámetros obligatorios) | Alta (parámetros opcionales) |
| **Interfaz** | Método estático simple | Interfaz fluida (method chaining) |
| **Validación** | En el momento de creación | Al final (en `build()`) |
| **Uso en proyecto** | Crear usuarios | Crear reservas |

### 🎯 Cuándo Usar Cada Uno

#### Usar Factory cuando:
- ✅ Necesitas crear objetos de una familia (User: CLIENTE, ADMIN)
- ✅ La creación involucra lógica compleja (validación, encriptación)
- ✅ Quieres ocultar la complejidad de la creación
- ✅ Los objetos son relativamente simples

**Ejemplo en el proyecto:** `UserFactory.create_user()`

#### Usar Builder cuando:
- ✅ El objeto tiene muchos parámetros (>5)
- ✅ Algunos parámetros son opcionales
- ✅ Quieres una construcción paso a paso
- ✅ Necesitas diferentes representaciones del mismo objeto

**Ejemplo en el proyecto:** `ReservationBuilder`

---

## 🔄 Flujo Completo de Uso

### Escenario: Usuario registra y hace una reserva

```python
# 1️⃣ Registro de usuario (Factory Pattern)
new_user = UserFactory.create_user(
    role='CLIENTE',
    email='cliente@email.com',
    password='secreto123'
)

# 2️⃣ Crear reserva (Builder Pattern)
builder = ReservationBuilder()
reserva = (builder
    .reset()
    .set_user(new_user.id)
    .set_restaurant(1)
    .set_table(5)
    .set_datetime(datetime(2025, 10, 20, 19, 0))
    .set_num_personas(4)
    .build())

# 3️⃣ Guardar en BD
db.session.add(reserva)
db.session.commit()
```

---

## 📈 Beneficios Generales

### 1. **Mantenibilidad**
- Código más limpio y organizado
- Cambios centralizados
- Fácil de entender para nuevos desarrolladores

### 2. **Escalabilidad**
- Fácil agregar nuevos tipos de usuarios (Factory)
- Fácil agregar nuevos campos a reservas (Builder)
- No rompe código existente

### 3. **Testabilidad**
- Fácil crear mocks de Factory
- Builder permite crear objetos para tests fácilmente
- Validaciones aisladas

### 4. **Reutilización**
- Mismo código para múltiples casos de uso
- Reducción de duplicación
- Componentes desacoplados

---

## 🎓 Conceptos Clave

### Method Chaining (Encadenamiento de Métodos)
```python
# Cada método retorna 'self'
builder.set_user(1).set_restaurant(2).set_table(3)
```

### Immutability del Builder
```python
# El builder no modifica el objeto final hasta build()
builder.set_user(1)
builder.set_restaurant(2)
reserva = builder.build()  # Solo aquí se crea
```

### Validación Lazy
```python
# No valida hasta el final
builder.set_user(1)  # ✅ No valida aún
builder.build()      # ✅ Aquí valida todo
```

---

## 📚 Referencias

### Archivos Relacionados
- `services/factories.py` - Implementación de Factory
- `services/reservation_service.py` - Implementación de Builder
- `app.py` - Uso de ambos patrones
- `models.py` - Modelos de dominio
- `create_db.py` - Inicialización con Factory

### Patrones de Diseño Gang of Four (GoF)
- Factory Method: Creational Pattern
- Builder: Creational Pattern

---

## ✅ Checklist de Implementación

- [x] Factory Pattern implementado
- [x] Factory Pattern en uso (UserFactory)
- [x] Builder Pattern implementado
- [x] Builder Pattern en uso (ReservationBuilder)
- [x] Documentación completa
- [x] Ejemplos de uso
- [x] Validaciones implementadas
- [x] Method chaining funcional
- [x] Código limpio y mantenible

---

**¡Ambos patrones creacionales están completamente implementados y en uso activo en el proyecto!** 🎉