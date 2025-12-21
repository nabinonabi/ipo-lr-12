import uuid

class Vehicle:
    def __init__(self, capacity: float):
        if not isinstance(capacity, (int, float)) or capacity <= 0:
            raise ValueError("Грузоподъемность должна быть положительным числом.")
        self.vehicle_id = str(uuid.uuid4())
        self.capacity = float(capacity)
        self.current_load = 0.0
        self.clients_list = []

    def load_cargo(self, client):
        if not hasattr(client, 'cargo_weight') or not hasattr(client, 'name'):
            raise TypeError("Объект должен быть экземпляром класса Client.")
        if self.current_load + client.cargo_weight > self.capacity:
            raise ValueError("Невозможно загрузить груз: превышает грузоподъемность.")
        self.current_load += client.cargo_weight
        self.clients_list.append(client)

    def has_space_for(self, cargo_weight: float) -> bool:
        return self.current_load + cargo_weight <= self.capacity

    def __str__(self):
        return f"Транспорт ID: {self.vehicle_id}, грузоподъемность: {self.capacity} т, текущая загрузка: {self.current_load:.2f} т"