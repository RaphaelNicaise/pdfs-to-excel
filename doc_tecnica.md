- Compilar archivo .py a .exe
```bash
pyinstaller --onefile --noconsole --add-data "assets/icon.ico:assets"  --icon=assets/icon.ico --name "PDFaExcel" main.py
```