import dearpygui.dearpygui as dpg
from transport.client import Client
from transport.train import Train
from transport.airplane import Airplane
from transport.transport_company import TransportCompany
import json
import os

company = TransportCompany("Моя Транспортная Компания")
client_table = "client_table"
vehicle_table = "vehicle_table"
status_bar = "status_bar"
last_export_path = None


def set_status(message: str):
    dpg.set_value(status_bar, message)


def show_message(title: str, message: str, error=False):
    with dpg.mutex():
        if dpg.does_item_exist("modal_msg"):
            dpg.delete_item("modal_msg")
    with dpg.window(label=title, modal=True, tag="modal_msg", no_close=True):
        dpg.add_text(message, color=(255, 50, 50) if error else (100, 200, 100))
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("modal_msg"))


def validate_client_data(name: str, weight_str: str) -> tuple[bool, str, float]:
    if not name or len(name.strip()) < 2 or not name.replace(" ", "").isalpha():
        return False, "Имя должно содержать минимум 2 буквы (без цифр и символов).", 0.0
    try:
        weight = float(weight_str)
        if weight <= 0 or weight > 10000:
            return False, "Вес груза должен быть от 0.1 до 10000 кг.", 0.0
    except ValueError:
        return False, "Вес груза должен быть числом.", 0.0
    return True, "", weight


def add_client_callback(sender, app_data, user_data):
    name = dpg.get_value("client_name_input")
    weight_str = dpg.get_value("client_weight_input")
    is_vip = dpg.get_value("client_vip_checkbox")

    valid, error_msg, weight = validate_client_data(name, weight_str)
    if not valid:
        show_message("Ошибка ввода", error_msg, error=True)
        return

    try:
        client = Client(name.strip(), weight, is_vip)
        company.add_client(client)
        refresh_client_table()
        set_status(f"Клиент '{name}' добавлен.")
        dpg.hide_item("add_client_window")
        dpg.set_value("client_name_input", "")
        dpg.set_value("client_weight_input", "")
        dpg.set_value("client_vip_checkbox", False)
    except Exception as e:
        show_message("Ошибка", str(e), error=True)


def open_add_client_window():
    dpg.set_value("client_name_input", "")
    dpg.set_value("client_weight_input", "")
    dpg.set_value("client_vip_checkbox", False)
    dpg.show_item("add_client_window")


def edit_client_callback(sender, app_data):
    row_id = app_data[1]
    if row_id < len(company.clients):
        client = company.clients[row_id]
        dpg.set_value("client_name_input", client.name)
        dpg.set_value("client_weight_input", str(client.cargo_weight))
        dpg.set_value("client_vip_checkbox", client.is_vip)
        dpg.set_item_user_data("save_client_btn", ("edit", row_id))
        dpg.show_item("add_client_window")


def save_client_edit(sender, app_data, user_data):
    action, index = user_data
    name = dpg.get_value("client_name_input")
    weight_str = dpg.get_value("client_weight_input")
    is_vip = dpg.get_value("client_vip_checkbox")

    valid, error_msg, weight = validate_client_data(name, weight_str)
    if not valid:
        show_message("Ошибка ввода", error_msg, error=True)
        return

    try:
        client = Client(name.strip(), weight, is_vip)
        company.clients[index] = client
        refresh_client_table()
        set_status(f"Клиент '{name}' обновлён.")
        dpg.hide_item("add_client_window")
    except Exception as e:
        show_message("Ошибка", str(e), error=True)


def delete_selected_client():
    selected = dpg.get_selected_rows(client_table)
    if not selected:
        show_message("Внимание", "Выберите клиента для удаления.")
        return
    idx = selected[0]
    name = company.clients[idx].name
    del company.clients[idx]
    refresh_client_table()
    set_status(f"Клиент '{name}' удалён.")


def validate_vehicle_data(vehicle_type: str, capacity_str: str, extra_str: str) -> tuple[bool, str, float, int]:
    try:
        capacity = float(capacity_str)
        if capacity <= 0 or capacity > 10000:
            return False, "Грузоподъёмность должна быть от 0.1 до 10000 т.", 0.0, 0
    except ValueError:
        return False, "Грузоподъёмность должна быть числом.", 0.0, 0

    try:
        extra = int(extra_str)
        if extra <= 0:
            return False, "Доп. параметр должен быть положительным целым числом.", 0.0, 0
    except ValueError:
        return False, "Доп. параметр должен быть целым числом.", 0.0, 0

    return True, "", capacity, extra


def add_vehicle_callback(sender, app_data, user_data):
    v_type = dpg.get_value("vehicle_type_combo")
    cap_str = dpg.get_value("vehicle_capacity_input")
    extra_str = dpg.get_value("vehicle_extra_input")

    valid, error_msg, capacity, extra = validate_vehicle_data(v_type, cap_str, extra_str)
    if not valid:
        show_message("Ошибка ввода", error_msg, error=True)
        return

    try:
        if v_type == "Поезд":
            vehicle = Train(capacity, extra)
        elif v_type == "Самолёт":
            vehicle = Airplane(capacity, extra)
        else:
            raise ValueError("Неизвестный тип транспорта")

        company.add_vehicle(vehicle)
        refresh_vehicle_table()
        set_status(f"{v_type} добавлен (ID: {vehicle.vehicle_id[:8]}...).")
        dpg.hide_item("add_vehicle_window")
    except Exception as e:
        show_message("Ошибка", str(e), error=True)


def open_add_vehicle_window():
    dpg.set_value("vehicle_type_combo", "Поезд")
    dpg.set_value("vehicle_capacity_input", "")
    dpg.set_value("vehicle_extra_input", "")
    dpg.show_item("add_vehicle_window")


def edit_vehicle_callback(sender, app_data):
    row_id = app_data[1]
    if row_id < len(company.vehicles):
        v = company.vehicles[row_id]
        if isinstance(v, Train):
            dpg.set_value("vehicle_type_combo", "Поезд")
            dpg.set_value("vehicle_extra_input", str(v.number_of_cars))
        elif isinstance(v, Airplane):
            dpg.set_value("vehicle_type_combo", "Самолёт")
            dpg.set_value("vehicle_extra_input", str(v.max_altitude))
        dpg.set_value("vehicle_capacity_input", str(v.capacity))
        dpg.set_item_user_data("save_vehicle_btn", ("edit", row_id))
        dpg.show_item("add_vehicle_window")


def save_vehicle_edit(sender, app_data, user_data):
    action, index = user_data
    v_type = dpg.get_value("vehicle_type_combo")
    cap_str = dpg.get_value("vehicle_capacity_input")
    extra_str = dpg.get_value("vehicle_extra_input")

    valid, error_msg, capacity, extra = validate_vehicle_data(v_type, cap_str, extra_str)
    if not valid:
        show_message("Ошибка ввода", error_msg, error=True)
        return

    try:
        if v_type == "Поезд":
            vehicle = Train(capacity, extra)
        elif v_type == "Самолёт":
            vehicle = Airplane(capacity, extra)
        else:
            raise ValueError("Неизвестный тип")

        old_id = company.vehicles[index].vehicle_id
        vehicle.vehicle_id = old_id
        company.vehicles[index] = vehicle
        refresh_vehicle_table()
        set_status(f"{v_type} обновлён.")
        dpg.hide_item("add_vehicle_window")
    except Exception as e:
        show_message("Ошибка", str(e), error=True)


def delete_selected_vehicle():
    selected = dpg.get_selected_rows(vehicle_table)
    if not selected:
        show_message("Внимание", "Выберите транспорт для удаления.")
        return
    idx = selected[0]
    v = company.vehicles[idx]
    v_type = "Поезд" if isinstance(v, Train) else "Самолёт"
    del company.vehicles[idx]
    refresh_vehicle_table()
    set_status(f"{v_type} (ID: {v.vehicle_id[:8]}...) удалён.")


def refresh_client_table():
    dpg.delete_item(client_table, children_only=True)
    for i, client in enumerate(company.clients):
        dpg.add_table_row(parent=client_table, tag=f"client_row_{i}")
        dpg.add_selectable(label=client.name, span_columns=True, callback=edit_client_callback,
                           user_data=i, parent=f"client_row_{i}")
        dpg.add_text(str(client.cargo_weight), parent=f"client_row_{i}")
        dpg.add_text("Да" if client.is_vip else "Нет", parent=f"client_row_{i}")


def refresh_vehicle_table():
    dpg.delete_item(vehicle_table, children_only=True)
    for i, v in enumerate(company.vehicles):
        v_type = "Поезд" if isinstance(v, Train) else "Самолёт"
        dpg.add_table_row(parent=vehicle_table, tag=f"vehicle_row_{i}")
        dpg.add_selectable(label=v.vehicle_id[:8] + "...", span_columns=True,
                           callback=edit_vehicle_callback, user_data=i, parent=f"vehicle_row_{i}")
        dpg.add_text(v_type, parent=f"vehicle_row_{i}")
        dpg.add_text(str(v.capacity), parent=f"vehicle_row_{i}")
        dpg.add_text(f"{v.current_load:.2f}", parent=f"vehicle_row_{i}")


def distribute_cargo():
    if not company.clients:
        show_message("Ошибка", "Нет клиентов для распределения.")
        return
    if not company.vehicles:
        show_message("Ошибка", "Нет транспорта для загрузки.")
        return

    unassigned = company.optimize_cargo_distribution()
    refresh_vehicle_table()
    set_status("Грузы распределены!")

    result_lines = ["Распределение грузов:\n"]
    for v in company.vehicles:
        v_type = "Поезд" if isinstance(v, Train) else "Самолёт"
        result_lines.append(f"\n{v_type} (ID: {v.vehicle_id[:8]}...):")
        if v.clients_list:
            for c in v.clients_list:
                result_lines.append(f"  - {c.name} ({c.cargo_weight} т)" + (" [VIP]" if c.is_vip else ""))
        else:
            result_lines.append("  (пусто)")

    if unassigned:
        result_lines.append("\nНе распределены:")
        for c in unassigned:
            result_lines.append(f"  - {c.name} ({c.cargo_weight} т)" + (" [VIP]" if c.is_vip else ""))

    result_text = "\n".join(result_lines)

    with dpg.mutex():
        if dpg.does_item_exist("distribution_result"):
            dpg.delete_item("distribution_result")
    with dpg.window(label="Результат распределения", tag="distribution_result", width=500, height=400):
        dpg.add_text(result_text, wrap=480)
        dpg.add_button(label="Закрыть", callback=lambda: dpg.delete_item("distribution_result"))


def export_results():
    if not company.vehicles or all(len(v.clients_list) == 0 for v in company.vehicles):
        show_message("Ошибка", "Нет распределённых грузов для экспорта.")
        return

    data = {
        "company": company.name,
        "vehicles": []
    }

    for v in company.vehicles:
        v_type = "Train" if isinstance(v, Train) else "Airplane"
        clients = [
            {
                "name": c.name,
                "cargo_weight": c.cargo_weight,
                "is_vip": c.is_vip
            }
            for c in v.clients_list
        ]
        data["vehicles"].append({
            "id": v.vehicle_id,
            "type": v_type,
            "capacity": v.capacity,
            "current_load": v.current_load,
            "clients": clients
        })

    try:
        with open("distribution_result.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        global last_export_path
        last_export_path = os.path.abspath("distribution_result.json")
        set_status(f"Результат сохранён в: distribution_result.json")
        show_message("Успех", "Результаты успешно экспортированы в файл distribution_result.json")
    except Exception as e:
        show_message("Ошибка экспорта", str(e), error=True)


def show_about():
    with dpg.mutex():
        if dpg.does_item_exist("about_window"):
            dpg.delete_item("about_window")
    with dpg.window(label="О программе", modal=True, tag="about_window", no_resize=True):
        dpg.add_text("Лабораторная работа №12")
        dpg.add_text("Вариант 5")
        dpg.add_text("Разработчик: [Ваше ФИО]")
        dpg.add_separator()
        dpg.add_button(label="Закрыть", callback=lambda: dpg.delete_item("about_window"))


dpg.create_context()

with dpg.window(tag="PrimaryWindow"):
    with dpg.menu_bar():
        with dpg.menu(label="Файл"):
            dpg.add_menu_item(label="Экспорт результата", callback=export_results)
        with dpg.menu(label="Справка"):
            dpg.add_menu_item(label="О программе", callback=show_about)

    with dpg.group(horizontal=True):
        dpg.add_button(label="Добавить клиента", callback=open_add_client_window)
        dpg.add_button(label="Удалить клиента", callback=delete_selected_client)
        dpg.add_button(label="Добавить транспорт", callback=open_add_vehicle_window)
        dpg.add_button(label="Удалить транспорт", callback=delete_selected_vehicle)
        dpg.add_button(label="Распределить грузы", callback=distribute_cargo)

    dpg.add_text("Клиенты:")
    with dpg.table(tag=client_table, header_row=True, borders_innerH=True, borders_outerH=True,
                   borders_innerV=True, borders_outerV=True, resizable=True, policy=dpg.mvTable_SizingFixedFit):
        dpg.add_table_column(label="Имя")
        dpg.add_table_column(label="Вес груза (т)")
        dpg.add_table_column(label="VIP")

    dpg.add_separator()
    dpg.add_text("Транспортные средства:")
    with dpg.table(tag=vehicle_table, header_row=True, borders_innerH=True, borders_outerH=True,
                   borders_innerV=True, borders_outerV=True, resizable=True, policy=dpg.mvTable_SizingFixedFit):
        dpg.add_table_column(label="ID")
        dpg.add_table_column(label="Тип")
        dpg.add_table_column(label="Грузоподъёмность (т)")
        dpg.add_table_column(label="Текущая загрузка (т)")

    dpg.add_text("", tag=status_bar)


with dpg.window(label="Добавить/редактировать клиента", show=False, tag="add_client_window", modal=True):
    dpg.add_input_text(label="Имя клиента", tag="client_name_input")
    dpg.add_input_text(label="Вес груза (т)", tag="client_weight_input")
    dpg.add_checkbox(label="VIP-статус", tag="client_vip_checkbox")
    dpg.add_button(label="Сохранить", tag="save_client_btn", callback=add_client_callback)
    dpg.add_same_line()
    dpg.add_button(label="Отмена", callback=lambda: dpg.hide_item("add_client_window"))


with dpg.window(label="Добавить/редактировать транспорт", show=False, tag="add_vehicle_window", modal=True):
    dpg.add_combo(label="Тип транспорта", items=["Поезд", "Самолёт"], default_value="Поезд", tag="vehicle_type_combo")
    dpg.add_input_text(label="Грузоподъёмность (т)", tag="vehicle_capacity_input")
    dpg.add_input_text(label="Кол-во вагонов / макс. высота", tag="vehicle_extra_input")
    dpg.add_button(label="Сохранить", tag="save_vehicle_btn", callback=add_vehicle_callback)
    dpg.add_same_line()
    dpg.add_button(label="Отмена", callback=lambda: dpg.hide_item("add_vehicle_window"))


dpg.set_table_row_double_click_callback(client_table, edit_client_callback)
dpg.set_table_row_double_click_callback(vehicle_table, edit_vehicle_callback)

dpg.create_viewport(title='Транспортная компания — ЛР12', width=900, height=700)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("PrimaryWindow", True)
dpg.start_dearpygui()
dpg.destroy_context()