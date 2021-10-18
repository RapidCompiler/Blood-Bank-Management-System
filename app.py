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

@app.route('/donate', methods=['GET'])
def donate():
    # return "Donate 👐"
    return render_template('donate.html')

@app.route('/request', methods=['GET'])
def ask():
    return render_template('request.html')
    # Code to read data from database here

@app.route('/req_process', methods=['POST'])
def req_process():
    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    query = 'INSERT INTO REQUEST VALUES ("' + request.form.get('first_name').title() + '", "' + request.form.get('last_name').title() + '", "' + sex + '", "' + request.form.get('city').title() + '", "' + request.form.get('locality').title() + '", "' + request.form.get('phone') + '", "' + request.form.get('aadhar') + '","' + request.form.get('issue') + '", "' + request.form.get('v_id') + '","' + request.form.get('blood_group') + '", "' + str(blood_polarity) + '", "' + request.form.get('hosp_name') + '","' + request.form.get('hosp_locality') + '","' + request.form.get('hosp_city') + '","' + request.form.get('hosp_pin') + '")'
    cursor.execute(query)
    conn.commit()
    query='SELECT phone FROM DONOR WHERE blood_group="' + request.form.get('blood_group') + '" AND blood_polarity="' + str(blood_polarity) +'"'
    x=cursor.execute(query)
    x=cursor.fetchone()
    print(x)
    # print("The number of matching Blood Donors is: {0}".format(x))
    query='SELECT phone FROM DONOR WHERE blood_group="' + request.form.get('blood_group') + '" AND blood_polarity="' + str(blood_polarity) +'" AND locality="'+request.form.get('hosp_locality')+ '"'
    # query='SELECT COUNT(*) WHERE locality="' +request.form.get('hosp_locality')+ '" IN (SELECT * FROM DONOR WHERE blood_group="' + request.form.get('blood_group') + '" AND blood_polarity="' + str(blood_polarity) +'")'
    x=cursor.execute(query)
    x=cursor.fetchone()
    print(x)
    # print("The number of Blood Donors in close vicinity is: {0}".format(x))
    conn.commit()
    return render_template('req_process.html')


@app.route('/donate_success', methods=['POST'])
def donate_success():
    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    verification = 1 if request.form.get('verification') == "yes" else 0
    query = 'INSERT INTO DONOR VALUES ("' + request.form.get('first_name').title() + '", "' + request.form.get('last_name').title() + '", "' + sex + '", "' + request.form.get('city').title() + '", "' + request.form.get('locality').title() + '", "' + request.form.get('phone') + '", "' + request.form.get('aadhar') + '", "' + request.form.get('blood_group') + '", "' + str(blood_polarity) + '", "' + str(verification) + '")'
    cursor.execute(query)
    conn.commit()
    return render_template('success.html')
    
if __name__ == "__main__":
    app.run(debug = True)