try {
    Remove-Item -Path ..\code\__pycache__ -Force -Recurse
    Remove-Item -Path ..\code\logs -Force -Recurse
    Remove-Item -Path build -Force -Recurse
    Remove-Item -Path dist -Force -Recurse
    Remove-Item -Path osu-parser.spec -Force -Recurse
}
finally {
    pyinstaller --noconfirm --onefile --windowed --uac-admin --icon "..\code\assets\icons\application.ico" --name "osu-parser" --add-data "..\code;."  "..\code\main.pyw"
}
