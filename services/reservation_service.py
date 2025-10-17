from models import Reservation, Table, db
from datetime import timedelta

class ReservationBuilder:
    """
    Patrón Builder para construir objetos Reservation de forma flexible y controlada.
    Permite construir reservas paso a paso con validaciones.
    """
    
    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia todos los valores del builder"""
        self._user_id = None
        self._restaurant_id = None
        self._fecha_hora = None
        self._num_personas = 1
        self._table_id = None
        self._estado = 'PENDIENTE'
        return self

    def set_user(self, user_id):
        """Establece el usuario que hace la reserva"""
        self._user_id = user_id
        return self

    def set_restaurant(self, restaurant_id):
        """Establece el restaurante de la reserva"""
        self._restaurant_id = restaurant_id
        return self

    def set_datetime(self, fecha_hora):
        """Establece la fecha y hora de la reserva"""
        self._fecha_hora = fecha_hora
        return self

    def set_num_personas(self, n):
        """Establece el número de personas"""
        self._num_personas = n
        return self

    def set_table(self, table_id):
        """Establece la mesa específica"""
        self._table_id = table_id
        return self

    def set_estado(self, estado):
        """Establece el estado de la reserva (PENDIENTE, ACEPTADA, CANCELADA)"""
        if estado in ['PENDIENTE', 'ACEPTADA', 'CANCELADA']:
            self._estado = estado
        return self

    def build(self):
        """
        Construye y retorna el objeto Reservation.
        Valida que todos los campos obligatorios estén presentes.
        """
        if not all([self._user_id, self._restaurant_id, self._fecha_hora]):
            raise ValueError('Faltan datos obligatorios para construir la reserva (user_id, restaurant_id, fecha_hora)')
        
        return Reservation(
            user_id=self._user_id,
            restaurant_id=self._restaurant_id,
            table_id=self._table_id,
            fecha_hora=self._fecha_hora,
            num_personas=self._num_personas,
            estado=self._estado
        )


class ReservationService:
    """
    Servicio que maneja la lógica de negocio de las reservas.
    Trabaja con ReservationBuilder para crear reservas validadas.
    """
    
    RESERVATION_WINDOW = timedelta(hours=2)  # Cada reserva dura 2h

    @staticmethod
    def create_reservation(reservation):
        """
        Crea una reserva validando disponibilidad.
        
        Args:
            reservation: Objeto Reservation construido con ReservationBuilder
            
        Returns:
            tuple: (success: bool, result: Reservation o mensaje de error)
        """
        fecha = reservation.fecha_hora
        start = fecha - ReservationService.RESERVATION_WINDOW
        end = fecha + ReservationService.RESERVATION_WINDOW

        # Si el usuario elige una mesa específica
        if reservation.table_id:
            conflict = Reservation.query.filter(
                Reservation.table_id == reservation.table_id,
                Reservation.fecha_hora.between(start, end),
                Reservation.estado != 'CANCELADA'
            ).first()
            if conflict:
                return False, 'La mesa seleccionada no está disponible en ese horario.'
            db.session.add(reservation)
            db.session.commit()
            return True, reservation

        # Buscar mesas que soporten el número de personas
        candidates = Table.query.filter(
            Table.restaurant_id == reservation.restaurant_id,
            Table.capacidad >= reservation.num_personas
        ).order_by(Table.numero).all()

        for table in candidates:
            conflict = Reservation.query.filter(
                Reservation.table_id == table.id,
                Reservation.fecha_hora.between(start, end),
                Reservation.estado != 'CANCELADA'
            ).first()
            if not conflict:
                reservation.table_id = table.id
                db.session.add(reservation)
                db.session.commit()
                return True, reservation

        return False, 'No hay mesas disponibles para ese horario.'

    @staticmethod
    def get_available_tables(restaurant_id, fecha_hora):
        """
        Devuelve las mesas disponibles en el restaurante para esa fecha y hora.
        
        Args:
            restaurant_id: ID del restaurante
            fecha_hora: Fecha y hora de la reserva
            
        Returns:
            list: Lista de objetos Table disponibles
        """
        inicio = fecha_hora
        fin = fecha_hora + ReservationService.RESERVATION_WINDOW

        mesas = Table.query.filter_by(restaurant_id=restaurant_id).all()

        reservas_ocupadas = Reservation.query.filter(
            Reservation.restaurant_id == restaurant_id,
            Reservation.fecha_hora < fin,
            (Reservation.fecha_hora + ReservationService.RESERVATION_WINDOW) > inicio,
            Reservation.estado != 'CANCELADA'
        ).all()

        mesas_ocupadas_ids = [r.table_id for r in reservas_ocupadas if r.table_id]

        mesas_disponibles = [m for m in mesas if m.id not in mesas_ocupadas_ids]

        return mesas_disponibles    