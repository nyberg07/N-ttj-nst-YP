# N-ttj-nst-YP

Vad jag har gjort hittills

Installerat nödvändiga Python-bibliotek för att läsa från SHT35-sensorn.

Skrivit ett Python-skript som läser temperatur och luftfuktighet från sensorn via I2C.

Testat skriptet och fått ut värden som visas i terminalen.

SHT35 Temperatur- och fuktighetslogger

Det här projektet innehåller ett Python-skript (sht35.py) som läser temperatur och luftfuktighet från en SHT35-sensor via I2C och loggar dessa värden till en fil med tidsstämplar.

Funktioner

Läser temperatur och luftfuktighet var 5:e sekund.

Sparar mätdata i en loggfil (sht35.log).

Körs som en systemd-tjänst (sht35.service) för automatisk start vid systemstart.

Tjänsten återstartas automatiskt vid eventuella fel.

Installation och användning

Kopiera sht35.py till /home/debian/ (eller önskad plats).

Placera systemd-tjänstfilen sht35.service i /etc/systemd/system/.

Kör följande kommandon för att aktivera och starta tjänsten:
sudo systemctl daemon-reload  
sudo systemctl enable sht35.service  
sudo systemctl start sht35.service  

Kontrollera status och loggar med:
sudo systemctl status sht35.service  
sudo journalctl -u sht35.service -f  

Loggfilen (sht35.log) kommer att finnas i samma katalog som skriptet och innehåller tidsstämplade mätvärden.

SHT35 Temperatursensor och Loggning

Nytt Python-script sht35.py som läser temperatur och luftfuktighet från SHT35-sensorn och loggar mätvärdena kontinuerligt till fil /home/debian/sht35.log.

Systemd-service sht35.service för att automatiskt starta och köra mätningen som en bakgrundsprocess vid uppstart.

Loggfilen uppdateras med tidsstämplade temperatur- och fuktighetsvärden för senare analys.

(Eventuell info om plotting-script om du har det.)
