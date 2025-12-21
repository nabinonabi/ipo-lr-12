from .vehicle import Vehicle

class Train(Vehicle):
    def __init__(self, capacity: float, number_of_cars: int):
        super().__init__(capacity)
        if not isinstance(number_of_cars, int) or number_of_cars <= 0:
            raise ValueError("Количество вагонов должно быть положительным целым числом.")
        self.number_of_cars = number_of_cars

    def __str__(self):
        base = super().__str__()
        return f"{base}, количество вагонов: {self.number_of_cars}"