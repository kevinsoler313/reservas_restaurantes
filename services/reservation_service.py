from models import Reservation, Table, db
from datetime import timedelta

class ReservationBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._user_id = None
        self._restaurant_id = None
        self._fecha_hora = None
        self._num_personas = 1
        self._table_id = None
        return self

    def set_user(self, user_id):
        self._user_id = user_id
        return self

    def set_restaurant(self, restaurant_id):
        self._restaurant_id = restaurant_id
        return self

    def set_datetime(self, fecha_hora):
        self._fecha_hora = fecha_hora
        return self

    def set_num_personas(self, n):
        self._num_personas = n
        return self

    def set_table(self, table_id):
        self._table_id = table_id
        return self

    def build(self):
        if not all([self._user_id, self._restaurant_id, self._fecha_hora]):
            raise ValueError('Faltan datos para construir la reserva')
        return Reservation(
            user_id=self._user_id,
            restaurant_id=self._restaurant_id,
            table_id=self._table_id,
            fecha_hora=self._fecha_hora,
            num_personas=self._num_personas,
        )


class ReservationService:
    RESERVATION_WINDOW = timedelta(hours=2)  # Cada reserva dura 2h

    @staticmethod
    def create_reservation(reservation):
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
        """Devuelve las mesas disponibles en el restaurante para esa fecha y hora."""
        inicio = fecha_hora
        fin = fecha_hora + ReservationService.RESERVATION_WINDOW

        mesas = Table.query.filter_by(restaurant_id=restaurant_id).all()

        reservas_ocupadas = Reservation.query.filter(
            Reservation.restaurant_id == restaurant_id,
            Reservation.fecha_hora < fin,
            (Reservation.fecha_hora + ReservationService.RESERVATION_WINDOW) > inicio
        ).all()

        mesas_ocupadas_ids = [r.table_id for r in reservas_ocupadas if r.table_id]

        mesas_disponibles = [m for m in mesas if m.id not in mesas_ocupadas_ids]

        return mesas_disponibles
