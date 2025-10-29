rm -rf ../src/__pycache__
rm -rf ../src/logs
rm -rf ../src/__init__.py
pyinstaller --distpath "osu-parser" --debug imports --noconfirm --onefile --windowed --uac-admin --icon "../src/assets/icons/application.ico" --name "osu-parser" --add-data "../src;."  "../src/main.pyw"
touch ../src/__init__.py
rm -rf build
rm -rf osu-parser.spec