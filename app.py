from logging import root
import re
from flask import Flask, render_template, request, session
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
    city_details=[[i[0],i[1],i[2]] for i in cursor.fetchall()]
    locality=[i[0] for i in city_details]
    city=[i[1] for i in city_details]
    pin=[i[2] for i in city_details]
    return(locality,set(city),pin)


    
@app.route('/donate', methods=['GET'])
def donate():
    local,city,pin=locality()
    return render_template('donate.html',message={'local':local,'city':city,'pin':pin})

@app.route('/request', methods=['GET'])
def ask():
    query="SELECT * from hospital_table"
    cursor.execute(query)
    hosp_list=[]
    for i in cursor.fetchall():
        hosp_list.append(str(i[0])+'.'+i[1]+','+i[2]+','+i[3]+','+i[4])
    local,city,pin=locality()
    return render_template('request.html',message={'hosp_list':hosp_list,'local':local,'city':city,'pin':pin})

@app.route('/view_request', methods=["GET", "POST"])
def view_request():
    if request.method == "POST":
        # Write query here to change the status of request to COMPLETED
        pass

    processing = [["Sanjay", "Suresh", 2345689, 3245346], ["Sanjay", "Suresh", 2345689, 3245346]] # Write query here to retrieve requests that are currently being processed
    completed = [] # Write query here to retrieve requests that are completed
    requests={"processing": processing, "completed": completed}
    print(requests)
    return render_template('request-view.html', requests=requests)

@app.route('/req_process', methods=['POST'])
def req_process():
    # Parsing sex and blood polarity from form
    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    hosp_data=request.form.get('hosp')
    hosp_id,b=hosp_data.split('.')
    hosp_name,hosp_locality,hosp_city,hosp_pin=b.split(',')
    v_id=request.form.get('v_id')
    query="SELECT first_name,last_name,aadhar_id FROM request_verification WHERE v_id=v_id" ##error_handling
    cursor.execute(query)
    x=cursor.fetchone()
    print(type(x[0]),type(request.form.get('first_name').title()))
    if(x[0].strip()==request.form.get('first_name').title().strip()) and x[1].strip()==request.form.get('last_name').title().strip() and x[2]==request.form.get('aadhar'):

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

        # print(drop_id)
        
        # Code to interate through database results and send SMS to all prospective donors (in the same location)
        for i in x:
            phone = "+91" + i[0]
            blood_polarity = "+" if request.form.get("blood_polarity") else "-"
            message = "A patient is in need of " + request.form.get('blood_group').upper() + blood_polarity + " blood in your locality"
            # print
            # client.publish(
            #     PhoneNumber=phone,
            #     Message=message
            # )
            print("Message sent", phone, message)
        
    return render_template('req_process.html')

@app.route('/donate_otp', methods=["POST"])
def donate_otp():
#     phone = "+91" + request.form.get('phone')
#     print(phone)
#     # otp_dict = client.create_sms_sandbox_phone_number(
#     #     PhoneNumber=phone,
#     #     LanguageCode="en-GB"
#     # )
    
#     session["sex"] = request.form.get('sex')[0]
#     session['blood_polarity'] = request.form.get('blood_polarity'),
#     session["first_name"] = request.form.get('first_name'),
#     session['last_name'] = request.form.get('last_name')
#     session['city'] = request.form.get('city')
#     session['locality'] = request.form.get('locality')
#     session['phone'] = request.form.get('phone')
#     session['aadhar'] = request.form.get('aadhar')
#     session['blood_group'] = request.form.get('blood_group')
#     session['verification'] = request.form.get('verification')

#     print(session.get('phone', None))

    return render_template('otp.html')

@app.route('/donate_success', methods=['POST'])
def donate_success():
    # print(session.get('first_name', None))
    # print(session.get('last_name', None))
    # print(session.get('city', None))
    # print(session.get('locality', None))
    # print(session.get('phone', None))
    # print(session.get('aadhar', None))

    # verify_sandbox = client.verify_sms_sandbox_phone_number(
    #     PhoneNumber="+91" + session.get('phone'),
    #     OneTimePassword=request.form.get('otp')
    # )

    sex = session.get('sex', None)[0]
    blood_polarity = 1 if session.get('blood_polarity', None)[0] == "plus" else 0
    verification = 1 if session.get('verification', None)[0] == "yes" else 0
    v_id=request.form.get('v_id')
    query="SELECT first_name,last_name,aadhar_id FROM donor_verification WHERE v_id=v_id" ##error_handling
    cursor.execute(query)
    x=cursor.fetchone()
    if(x[0].strip()==request.form.get('first_name').title().strip()) and x[1].strip()==request.form.get('last_name').title().strip() and x[2]==request.form.get('aadhar'):
        query = 'INSERT INTO DONOR VALUES ("' + session.get('first_name', None)[0].title() + '", "' + session.get('last_name', None).title() + '", "' + sex + '", "' + session.get('city', None).title() + '", "' + session.get('locality', None).title() + '", "' + session.get('phone', None) + '", "' + session.get('aadhar', None) + '", "' + session.get('blood_group', None) + '", "' + str(blood_polarity) + '", ' + verification + ',' + str(v_id) + ')'
        cursor.execute(query)
        conn.commit()
    return render_template('success.html')
    
if __name__ == "__main__":
    app.run(debug = True)