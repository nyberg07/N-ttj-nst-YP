from flask import Flask, jsonify, render_template
import mysql.connector
from datetime import datetime

# Skapar en Flask-applikation
app = Flask(__name__)

def get_latest_reading():
    # Anslutning till MySQL-databasen
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="By8Hq2Ze",   # OBS: hårdkodade lösenord bör undvikas i riktig drift
        database="sht35db"
    )

    # Skapar en cursor som låter oss köra SQL-frågor
    cursor = db.cursor()

    # Hämtar den senaste posten baserat på timestamp
    cursor.execute(
        "SELECT timestamp, temperature, humidity "
        "FROM readings ORDER BY timestamp DESC LIMIT 1"
    )

    # Tar ut första (och enda) raden
    row = cursor.fetchone()

    # Stänger anslutning och cursor
    cursor.close()
    db.close()

    # Om en rad finns returneras den formaterad
    if row:
        return {
            "timestamp": row[0].strftime("%Y-%m-%d %H:%M:%S"),  # formaterar datum
            "temperature": round(row[1], 2),  # avrundar temperatur
            "humidity": round(row[2], 2)      # avrundar luftfuktighet
        }
    else:
        # Om databasen är tom returneras ett tomt objekt
        return {}

# API-endpoint som returnerar senaste mätvärdet i JSON-format
@app.route("/latest_reading")
def latest_reading():
    data = get_latest_reading()
    return jsonify(data)

# Huvudsida — renderar en HTML-mall
@app.route("/")
def index():
    return render_template("index.html")

# Startar Flask-servern om filen körs direkt
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
