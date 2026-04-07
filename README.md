# ADCP Coordinate Replacer / Обработчик координат профилографа

**[English](#english) | [Русский](#русский)**

---

<a name="english"></a>
## English

### What it does

Acoustic Doppler profilers (ADCP) embed GPS coordinates directly into their output files. When the instrument cannot get a GPS fix, it writes placeholder values (`30000.0000000`) instead of real coordinates. This tool replaces those placeholder coordinates with precise positions from an external GPS track, matched by timestamp.

### Features

- Supports **GPX tracks** (Garmin and compatible devices)
- Supports **timestamped TXT** tracks (`lat,lon,ISO8601time`)
- Supports **point-ID TXT** files (`point_id,lat,lon`) for static stations
- Batch processing of **multiple instrument files** at once
- Independent **timezone** settings for GPS and instrument clocks
- **Track lag correction** in seconds (positive or negative) to compensate for clock desync
- Drag-and-drop file loading
- Simple GUI, no command line required

### Requirements

- Python 3.8+
- Windows (tested); macOS/Linux should work with minor adjustments

### Installation

```
pip install customtkinter tkinterdnd2 pytz
python app.py
```

Or download the prebuilt **[Windows executable](../../releases/latest)** — no Python needed.

### Instrument file format

Each measurement block in the instrument file looks like this:

```
25 5 3 7 29 38 23  28  1  -2.260  -1.910  98.160  4.380
25.11  -9.27  -1.13  0.14  0.00  0.00  0.00  0.00  3.97  3.76  3.63  4.02
0.00         0.00         0.00         0.00         0.00
30000.0000000 30000.0000000 -32768   -32768         0.0    ← coordinates here
-0.0  -0.0  -0.0  0.0  0.0  0.0  0.0  0.30  2.85
20 cm BT dB 0.46  0.150
  0.30   60.09   215.46  ...
```

The first line contains the timestamp (`YY MM DD HH mm SS cs`) and point ID. The coordinate line is the **second 5-column numeric line** in the block. When the built-in GPS has no fix, it contains `30000.0000000` as placeholder values — this tool replaces them with coordinates from the external GPS track.

### Coordinate file formats

**GPX** — standard GPS track exported from Garmin, OsmAnd, etc.

**TXT timestamped:**
```
55.123456,48.654321,2025-05-15T10:23:45Z
55.123490,48.654400,2025-05-15T10:23:46Z
```

**TXT point-ID:**
```
1,55.123456,48.654321
2,55.124000,48.655000
```

### How to use

1. Run `app.py` or the `.exe`
2. Add **coordinate files** (GPX or TXT) to the left panel
3. Add **instrument files** (TXT) to the right panel
4. Set the correct **timezone** for GPS and instrument
5. Set **track lag** if clocks are out of sync (e.g. `-5` means GPS is 5 s behind)
6. Choose an output file
7. Click **Обработать**

When processing multiple instrument files, outputs are saved with `_1`, `_2`, ... suffixes.

### Matching logic

Each measurement timestamp is converted to UTC and matched against the GPS track. The closest GPS point within **±10 seconds** is used. If no match is found, the original line is kept unchanged.

---

<a name="русский"></a>
## Русский

### Назначение

Акустические доплеровские профилографы (ADCP) записывают GPS-координаты непосредственно в выходные файлы. Если прибор не поймал сигнал GPS, вместо координат записываются значения-заглушки (`30000.0000000`). Эта программа заменяет такие заглушки на точные координаты из внешнего GPS-трека, сопоставляя записи по времени.

### Возможности

- Поддержка **GPX-треков** (Garmin и совместимые устройства)
- Поддержка **TXT-треков с временными метками** (`lat,lon,ISO8601time`)
- Поддержка **TXT-файлов по номерам точек** (`point_id,lat,lon`) для стационарных наблюдений
- Пакетная обработка **нескольких файлов прибора** за один раз
- Независимая настройка **часового пояса** для GPS и прибора
- **Коррекция лага трека** в секундах (положительная или отрицательная) для компенсации рассинхронизации часов
- Загрузка файлов перетаскиванием (drag & drop)
- Простой графический интерфейс, командная строка не нужна

### Требования

- Python 3.8+
- Windows (протестировано); macOS/Linux — с незначительными поправками

### Установка

```
pip install customtkinter tkinterdnd2 pytz
python app.py
```

Или скачайте готовый **[исполняемый файл для Windows](../../releases/latest)** — Python не нужен.

### Формат файлов прибора

Каждый блок измерения в файле прибора выглядит так:

```
25 5 3 7 29 38 23  28  1  -2.260  -1.910  98.160  4.380
25.11  -9.27  -1.13  0.14  0.00  0.00  0.00  0.00  3.97  3.76  3.63  4.02
0.00         0.00         0.00         0.00         0.00
30000.0000000 30000.0000000 -32768   -32768         0.0    ← координаты здесь
-0.0  -0.0  -0.0  0.0  0.0  0.0  0.0  0.30  2.85
20 cm BT dB 0.46  0.150
  0.30   60.09   215.46  ...
```

Первая строка содержит временну́ю метку (`YY MM DD HH mm SS cs`) и номер точки. Строка с координатами — **вторая строка из пяти чисел** в блоке. Когда встроенный GPS не поймал сигнал, там стоят значения `30000.0000000` — программа заменяет их на координаты из внешнего трека.

### Форматы файлов координат

**GPX** — стандартный трек, экспортированный из Garmin, OsmAnd и др.

**TXT с временными метками:**
```
55.123456,48.654321,2025-05-15T10:23:45Z
55.123490,48.654400,2025-05-15T10:23:46Z
```

**TXT по номерам точек:**
```
1,55.123456,48.654321
2,55.124000,48.655000
```

### Использование

1. Запустить `app.py` или `.exe`
2. Добавить **файлы координат** (GPX или TXT) в левую панель
3. Добавить **файлы прибора** (TXT) в правую панель
4. Задать корректный **часовой пояс** для GPS и прибора
5. При необходимости задать **лаг трека** (например, `-5` — GPS отстаёт на 5 с)
6. Выбрать выходной файл
7. Нажать **Обработать**

При обработке нескольких файлов прибора к именам выходных файлов добавляются суффиксы `_1`, `_2`, ...

### Логика сопоставления

Временна́я метка каждого измерения переводится в UTC и сопоставляется с треком GPS. Используется ближайшая точка трека в пределах **±10 секунд**. Если подходящая точка не найдена — исходная строка остаётся без изменений.

---

## License / Лицензия

MIT — see [LICENSE](LICENSE)
