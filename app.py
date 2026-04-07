import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

# Устанавливаем светлую тему
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Словарь часовых поясов
TIMEZONES = {
    "UTC": "UTC",
    "Калининград (+02:00)": "Europe/Kaliningrad",
    "Москва (+03:00)": "Europe/Moscow",
    "Самара (+04:00)": "Europe/Samara",
    "Екатеринбург (+05:00)": "Asia/Yekaterinburg",
    "Омск (+06:00)": "Asia/Omsk",
    "Красноярск (+07:00)": "Asia/Krasnoyarsk",
    "Иркутск (+08:00)": "Asia/Irkutsk",
    "Якутск (+09:00)": "Asia/Yakutsk",
    "Владивосток (+10:00)": "Asia/Vladivostok",
    "Магадан (+11:00)": "Asia/Magadan",
    "Камчатка (+12:00)": "Asia/Kamchatka"
}

TIMEZONES_WITH_NONE = {
    "Не указывать": None,
    "Калининград (+02:00)": "Europe/Kaliningrad",
    "Москва (+03:00)": "Europe/Moscow",
    "Самара (+04:00)": "Europe/Samara",
    "Екатеринбург (+05:00)": "Asia/Yekaterinburg",
    "Омск (+06:00)": "Asia/Omsk",
    "Красноярск (+07:00)": "Asia/Krasnoyarsk",
    "Иркутск (+08:00)": "Asia/Irkutsk",
    "Якутск (+09:00)": "Asia/Yakutsk",
    "Владивосток (+10:00)": "Asia/Vladivostok",
    "Магадан (+11:00)": "Asia/Magadan",
    "Камчатка (+12:00)": "Asia/Kamchatka"
}

def parse_gpx_file(file_path, gps_timezone, lag_seconds=0):
    """Читает GPX, возвращает список (utc_time, lat, lon) с применённым лагом (секунды, могут быть отриц.)."""
    coords = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {
            'default': 'http://www.topografix.com/GPX/1/1',
            'ns3': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
            'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
            'gpx_style': 'http://www.topografix.com/GPX/gpx_style/0/2'
        }
        lag = timedelta(seconds=lag_seconds)
        for trkpt in root.findall('.//default:trkpt', ns):
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            time_elem = trkpt.find('default:time', ns)
            if time_elem is None or time_elem.text is None:
                print(f"GPX: No time found for trackpoint at lat={lat}, lon={lon}")
                continue
            time_str = time_elem.text
            try:
                if time_str.endswith('Z'):
                    if '.' in time_str:
                        time = datetime.strptime(time_str[:-1], '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        time = datetime.strptime(time_str[:-1], '%Y-%m-%dT%H:%M:%S')
                else:
                    if '.' in time_str:
                        time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

                if gps_timezone:
                    tz = pytz.timezone(gps_timezone)
                    localized = tz.localize(time, is_dst=None)
                    utc_time = localized.astimezone(pytz.UTC)
                else:
                    utc_time = time.replace(tzinfo=pytz.UTC)

                utc_time = utc_time + lag  # применяем лаг в секундах

                coords.append((utc_time, lat, lon))
                print(f"GPX: local={time}, tz={gps_timezone}, utc(with lag)={utc_time}, lat={lat}, lon={lon}")
            except (ValueError, AttributeError) as e:
                print(f"GPX: Error parsing time {time_str}: {e}")
                continue
    except Exception as e:
        print(f"Ошибка при чтении GPX-файла {file_path}: {e}")
    return coords

def read_txt_coord_file(file_path, gps_timezone=None, lag_seconds=0):
    """
    TXT как:
      • point_id,lat,lon  (gps_timezone=None) → {point_id: (lat, lon)}
      • lat,lon,ISOtime   (gps_timezone задан) → {utc_time(+лаг сек): (lat, lon)}
    """
    coords = {}
    try:
        with open(file_path, 'r') as f:
            lag = timedelta(seconds=lag_seconds)
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3 and gps_timezone is None:
                    try:
                        point_id = int(parts[0])
                        lat = float(parts[1])
                        lon = float(parts[2])
                        coords[point_id] = (lat, lon)
                    except ValueError:
                        continue
                elif len(parts) == 3 and gps_timezone:
                    try:
                        lat = float(parts[0])
                        lon = float(parts[1])
                        time_str = parts[2].strip()
                        if time_str.endswith('Z'):
                            if '.' in time_str:
                                time = datetime.strptime(time_str[:-1], '%Y-%m-%dT%H:%M:%S.%f')
                            else:
                                time = datetime.strptime(time_str[:-1], '%Y-%m-%dT%H:%M:%S')
                        else:
                            if '.' in time_str:
                                time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')
                            else:
                                time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

                        tz = pytz.timezone(gps_timezone)
                        localized = tz.localize(time, is_dst=None)
                        utc_time = localized.astimezone(pytz.UTC)

                        utc_time = utc_time + lag  # применяем лаг в секундах

                        coords[utc_time] = (lat, lon)
                        print(f"TXT-GPS: local={time}, tz={gps_timezone}, utc(with lag)={utc_time}, lat={lat}, lon={lon}")
                    except (ValueError, AttributeError) as e:
                        print(f"TXT-GPS: Error parsing time {time_str}: {e}")
                        continue
    except Exception as e:
        print(f"Ошибка при чтении TXT-файла координат {file_path}: {e}")
    return coords

def is_five_number_line(parts):
    if len(parts) != 5:
        return False
    try:
        float(parts[0]); float(parts[1]); float(parts[2]); float(parts[3]); float(parts[4])
        return True
    except ValueError:
        return False

def find_closest_gpx_coord(gpx_coords, target_time):
    if not gpx_coords:
        print("GPS: No coordinates available")
        return None
    target_time = target_time.replace(microsecond=0)
    gpx_coords.sort(key=lambda x: x[0])
    closest = min(gpx_coords, key=lambda coord: abs(coord[0] - target_time))
    time_diff = abs(closest[0] - target_time)
    if time_diff > timedelta(seconds=10):
        print(f"GPS: No close match for time={target_time} (UTC), closest diff={time_diff}")
        return None
    print(f"GPS: Closest for {target_time} → actual={closest[0]}, diff={time_diff}, coords={(closest[1], closest[2])}")
    return (closest[1], closest[2])

def find_closest_txt_gpx_coord(txt_coords, target_time):
    if not txt_coords:
        print("TXT-GPS: No coordinates available")
        return None
    target_time = target_time.replace(microsecond=0)
    print(f"Searching TXT-GPS for target_time={target_time} (UTC)")
    closest_time = min(txt_coords.keys(), key=lambda t: abs(t - target_time))
    time_diff = abs(closest_time - target_time)
    if time_diff > timedelta(seconds=10):
        print(f"TXT-GPS: No close match for time={target_time} (UTC), closest diff={time_diff}")
        return None
    coords = txt_coords[closest_time]
    print(f"TXT-GPS: Closest for {target_time} → actual={closest_time}, diff={time_diff}, coords={coords}")
    return coords

def process_file(file_path, coords, gpx_coords, output_path, instrument_timezone, is_gps=False):
    try:
        with open(file_path, 'r') as f1, open(output_path, 'w') as f_out:
            current_point_id = None
            five_number_count = 0
            current_time = None
            tz = pytz.UTC if instrument_timezone == "UTC" else pytz.timezone(instrument_timezone)

            for line in f1:
                line = line.rstrip('\n')
                parts = line.split()
                if len(parts) >= 8 and parts[0].isdigit() and parts[7].isdigit():
                    try:
                        current_point_id = int(parts[7])
                        five_number_count = 0
                        year, month, day, hour, minute, second, hundredth = map(int, parts[:7])
                        if year < 100:
                            year += 2000
                        if year < 2000:
                            raise ValueError(f"Invalid year {year}")
                        microsecond = hundredth * 10000
                        print(f"Instrument: raw={parts[:7]}, adjusted_year={year}")
                        naive = datetime(year, month, day, hour, minute, second, microsecond)
                        current_time = tz.localize(naive, is_dst=None).astimezone(pytz.UTC)
                        print(f"Instrument: point_id={current_point_id}, local={naive}, utc={current_time}")
                    except ValueError as e:
                        print(f"Instrument: Error parsing time {parts[:7]}: {e}")
                        current_point_id = None
                        current_time = None

                elif is_five_number_line(parts):
                    five_number_count += 1
                    print(f"Found 5-number line #{five_number_count}: {line}")
                    if five_number_count == 2 and current_time is not None:
                        new_lat, new_lon = None, None
                        if gpx_coords:
                            result = find_closest_gpx_coord(gpx_coords, current_time)
                            if result:
                                new_lat, new_lon = result
                                print(f"Replacing with GPS coords: lat={new_lat}, lon={new_lon}")
                        elif is_gps:
                            result = find_closest_txt_gpx_coord(coords, current_time)
                            if result:
                                new_lat, new_lon = result
                                print(f"Replacing with TXT-GPS coords: lat={new_lat}, lon={new_lon}")
                        elif current_point_id in coords:
                            new_lat, new_lon = coords[current_point_id]
                            print(f"Replacing with TXT coords: lat={new_lat}, lon={new_lon}")

                        if new_lat is not None and new_lon is not None:
                            parts[0] = str(new_lat)
                            parts[1] = str(new_lon)
                            line = ' '.join(parts)
                            print(f"New line: {line}")
                        else:
                            print("No coordinates found for replacement")

                f_out.write(line + '\n')
        return True
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return False

class DopplerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Обработчик координат")
        self.geometry("900x640")
        self.resizable(False, False)

        # Основной фрейм
        self.main_frame = ctk.CTkFrame(self, fg_color="#F7F7F9", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        self.title_label = ctk.CTkLabel(self.main_frame, text="Обработчик координат",
                                        font=("Arial", 26, "bold"), text_color="#333333")
        self.title_label.pack(pady=(0, 20), anchor="center")

        # Фрейм для списков файлов
        self.files_frame = ctk.CTkFrame(self.main_frame, fg_color="#F7F7F9", corner_radius=0)
        self.files_frame.pack(fill="both", expand=True)

        # Панель координат
        self.coord_container = ctk.CTkFrame(self.files_frame, fg_color="#FFFFFF", corner_radius=10)
        self.coord_container.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.coord_label = ctk.CTkLabel(self.coord_container, text="Файлы координат", font=("Arial", 14), text_color="#555555")
        self.coord_label.pack(anchor="w", padx=15, pady=(15, 5))
        self.coord_listbox_frame = tk.Frame(self.coord_container, bg="#F9F9F9")
        self.coord_listbox_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.coord_listbox = tk.Listbox(self.coord_listbox_frame, height=8, bg="#F9F9F9",
                                       relief="flat", borderwidth=0, highlightthickness=0, font=("Arial", 14))
        self.coord_listbox.pack(fill="both", expand=True)
        self.coord_listbox.drop_target_register(DND_FILES)
        self.coord_listbox.dnd_bind('<<Drop>>', self.drop_coord_file)
        self.coord_menu = tk.Menu(self.coord_listbox, tearoff=0, font=("Arial", 12))
        self.coord_menu.add_command(label="Удалить", command=self.delete_coord_file)
        self.coord_listbox.bind("<Button-3>", self.show_coord_menu)
        self.coord_buttons_frame = ctk.CTkFrame(self.coord_container, fg_color="#FFFFFF")
        self.coord_buttons_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.add_coord_button = ctk.CTkButton(self.coord_buttons_frame, text="Добавить", font=("Arial", 14),
                                            command=self.add_coord_files, width=100, height=32, corner_radius=8)
        self.add_coord_button.pack(side="left", padx=(0, 5))
        self.clear_coord_button = ctk.CTkButton(self.coord_buttons_frame, text="Очистить", font=("Arial", 14),
                                              command=self.clear_coord_files, width=100, height=32, corner_radius=8)
        self.clear_coord_button.pack(side="left")

        # Панель прибора
        self.data_container = ctk.CTkFrame(self.files_frame, fg_color="#FFFFFF", corner_radius=10)
        self.data_container.pack(side="right", fill="both", expand=True, padx=(10, 0))
        self.data_label = ctk.CTkLabel(self.data_container, text="Файлы прибора", font=("Arial", 14), text_color="#555555")
        self.data_label.pack(anchor="w", padx=15, pady=(15, 5))
        self.data_listbox_frame = tk.Frame(self.data_container, bg="#F9F9F9")
        self.data_listbox_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.data_listbox = tk.Listbox(self.data_listbox_frame, height=8, bg="#F9F9F9",
                                      relief="flat", borderwidth=0, highlightthickness=0, font=("Arial", 14))
        self.data_listbox.pack(fill="both", expand=True)
        self.data_listbox.drop_target_register(DND_FILES)
        self.data_listbox.dnd_bind('<<Drop>>', self.drop_data_files)
        self.data_menu = tk.Menu(self.data_listbox, tearoff=0, font=("Arial", 12))
        self.data_menu.add_command(label="Удалить", command=self.delete_data_file)
        self.data_listbox.bind("<Button-3>", self.show_data_menu)
        self.data_buttons_frame = ctk.CTkFrame(self.data_container, fg_color="#FFFFFF")
        self.data_buttons_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.add_data_button = ctk.CTkButton(self.data_buttons_frame, text="Добавить", font=("Arial", 14),
                                           command=self.add_data_files, width=100, height=32, corner_radius=8)
        self.add_data_button.pack(side="left", padx=(0, 5))
        self.clear_data_button = ctk.CTkButton(self.data_buttons_frame, text="Очистить", font=("Arial", 14),
                                             command=self.clear_data_files, width=100, height=32, corner_radius=8)
        self.clear_data_button.pack(side="left")

        # Временные настройки (часы поясов + лаг в секундах)
        self.timezone_frame = ctk.CTkFrame(self.main_frame, fg_color="#F7F7F9", corner_radius=0)
        self.timezone_frame.pack(fill="x", pady=(20, 10))

        self.timezone_inner_frame = ctk.CTkFrame(self.timezone_frame, fg_color="#F7F7F9", corner_radius=0)
        self.timezone_inner_frame.pack(anchor="center")

        self.gps_tz_label = ctk.CTkLabel(self.timezone_inner_frame, text="Часовой пояс GPS:", font=("Arial", 14), text_color="#555555")
        self.gps_tz_label.pack(side="left", padx=(0, 10))
        self.gps_tz = ctk.CTkComboBox(self.timezone_inner_frame, values=list(TIMEZONES.keys()), font=("Arial", 14),
                                    dropdown_font=("Arial", 12), width=200, corner_radius=8)
        self.gps_tz.set("Москва (+03:00)")
        self.gps_tz.pack(side="left", padx=10)

        self.instrument_tz_label = ctk.CTkLabel(self.timezone_inner_frame, text="Часовой пояс прибора:", font=("Arial", 14), text_color="#555555")
        self.instrument_tz_label.pack(side="left", padx=(20, 10))
        self.instrument_tz = ctk.CTkComboBox(self.timezone_inner_frame, values=list(TIMEZONES.keys()), font=("Arial", 14),
                                           dropdown_font=("Arial", 12), width=200, corner_radius=8)
        self.instrument_tz.set("Москва (+03:00)")
        self.instrument_tz.pack(side="left", padx=10)

        # Лаг трека (в секундах, допускаются отрицательные)
        self.lag_frame = ctk.CTkFrame(self.main_frame, fg_color="#F7F7F9", corner_radius=0)
        self.lag_frame.pack(fill="x", pady=(0, 10))
        self.lag_inner = ctk.CTkFrame(self.lag_frame, fg_color="#F7F7F9", corner_radius=0)
        self.lag_inner.pack(anchor="center")

        self.lag_label = ctk.CTkLabel(self.lag_inner, text="Лаг трека (сек.):", font=("Arial", 14), text_color="#555555")
        self.lag_label.pack(side="left", padx=(0, 10))
        self.lag_entry = ctk.CTkEntry(self.lag_inner, width=120, font=("Arial", 14))
        self.lag_entry.insert(0, "0")
        self.lag_entry.pack(side="left")

        # Фрейм выбора файла вывода
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="#F7F7F9", corner_radius=0)
        self.action_frame.pack(fill="x", pady=(10, 20))
        self.action_inner_frame = ctk.CTkFrame(self.action_frame, fg_color="#F7F7F9", corner_radius=0)
        self.action_inner_frame.pack(anchor="center")
        self.output_label = ctk.CTkLabel(self.action_inner_frame, text="Папка: не выбрана", font=("Arial", 14), text_color="#555555")
        self.output_label.pack(side="left", padx=(0, 10))
        self.select_output_button = ctk.CTkButton(self.action_inner_frame, text="Выбрать", font=("Arial", 14),
                                                command=self.select_output_file, width=100, height=32, corner_radius=8)
        self.select_output_button.pack(side="left")

        self.status_label = ctk.CTkLabel(self.main_frame, text="Добавьте файлы для начала", font=("Arial", 14), text_color="#555555")
        self.status_label.pack(pady=(0, 15), anchor="center")
        self.process_button = ctk.CTkButton(self.main_frame, text="Обработать", font=("Arial", 16, "bold"),
                                          command=self.process_files, height=40, corner_radius=10)
        self.process_button.pack(anchor="center")

        self.coord_files = []
        self.coord_types = []
        self.data_files = []
        self.output_dir = None
        self.output_filename = None

    # --- Вспомогательные методы GUI ---
    def check_coord_file_type(self, file_path, gps_timezone=None):
        print(f"Checking file type for: {file_path}")
        if file_path.lower().endswith('.gpx'):
            return 'gps'
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline().strip().split(',')
                if len(first_line) == 3:
                    try:
                        int(first_line[0]); float(first_line[1]); float(first_line[2])
                        return 'point_id'
                    except ValueError:
                        try:
                            float(first_line[0]); float(first_line[1])
                            time_str = first_line[2].strip()
                            if time_str.endswith('Z'):
                                if '.' in time_str:
                                    datetime.strptime(time_str[:-1], '%Y-%m-%dT%H:%M:%S.%f')
                                else:
                                    datetime.strptime(time_str[:-1], '%Y-%m-%dT%H:%M:%S')
                            else:
                                if '.' in time_str:
                                    datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')
                                else:
                                    datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
                            return 'gps'
                        except (ValueError, AttributeError):
                            return None
        except Exception as e:
            print(f"Ошибка проверки типа файла {file_path}: {e}")
            return None
        return None

    def show_coord_menu(self, event):
        if self.coord_listbox.size() > 0:
            self.coord_listbox.select_set(self.coord_listbox.nearest(event.y))
            self.coord_menu.post(event.x_root, event.y_root)

    def show_data_menu(self, event):
        if self.data_listbox.size() > 0:
            self.data_listbox.select_set(self.data_listbox.nearest(event.y))
            self.data_menu.post(event.x_root, event.y_root)

    def delete_coord_file(self):
        selected = self.coord_listbox.curselection()
        if selected:
            index = selected[0]
            print(f"Deleting coord file at index {index}: {self.coord_files[index]}")
            self.coord_listbox.delete(index)
            self.coord_files.pop(index)
            self.coord_types.pop(index)
            self.update_status()

    def delete_data_file(self):
        selected = self.data_listbox.curselection()
        if selected:
            index = selected[0]
            print(f"Deleting data file at index {index}: {self.data_files[index]}")
            self.data_listbox.delete(index)
            self.data_files.pop(index)
            self.update_status()

    def clear_coord_files(self):
        self.coord_listbox.delete(0, tk.END)
        self.coord_files.clear()
        self.coord_types.clear()
        self.update_status()

    def clear_data_files(self):
        self.data_listbox.delete(0, tk.END)
        self.data_files.clear()
        self.update_status()

    def update_status(self):
        if not self.coord_files and not self.data_files:
            self.status_label.configure(text="Добавьте файлы для начала")
            self.gps_tz.configure(values=list(TIMEZONES.keys()))
            self.gps_tz.set("Москва (+03:00)")
        else:
            gps_count = sum(1 for t in self.coord_types if t == 'gps')
            point_id_count = len(self.coord_files) - gps_count
            self.status_label.configure(text=f"GPS: {gps_count}, Point-ID: {point_id_count}, Прибор: {len(self.data_files)}")
            if gps_count > 0:
                self.gps_tz.configure(values=list(TIMEZONES.keys()))
                self.gps_tz.set("Москва (+03:00)")
            else:
                self.gps_tz.configure(values=list(TIMEZONES_WITH_NONE.keys()))
                self.gps_tz.set("Не указывать")

    def add_coord_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите файлы координат",
            filetypes=[("GPX файлы", "*.gpx"), ("TXT файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        print(f"Selected coord files via dialog: {files}")
        for file in files:
            if file not in self.coord_files:
                coord_type = self.check_coord_file_type(file)
                if coord_type is None:
                    messagebox.showerror("Ошибка", f"Файл {os.path.basename(file)} не соответствует формату")
                    continue
                self.coord_files.append(file)
                self.coord_types.append(coord_type)
                self.coord_listbox.insert(tk.END, os.path.basename(file))
                if any(t == 'gps' for t in self.coord_types):
                    self.gps_tz.configure(values=list(TIMEZONES.keys()))
                    self.gps_tz.set("Москва (+03:00)")
                else:
                    self.gps_tz.configure(values=list(TIMEZONES_WITH_NONE.keys()))
                    self.gps_tz.set("Не указывать")
        self.update_status()

    def add_data_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите файлы прибора",
            filetypes=[("TXT файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        print(f"Selected data files via dialog: {files}")
        new_files = [f for f in files if f not in self.data_files]
        self.data_files.extend(new_files)
        self.data_listbox.delete(0, tk.END)
        for file in self.data_files:
            self.data_listbox.insert(tk.END, os.path.basename(file))
        self.update_status()

    def drop_coord_file(self, event):
        files = self.tk.splitlist(event.data)
        print(f"Dropped coord files: {files}")
        for file in files:
            if file not in self.coord_files:
                coord_type = self.check_coord_file_type(file)
                if coord_type is None:
                    messagebox.showerror("Ошибка", f"Файл {os.path.basename(file)} не соответствует формату")
                    continue
                self.coord_files.append(file)
                self.coord_types.append(coord_type)
                self.coord_listbox.insert(tk.END, os.path.basename(file))
                if any(t == 'gps' for t in self.coord_types):
                    self.gps_tz.configure(values=list(TIMEZONES.keys()))
                    self.gps_tz.set("Москва (+03:00)")
                else:
                    self.gps_tz.configure(values=list(TIMEZONES_WITH_NONE.keys()))
                    self.gps_tz.set("Не указывать")
        self.update_status()

    def drop_data_files(self, event):
        files = self.tk.splitlist(event.data)
        print(f"Dropped data files: {files}")
        new_files = [f for f in files if f not in self.data_files]
        self.data_files.extend(new_files)
        self.data_listbox.delete(0, tk.END)
        for file in self.data_files:
            self.data_listbox.insert(tk.END, os.path.basename(file))
        self.update_status()

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Выберите папку и имя файла",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")],
            initialfile="output"
        )
        if file_path:
            self.output_dir = os.path.dirname(file_path)
            self.output_filename = os.path.basename(file_path)
            self.output_label.configure(text=f"Папка: {os.path.basename(self.output_dir)}")
            self.status_label.configure(text="Папка выбрана")

    def process_files(self):
        if not self.coord_files:
            messagebox.showerror("Ошибка", "Файлы координат не загружены")
            return
        if not self.data_files:
            messagebox.showerror("Ошибка", "Файлы прибора не загружены")
            return
        if not self.output_dir or not self.output_filename:
            messagebox.showerror("Ошибка", "Папка не выбрана")
            return

        # Лаг трека (секунды). Любой некорректный ввод -> 0.
        try:
            lag_seconds = int(self.lag_entry.get().strip())
        except Exception:
            lag_seconds = 0

        is_gps = any(coord_type == 'gps' for coord_type in self.coord_types)
        if not is_gps and len(self.coord_files) != len(self.data_files):
            messagebox.showerror("Ошибка", "Количество файлов координат и файлов прибора должно совпадать")
            return

        self.status_label.configure(text="Обработка...")
        self.process_button.configure(state="disabled")

        instrument_tz = TIMEZONES[self.instrument_tz.get()]
        gps_tz = TIMEZONES.get(self.gps_tz.get(), None)

        success_count = 0

        if is_gps:
            # Собираем все GPS-координаты (GPX и TXT-GPS) с учётом лага (сек)
            all_gpx_coords = []
            all_txt_coords = {}
            for coord_file, coord_type in zip(self.coord_files, self.coord_types):
                if coord_type == 'gps':
                    if coord_file.lower().endswith('.gpx'):
                        coords = parse_gpx_file(coord_file, gps_tz, lag_seconds=lag_seconds)
                        all_gpx_coords.extend(coords)
                    else:
                        coords = read_txt_coord_file(coord_file, gps_timezone=gps_tz, lag_seconds=lag_seconds)
                        all_txt_coords.update(coords)

            if not all_gpx_coords and not all_txt_coords:
                messagebox.showerror("Ошибка", "Не удалось прочитать файлы координат")
                self.status_label.configure(text="Ошибка")
                self.process_button.configure(state="normal")
                return

            for i, data_file in enumerate(self.data_files):
                base, ext = os.path.splitext(self.output_filename)
                output_filename = f"{base}_{i+1}{ext}" if len(self.data_files) > 1 else self.output_filename
                output_path = os.path.join(self.output_dir, output_filename)
                if process_file(data_file, all_txt_coords, all_gpx_coords, output_path, instrument_tz, is_gps=True):
                    success_count += 1

        else:
            # Режим point_id → лаг не применяется (он про трек)
            for i, (coord_file, data_file) in enumerate(zip(self.coord_files, self.data_files)):
                coords = read_txt_coord_file(coord_file, None)
                gpx_coords = []
                if not coords:
                    messagebox.showerror("Ошибка", f"Не удалось прочитать TXT-файл: {os.path.basename(coord_file)}")
                    self.status_label.configure(text="Ошибка")
                    self.process_button.configure(state="normal")
                    return
                base, ext = os.path.splitext(self.output_filename)
                output_filename = f"{base}_{i+1}{ext}" if len(self.data_files) > 1 else self.output_filename
                output_path = os.path.join(self.output_dir, output_filename)
                if process_file(data_file, coords, gpx_coords, output_path, instrument_tz, is_gps=False):
                    success_count += 1

        self.status_label.configure(text=f"Обработано {success_count}/{len(self.data_files)} файлов")
        self.process_button.configure(state="normal")
        messagebox.showinfo("Успех", f"Обработано {success_count} файлов. Файлы сохранены в {self.output_dir}")

if __name__ == "__main__":
    try:
        app = DopplerApp()
        app.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        raise
