from .vehicle import Vehicle
from .client import Client

class TransportCompany:
    def __init__(self, name: str):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название компании должно быть непустой строкой.")
        self.name = name.strip()
        self.vehicles = []
        self.clients = []

    def add_vehicle(self, vehicle):
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Объект должен быть экземпляром класса Vehicle или его наследником.")
        self.vehicles.append(vehicle)

    def list_vehicles(self):
        return self.vehicles

    def add_client(self, client):
        if not isinstance(client, Client):
            raise TypeError("Объект должен быть экземпляром класса Client.")
        self.clients.append(client)

    def optimize_cargo_distribution(self):
        # Сортируем клиентов: VIP — в начало
        sorted_clients = sorted(self.clients, key=lambda c: not c.is_vip)

        # Сортируем транспорт по убыванию грузоподъемности (жадный алгоритм)
        sorted_vehicles = sorted(self.vehicles, key=lambda v: v.capacity, reverse=True)

        # Сбрасываем загрузку всех транспортных средств
        for v in sorted_vehicles:
            v.current_load = 0.0
            v.clients_list = []

        unassigned = []

        for client in sorted_clients:
            assigned = False
            # Ищем первый транспорт, в который помещается груз
            for vehicle in sorted_vehicles:
                if vehicle.has_space_for(client.cargo_weight):
                    vehicle.load_cargo(client)
                    assigned = True
                    break
            if not assigned:
                unassigned.append(client)

        return unassigned