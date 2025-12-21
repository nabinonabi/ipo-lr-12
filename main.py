from transport.client import Client
from transport.train import Train
from transport.airplane import Airplane
from transport.transport_company import TransportCompany

def get_float_input(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Значение должно быть положительным.")
                continue
            return value
        except ValueError:
            print("Некорректный ввод. Введите число.")

def get_int_input(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Значение должно быть положительным целым числом.")
                continue
            return value
        except ValueError:
            print("Некоректный ввод. Введите целое число.")

def get_bool_input(prompt: str) -> bool:
    while True:
        response = input(prompt).strip().lower()
        if response in ('да', 'yes', 'y', '1'):
            return True
        elif response in ('нет', 'no', 'n', '0'):
            return False
        else:
            print("Введите 'да' или 'нет'.")

def main():
    print("Добро пожаловать в систему управления транспортной компанией")
    company_name = input("Введите название компании: ").strip()
    while not company_name:
        print("Название не может быть пустым.")
        company_name = input("Введите название компании: ").strip()

    company = TransportCompany(company_name)

    while True:
        print("\nМеню:")
        print("1. Добавить клиента")
        print("2. Добавить транспортное средство")
        print("3. Показать всех клиентов")
        print("4. Показать все транспортные средства")
        print("5. Распределить грузы")
        print("6. Выйти")

        choice = input("Выберите действие (1-6): ").strip()

        if choice == '1':
            name = input("Введите имя клиента: ").strip()
            while not name:
                print("Имя не может быть пустым.")
                name = input("Введите имя клиента: ").strip()
            weight = get_float_input("Введите вес груза (в тоннах): ")
            is_vip = get_bool_input("Это VIP-клиент? (да/нет): ")
            try:
                client = Client(name, weight, is_vip)
                company.add_client(client)
                print(f"Клиент '{name}' успешно добавлен.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '2':
            print("\nТипы транспорта:")
            print("1. Поезд")
            print("2. Самолет")
            transport_type = input("Выберите тип (1 или 2): ").strip()
            capacity = get_float_input("Введите грузоподъемность (в тоннах): ")

            try:
                if transport_type == '1':
                    cars = get_int_input("Введите количество вагонов: ")
                    vehicle = Train(capacity, cars)
                elif transport_type == '2':
                    altitude = get_int_input("Введите максимальную высоту полета (в метрах): ")
                    vehicle = Airplane(capacity, altitude)
                else:
                    print("Неверный выбор.")
                    continue

                company.add_vehicle(vehicle)
                print("Транспортное средство успешно добавлено.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            if not company.clients:
                print("Нет зарегистрированных клиентов.")
            else:
                print("\nСписок клиентов:")
                for i, client in enumerate(company.clients, 1):
                    vip_str = " (VIP)" if client.is_vip else ""
                    print(f"{i}. {client.name}, груз: {client.cargo_weight} т{vip_str}")

        elif choice == '4':
            vehicles = company.list_vehicles()
            if not vehicles:
                print("Нет зарегистрированных транспортных средств.")
            else:
                print("\nСписок транспортных средств:")
                for i, v in enumerate(vehicles, 1):
                    print(f"{i}. {v}")

        elif choice == '5':
            if not company.clients:
                print("Нет клиентов для распределения грузов.")
            elif not company.vehicles:
                print("Нет транспорта для распределения грузов.")
            else:
                unassigned = company.optimize_cargo_distribution()
                print("\nРаспределение грузов завершено.")

                print("\nРезультаты загрузки")
                for v in company.vehicles:
                    if v.clients_list:
                        print(f"\n{v}")
                        for client in v.clients_list:
                            vip = " (VIP)" if client.is_vip else ""
                            print(f"  - {client.name}: {client.cargo_weight} т{vip}")
                    else:
                        print(f"\n{v}пуст")

                if unassigned:
                    print("\nНе удалось распределить грузы для следующих клиентов:")
                    for client in unassigned:
                        vip = " (VIP)" if client.is_vip else ""
                        print(f"  - {client.name}: {client.cargo_weight} т{vip}")
                else:
                    print("\n Все грузы распределены")

        elif choice == '6':
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()