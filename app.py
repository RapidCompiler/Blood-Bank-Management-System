from logging import root
import re
from flask import Flask, render_template, request, session, redirect
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os
import boto3

load_dotenv()

# Initializing connection to AWS SNS Client
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
client = boto3.client(
    "sns",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="us-east-1"
)

# Setting up flask and mysql connection parameters
app = Flask(__name__)
app.secret_key = "applepie"
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
mysql = MySQL()
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

# Home page of the management system
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def locality():
    query="SELECT * from city"
    cursor.execute(query)
    city = [i[0] for i in cursor.fetchall()]
    
    query = "select locality, pin from locality"
    cursor.execute(query)
    locality = [(i[0], i[1]) for i in cursor.fetchall()]
    
    return(locality, city)

@app.route('/donate', methods=['GET'])
def donate():
    local, city = locality()
    error = session.get('error', "")
    return render_template('donate.html',message={'local':local,'city':city, "error": error})

@app.route('/request', methods=['GET'])
def ask():
    query="select hosp_id, hosp_name, locality, name, pin from hospital_table left join locality on hospital_table.hosp_locality = locality.id left join city on hospital_table.hosp_city = city.id;;"
    cursor.execute(query)
    hosp_list=[str(i[0]) + '. ' + i[1] + ', ' + i[2] + ', ' + i[3] + ' - ' + i[4] for i in cursor.fetchall()]
    print(hosp_list)

    local, city = locality()
    error = session.get("error", None)
    return render_template('request.html',message={'hosp_list':hosp_list,'local':local,'city':city, 'error': error})

@app.route('/view_request', methods=["GET", "POST"])
def view_request():
    if request.method == "POST":
        # query to change the status of request to COMPLETED
        print(request.form.get('request_id'), request.form.get('donor'), request.form.get('hospital'))
        query = f"update request set status = '1', hosp_id = '{request.form.get('hospital')}', donor_id = '{request.form.get('donor')}' where id = '{request.form.get('request_id')}'"
        print(query)
        cursor.execute(query)
        conn.commit()

    query = f"select id, first_name, last_name, phone, aadhar, blood_group, blood_polarity from request where status = '0'"
    cursor.execute(query)
    processing = cursor.fetchall()

    query = f"select id, first_name, last_name, phone, aadhar, blood_group, blood_polarity from request where status = '1'"
    cursor.execute(query)
    completed = cursor.fetchall()
 
    query = f"select v_id, first_name, last_name from donor"
    cursor.execute(query)
    donors = cursor.fetchall()

    query = f"select hosp_id, hosp_name, hosp_locality from hospital_table"
    cursor.execute(query)
    hospitals = cursor.fetchall()

    requests={"processing": processing, "completed": completed, "donors": donors, "hospitals": hospitals}
    return render_template('request-view.html', requests=requests)

@app.route('/req_process', methods=['POST'])
def req_process():
    # Parsing sex and blood polarity from form
    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    hosp_data=request.form.get('hosp')
    print("This is the hospital data : ", hosp_data)
    hosp_id,b=hosp_data.split('.')
    hosp_name,hosp_locality,hosp_city,hosp_pin=b.split(',')
    v_id=request.form.get('v_id')

    # checking request_verification table for exisiting recepient
    query = f"SELECT first_name,last_name,aadhar_id FROM request_verification WHERE v_id={v_id}" ##error_handling
    cursor.execute(query)
    x = cursor.fetchone()

    print("This is x : ", x)
    print(x[0].strip(), request.form.get('first_name').lower().strip())
    if(x[0].strip()==request.form.get('first_name').lower().strip()) and x[1].strip()==request.form.get('last_name').lower().strip() and x[2]==request.form.get('aadhar'):
        session.pop("error", None)
        
        # Query to insert into request table in database
        query = 'INSERT INTO REQUEST(first_name,last_name,sex,city,locality,phone,aadhar,issue,blood_group,blood_polarity,hosp_name,hosp_locality,hosp_city,hosp_pin,hosp_id,v_id) VALUES ("' + request.form.get('first_name').title() + '", "' + request.form.get('last_name').title() + '", "' + sex + '", "' + request.form.get('city').title() + '", "' + request.form.get('local').title() + '", "' + request.form.get('phone') + '", "' + request.form.get('aadhar') + '","' + request.form.get('issue') + '","' + request.form.get('blood_group') + '", "' + str(blood_polarity) + '", "' + hosp_name + '","' + hosp_locality + '","' + hosp_city + '","' + hosp_pin + '", ' + str(hosp_id) +' , ' + str(v_id) +')'
        print(query)
        cursor.execute(query)
        conn.commit()

        # Query to read from donor table in database
        query='SELECT phone FROM DONOR WHERE blood_group="' + request.form.get('blood_group') + '" AND blood_polarity="' + str(blood_polarity) +'" AND locality="'+request.form.get('local')+ '"'
        x=cursor.execute(query)
        x=cursor.fetchall()
        print(x)

        # Code to iterate through database results and send SMS to all prospective donors (in the same location)
        for i in x:
            phone = "+91" + i[0]
            print(phone, blood_polarity)
            blood_polarity = "+" if request.form.get("blood_polarity") else "-"
            message = "A patient is in need of " + request.form.get('blood_group').upper() + blood_polarity + " blood in your locality"

            # publish = client.publish(
            #     PhoneNumber=phone,
            #     Message=message
            # )

            # print(publish)
            print("Message sent", phone, message)
    else:
        session["error"] = "Recepient not found"
        return redirect('/request')
        
    return render_template('req_process.html')

@app.route('/donate_success', methods=["POST"])
def donate_success():
    query = f"select first_name, last_name, aadhar_id from donor_verification where v_id = {request.form.get('v_id')}"
    print(query)
    cursor.execute(query)
    results = cursor.fetchall()
    
    # form validation
    if len(results) == 0:
        session["error"] = "Donor not found"
    
        return redirect('/donate')
    elif results[0][0].lower() != request.form.get('first_name'):
        session["error"] = "First name does not match"
        return redirect('/donate')

    elif results[0][1].lower() != request.form.get('last_name'):
        session["error"] = "Last name does not match"
        return redirect('/donate')

    elif results[0][2].lower() != request.form.get('aadhar'):
        session["error"] = "Aadhar Number does not match"
        return redirect('/donate')

    phone = "+91" + request.form.get('phone')
    print(phone)

    session.pop('error', None)

    print("this is the error after it is popped", session.get('error', None))
    print(request.form.get('locality'))

    # session["sex"] = request.form.get('sex')[0]
    # session['blood_polarity'] = request.form.get('blood_polarity'),
    # session["first_name"] = request.form.get('first_name'),
    # session['last_name'] = request.form.get('last_name')
    # session['city'] = request.form.get('city')
    # session['locality'] = request.form.get('locality')
    # session['phone'] = request.form.get('phone')
    # session['aadhar'] = request.form.get('aadhar')
    # session['blood_group'] = request.form.get('blood_group')
    # session['v_id'] = request.form.get('v_id')

    print("This is the sex : ", session.get('sex', None))
    sex = request.form.get('sex')[0]
    print(sex)
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    verification = 1 if request.form.get('v_id') == "yes" else 0
    v_id = request.form.get('v_id')
    query = 'INSERT INTO DONOR VALUES ("' + request.form.get('first_name').title() + '", "' + request.form.get('last_name').title() + '", "' + sex + '", "' + request.form.get('city').title() + '", "' + request.form.get('locality').title() + '", "' + request.form.get('phone') + '", "' + request.form.get('aadhar') + '", "' + request.form.get('blood_group') + '", "' + str(blood_polarity) + '", "' +  str(v_id) + '","' + str(verification) + '")'
    print(query)
    cursor.execute(query)
    conn.commit()
    return render_template('success.html')

if __name__ == "__main__":
    app.run(debug = True, port = 5001)