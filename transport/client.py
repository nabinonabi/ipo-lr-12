class Client:
    def __init__(self, name: str, cargo_weight: float, is_vip: bool = False):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя клиента должно быть непустой строкой.")
        if not isinstance(cargo_weight, (int, float)) or cargo_weight <= 0:
            raise ValueError("Вес груза должен быть положительным числом.")
        if not isinstance(is_vip, bool):
            raise ValueError("Флаг VIP-статуса должен быть логическим значением.")

        self.name = name.strip()
        self.cargo_weight = float(cargo_weight)
        self.is_vip = is_vip

    def __repr__(self):
        return f"Client(name='{self.name}', cargo_weight={self.cargo_weight}, is_vip={self.is_vip})"