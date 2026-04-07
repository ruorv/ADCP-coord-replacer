# Examples / Примеры

This folder contains sample input files for testing.

## coords_point_id.txt
Coordinate file in point-ID format: `point_id,lat,lon`  
Use this when each station has a fixed ID that matches the instrument file.

## coords_timestamped.txt
Coordinate file in timestamped format: `lat,lon,ISO8601time`  
Use this when coordinates come from a GPS logger with timestamps (no GPX).

---

**Note:** GPX files are excluded from the repository by `.gitignore`.  
To test with a real GPX track, export one from Garmin Connect, OsmAnd, or any GPS app.

---

Эта папка содержит примеры входных файлов для тестирования.

**Примечание:** GPX-файлы исключены из репозитория через `.gitignore`.  
Для тестирования с реальным треком — экспортируйте GPX из Garmin Connect, OsmAnd или любого GPS-приложения.
