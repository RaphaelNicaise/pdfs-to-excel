- Compilar archivo .py a .exe
```bash
pyinstaller --onefile --noconsole --add-data "assets/icon.ico;assets" --add-data "assets/plantilla_detalle_operaciones.xlsx;assets" --add-data "assets/imagen.jpg;assets" --icon=assets/icon.ico --name "PDFaExcel" main.py
```