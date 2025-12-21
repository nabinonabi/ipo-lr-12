from .vehicle import Vehicle

class Airplane(Vehicle):
    def __init__(self, capacity: float, max_altitude: int):
        super().__init__(capacity)
        if not isinstance(max_altitude, int) or max_altitude <= 0:
            raise ValueError("Максимальная высота должна быть положительным целым числом.")
        self.max_altitude = max_altitude

    def __str__(self):
        base = super().__str__()
        return f"{base}, макс. высота: {self.max_altitude} м"