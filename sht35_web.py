from flask import Flask, jsonify, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def get_latest_reading():
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="By8Hq2Ze",
    database="sht35db"
)



    cursor = db.cursor()
    cursor.execute("SELECT timestamp, temperature, humidity FROM readings ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return {
            "timestamp": row[0].strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(row[1], 2),
            "humidity": round(row[2], 2)
        }
    else:
        return {}

@app.route("/latest_reading")
def latest_reading():
    data = get_latest_reading()
    return jsonify(data)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

