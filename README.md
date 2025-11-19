# N-ttj-nst-YP

Vad jag har gjort hittills

Jag har byggt ett system som läser av temperatur och luftfuktighet från en SHT35-sensor via I2C på en BeagleBone Black och loggar data både till en fil och till en MySQL/MariaDB-databas. Sedan visar jag datan på en webbsida med hjälp av Flask.

Steg för steg – så här har jag fått allt att fungera
1. Skapa en virtuell miljö och installera nödvändiga Python-paket

För att hålla allt rent och organiserat skapade jag en Python virtuell miljö för projektet:
python3 -m venv sht35_venv
source sht35_venv/bin/activate

När miljön var aktiv installerade jag alla bibliotek som behövdes:
pip install smbus2 mysql-connector-python flask

2. Skriva Python-skriptet för att läsa av SHT35-sensorn (sht35.py)

Jag skrev ett Python-skript som läser temperatur och luftfuktighet från SHT35 via I2C. Skriptet gör en CRC-kontroll för att säkerställa datakvalitet och skriver sedan värdena med tidsstämpel till en loggfil /home/debian/sht35.log.

För att testa körde jag:
python3 sht35.py

och verifierade att värdena skrivs ut i terminalen.

3. Skapa och aktivera systemd-tjänst för automatisk start (sht35.service)

Jag skrev en systemd-servicefil för att köra sht35.py som bakgrundstjänst och få den att starta automatiskt vid uppstart. Filen placerades i /etc/systemd/system/sht35.service:

[Unit]
Description=SHT35 Temperature/Humidity Logger
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/debian/sht35.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

Sedan laddade jag om systemd och startade tjänsten:
sudo systemctl daemon-reload
sudo systemctl enable sht35.service
sudo systemctl start sht35.service

Jag kontrollerade status och loggar med:
sudo systemctl status sht35.service
sudo journalctl -u sht35.service -f

4. Installera och konfigurera MariaDB

För att spara mätdata i en databas installerade jag MariaDB-server:
sudo apt update
sudo apt install mariadb-server

Jag loggade in i databasen och skapade en databas och en tabell för mätdata:
CREATE DATABASE sht35db;
USE sht35db;
CREATE TABLE readings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timestamp DATETIME NOT NULL,
  temperature FLOAT NOT NULL,
  humidity FLOAT NOT NULL
);
CREATE USER 'sht35user'@'localhost' IDENTIFIED BY 'By8Hq2Ze';
GRANT ALL PRIVILEGES ON sht35db.* TO 'sht35user'@'localhost';
FLUSH PRIVILEGES;

5. Modifiera Python-skriptet för att skriva till databasen

Jag uppdaterade sht35.py så att den inte bara loggar till fil, utan även skriver temperatur och luftfuktighet till databasen direkt efter varje mätning.

Efter det testade jag med SQL-frågor för att se att data faktiskt lagrades:
SELECT * FROM readings ORDER BY timestamp DESC LIMIT 10;

6. Skapa webbserver med Flask för att visa data (sht35_web.py)

Jag skrev ett Flask-baserat webbskript som hämtar och visar de senaste mätvärdena från databasen på en enkel webbsida.

Jag startade servern med:
python3 sht35_web.py

Sedan öppnade jag webbläsaren på http://<beaglebone-ip>:8000 för att se datan.

7. Hantera portkonflikt

När jag skulle starta Flask-servern första gången fick jag felmeddelande att port 8000 redan var upptagen.

Jag kontrollerade vilken process som använde porten:
sudo lsof -i :8000

Och dödade den processen med:

sudo kill -9 <PID>

Efter det kunde jag starta Flask-servern utan problem.

| Används till att:                 | Kommando/exempel:                                                               |
| --------------------------------- | ------------------------------------------------------------------------------ |
| Skapa virtuell miljö              | `python3 -m venv sht35_venv`                                                   |
| Aktivera virtuell miljö           | `source sht35_venv/bin/activate`                                               |
| Installera Python-paket           | `pip install smbus2 mysql-connector-python flask`                              |
| Köra skript direkt                | `python3 sht35.py`                                                             |
| Skapa systemd-tjänstfil           | Placera `sht35.service` i `/etc/systemd/system/`                               |
| Ladda om systemd                  | `sudo systemctl daemon-reload`                                                 |
| Aktivera och starta tjänst        | `sudo systemctl enable sht35.service` och `sudo systemctl start sht35.service` |
| Kontrollera tjänststatus          | `sudo systemctl status sht35.service`                                          |
| Visa tjänstloggar                 | `sudo journalctl -u sht35.service -f`                                          |
| Installera MariaDB                | `sudo apt install mariadb-server`                                              |
| Logga in i MariaDB                | `sudo mysql`                                                                   |
| Skapa databas och tabell          | Se SQL-kommandon ovan                                                          |
| Starta Flask-webbserver           | `python3 sht35_web.py`                                                         |
| Kontrollera port och döda process | `sudo lsof -i :8000` och `sudo kill -9 <PID>`                                  |

8. Skapa en Nginx-reverse proxy för Flask-applikationen

För att göra Flask-webbservern tillgänglig via standard HTTP-porten 80 (så att man slipper skriva portnummer i webbläsaren) skapade vi en Nginx-konfiguration som proxyar all trafik från port 80 till Flask-applikationen som körs på port 8000.

Vi skapade en Nginx site-fil /etc/nginx/sites-available/sht35 som pekar om all trafik till http://127.0.0.1:8000.

Denna site aktiverades genom en symbolisk länk i /etc/nginx/sites-enabled/.

Efter konfigurationsändringen startades Nginx om för att ändringarna skulle börja gälla.

Det gör att du nu kan nå Flask-applikationen via http://<beaglebone-ip>/ istället för att behöva ange port 8000.

9. Bygga en frontend-tabell för visning av sensorvärden

Vi skapade en tabell i HTML (placerad i index.html) som hämtar temperatur- och fuktighetsdata i JSON-format från Flask-servern.

Data visas i tabellen när sidan laddas om.

Tabellens rader byggs dynamiskt med JavaScript som parsar JSON-data och fyller tabellen med aktuell mätdata från sensorerna.

Det här gör att användaren enkelt kan se mätvärdena direkt på webbsidan utan att behöva läsa rå JSON.

10. Test och verifiering

Bekräftade att sidan laddas på port 80 och visar tabellen med data.

Kontrollerade att Flask-applikationen fungerar som den ska bakom Nginx-reverse proxyn.

Säkerställde att all data från SHT35 sensorn presenteras korrekt i tabellen på webbsidan.

Kort sammanfattning
Åtgärd	Vad det innebär
Nginx proxy till Flask	Gör Flask-applikationen tillgänglig via port 80
Frontend HTML-tabell	Visar sensorvärden snyggt och läsbart i webbläsaren
Data uppdateras vid omladdning	Ny data hämtas från servern varje gång sidan laddas
