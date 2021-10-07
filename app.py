from logging import root
from flask import Flask, render_template, request
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
    # Home page of the management system

@app.route('/donate')
def donate():
    # return "Donate 👐"
    return render_template('donate.html')
    # Code to write data into database here

@app.route('/request')
def ask():
    return "Request 🩸"
    # Code to read data from database here

@app.route('/donate_success', methods=['POST'])
def donate_success():
    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    verification = 1 if request.form.get('verification') == "yes" else 0
    query = 'INSERT INTO DONOR VALUES ("' + request.form.get('first_name') + '", "' + request.form.get('last_name') + '", "' + sex + '", "' + request.form.get('city') + '", "' + request.form.get('locality') + '", "' + request.form.get('phone') + '", "' + request.form.get('aadhar') + '", "' + request.form.get('blood_group') + '", "' + str(blood_polarity) + '", "' + str(verification) + '")'
    cursor.execute(query)
    conn.commit()
    return render_template('success.html')

if __name__ == "__main__":
    app.run(debug = True)