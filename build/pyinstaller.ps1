try {
    Remove-Item -Path ..\code\__pycache__ -Force -Recurse
}
finally {
    pyinstaller --noconfirm --onefile --windowed --icon "..\code\assets\icons\application.ico" --name "osu-parser" --add-data "..\code;."  "..\code\main.pyw"
}
