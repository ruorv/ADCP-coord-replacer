# ADCP Coordinate Replacer / Замена координат ADCP

**[English](#english) | [Русский](#русский)**

---

<a name="english"></a>
## 🇬🇧 English

### What it does

The Teledyne RDI RiverRay ADCP records GPS coordinates directly into its ASCII output files. However, the built-in GPS can be inaccurate — especially in narrow channels, under dense vegetation, or when the DGPS signal is weak.

This tool replaces the embedded coordinates in RiverRay ASCII files with precise coordinates from an external GPS track, matched by timestamp.

### Features

- Supports **GPX tracks** (Garmin, OsmAnd, and other GPS apps)
- Supports **timestamped TXT** GPS tracks (`lat,lon,ISO8601time`)
- Supports **point-ID TXT** files (`point_id,lat,lon`) — for fixed measurement stations
- Processes **multiple instrument files** in one batch
- Configurable **timezone** for GPS device and ADCP independently
- **Track lag correction** (seconds, positive or negative) — compensates for clock offset between GPS and ADCP
- Drag-and-drop file loading
- No command line needed

### Requirements

- Python 3.8+
- Windows (tested); macOS/Linux should work with minor adjustments

### Installation

```bash
pip install customtkinter tkinterdnd2 pytz
python app.py
```

Or download the prebuilt **[Windows executable →](../../releases/latest)**

### Step-by-step usage

1. **Run** `app.py` or the `.exe`
2. **Add GPS coordinate files** to the left panel (drag & drop, or click "Добавить")
3. **Add ADCP instrument files** to the right panel
4. **Set the timezone** for the GPS device and for the ADCP separately
5. **Set track lag** if the GPS clock and ADCP clock are out of sync  
   *(e.g. `-5` means GPS is 5 seconds behind the ADCP)*
6. **Choose output folder and filename**
7. **Click "Обработать"** (Process)

When processing multiple instrument files, output files are named `output_1.txt`, `output_2.txt`, etc.

### Input file formats

#### GPS coordinate files

**GPX** — standard GPS track. Export from Garmin Connect, OsmAnd, Strava, etc.

Example from `examples/gps_track_example.gpx` (Organic Maps export):
```xml
<trkpt lat="61.665590" lon="50.835940">
  <time>2025-05-03T09:51:10Z</time>
</trkpt>
```

**TXT with timestamps** (`lat,lon,ISO8601time`):
```
61.665590,50.835940,2025-05-03T09:51:10Z
61.665620,50.835980,2025-05-03T09:51:11Z
```

**TXT with point IDs** (`point_id,lat,lon`):
```
1,61.665590,50.835940
2,61.665620,50.835980
```
Use this format when each transect has a fixed station number that matches the ADCP file.

#### ADCP instrument files (RiverRay ASCII)

Each measurement ensemble starts with a header line (date/time + point ID), followed by data lines. The tool replaces coordinates on the **second 5-column numeric line** of each ensemble:

```
25 5 3 7 29 38 23    28      1   -2.260   -1.910   98.160    4.380
                                  ↑ lon     ↑ lat   ← these get replaced
```
Line format: `YY MM DD HH mm SS cs  point_id  channel  lon  lat  ...`

### Matching logic

Each ensemble timestamp is converted to UTC and matched to the nearest GPS point within **±10 seconds**. If no GPS point is found within this window, the original coordinates are left unchanged.

### Examples

See the `examples/` folder:
- `gps_track_example.gpx` — real GPX track recorded with Organic Maps
- `instrument_example.txt` — real RiverRay ASCII output file (excerpt)

---

<a name="русский"></a>
## 🇷🇺 Русский

### Назначение

Профилограф Teledyne RDI RiverRay ADCP записывает GPS-координаты непосредственно в ASCII-файлы выходных данных. Однако встроенный GPS может давать неточные результаты — особенно в узких протоках, под густой растительностью или при слабом сигнале DGPS.

Эта программа заменяет встроенные координаты в ASCII-файлах RiverRay на точные координаты из внешнего GPS-трека, сопоставляя их по времени.

### Возможности

- Поддержка **GPX-треков** (Garmin, OsmAnd и другие GPS-приложения)
- Поддержка **TXT-треков с временными метками** (`lat,lon,ISO8601time`)
- Поддержка **TXT-файлов по номерам точек** (`point_id,lat,lon`) — для фиксированных створов
- Пакетная обработка **нескольких файлов прибора** за один раз
- Независимая настройка **часового пояса** для GPS и прибора
- **Коррекция лага трека** (в секундах, положительная или отрицательная) — компенсирует рассинхронизацию часов GPS и ADCP
- Загрузка файлов перетаскиванием (drag & drop)
- Графический интерфейс, командная строка не нужна

### Требования

- Python 3.8+
- Windows (протестировано); macOS/Linux — с незначительными поправками

### Установка

```bash
pip install customtkinter tkinterdnd2 pytz
python app.py
```

Или скачайте готовый **[исполняемый файл для Windows →](../../releases/latest)**

### Пошаговая инструкция

1. **Запустите** `app.py` или `.exe`
2. **Добавьте файлы GPS** в левую панель — перетащите или нажмите «Добавить»
3. **Добавьте файлы ADCP** в правую панель
4. **Задайте часовой пояс** отдельно для GPS и для прибора
5. **Задайте лаг трека**, если часы GPS и ADCP рассинхронизированы  
   *(например, `-5` означает, что GPS отстаёт от прибора на 5 секунд)*
6. **Выберите папку и имя выходного файла**
7. **Нажмите «Обработать»**

При обработке нескольких файлов к именам добавляются суффиксы: `output_1.txt`, `output_2.txt` и т.д.

### Форматы входных файлов

#### Файлы координат GPS

**GPX** — стандартный формат GPS-трека. Экспорт из Garmin Connect, OsmAnd, Strava и др.

Пример из `examples/gps_track_example.gpx` (экспорт Organic Maps):
```xml
<trkpt lat="61.665590" lon="50.835940">
  <time>2025-05-03T09:51:10Z</time>
</trkpt>
```

**TXT с временными метками** (`lat,lon,ISO8601time`):
```
61.665590,50.835940,2025-05-03T09:51:10Z
61.665620,50.835980,2025-05-03T09:51:11Z
```

**TXT по номерам точек** (`point_id,lat,lon`):
```
1,61.665590,50.835940
2,61.665620,50.835980
```
Используется, если каждый створ имеет фиксированный номер, совпадающий с номером в файле прибора.

#### Файлы прибора (RiverRay ASCII)

Каждый ансамбль начинается строкой-заголовком (дата/время + номер точки), за которой следуют строки данных. Программа заменяет координаты на **второй строке из 5 чисел** каждого ансамбля:

```
25 5 3 7 29 38 23    28      1   -2.260   -1.910   98.160    4.380
                                   ↑ lon    ↑ lat   ← заменяются
```
Формат строки: `YY MM DD HH mm SS cs  point_id  channel  lon  lat  ...`

### Логика сопоставления

Временна́я метка каждого ансамбля переводится в UTC и сопоставляется с ближайшей точкой GPS-трека в пределах **±10 секунд**. Если подходящая точка не найдена — исходные координаты сохраняются без изменений.

### Примеры

Папка `examples/`:
- `gps_track_example.gpx` — реальный GPX-трек, записанный в Organic Maps
- `instrument_example.txt` — реальный фрагмент ASCII-файла RiverRay ADCP

---

## License / Лицензия

MIT License — Copyright (c) 2026 Александр Иннокентьев  
See [LICENSE](LICENSE)
