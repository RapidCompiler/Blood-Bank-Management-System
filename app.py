from flask import Flask, render_template, request, session, redirect, url_for
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import os
# import boto3
from twilio.rest import Client
import bcrypt

load_dotenv()

# Initializing connection to AWS SNS Client
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
messaging_service_id = os.getenv('TWILIO_MESSAGING_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)
# access_key = os.getenv('AWS_ACCESS_KEY_ID')
# secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# client = boto3.client(
#     "sns",
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key,
#     region_name="us-east-1"
# )

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


@app.route('/', methods=['GET'])
@app.route('/<user>')
def index(user = None):
    if user == None:
        if session.get('doctor_logged_in', None):
            user = "doctor"
        elif session.get('hospital_logged_in', None):
            user = "hospital"

    user = restrictedViewCheck(user, 'index')

    session.pop("error", None)

    return render_template('index.html', message={"user": user})
    

def locality():
    query="SELECT * from city"
    cursor.execute(query)
    city = [i[0] for i in cursor.fetchall()]
    query = "select locality_name, pin from locality"
    cursor.execute(query)
    locality = [(i[0], i[1]) for i in cursor.fetchall()]    
    return(locality, city)

def sendSMS(body, phone):
    client.messages.create(
        messaging_service_sid = messaging_service_id,
        body = body,
        to = phone
    )
    print("Message sent", phone, body)

def restrictedViewCheck(user, endpoint):
    if (user == "hospital" and session.get('doctor_logged_in', None)) or (user == "doctor" and session.get('hospital_logged_in', None)):
        if user == "doctor":
            return "hospital"
        return "doctor"

    if user not in ["doctor", "hospital"]:
        if session.get('doctor_logged_in', None):
            return "doctor"
        return "hospital"

    return user


@app.route('/donate', methods=['GET'])
def donate():
    local, city = locality()
    error = session.get('error', "")
    return render_template('donate.html',message={'local':local,'city':city, "error": error})


@app.route('/request', methods=['GET'])
def ask():
    query="select hospital_table.id, hosp_name, locality_name, name, pin from hospital_table left join locality on hospital_table.hosp_locality = locality.id left join city on hospital_table.hosp_city = city.id;"
    cursor.execute(query)
    hosp_list=[str(i[0]) + '. ' + i[1] + ', ' + i[2] + ', ' + i[3] + ' - ' + i[4] for i in cursor.fetchall()]
    print(hosp_list)

    local, city = locality()
    error = session.get("error", None)
    return render_template('request.html',message={'hosp_list':hosp_list,'local':local,'city':city, 'error': error})

    
@app.route('/view_request/hospital', methods=["GET", "POST"])
def view_request():
    user = restrictedViewCheck('hospital', 'view_donor')
    if user == "doctor":
        return redirect('/')
    
    if request.method == "POST":
        # query to change the status of request to COMPLETED
        print(request.form.get('request_id'), request.form.get('donor'), session.get('hospital_id', None))
        query = f"update request set req_status = 'COMPLETED', hosp_id = '{session.get('hospital_id', None)}', donor_id = {request.form.get('donor')} where id = {request.form.get('request_id')}"
        print(query)
        cursor.execute(query)
        conn.commit()

    hosp_id = session.get('hospital_id', None)
    print(hosp_id)

    query = f"select request.id, first_name, last_name, phone, aadhar_id, blood_group, blood_polarity, issue from request left join request_verification on request.v_id=request_verification.v_id where req_status = 'PROCESSING' and hosp_id = {hosp_id};"
    cursor.execute(query)
    processing = cursor.fetchall()

    query = f"select request.id, request_verification.first_name, request_verification.last_name, request.phone, request_verification.aadhar_id, request.blood_group, request.blood_polarity, request.issue, request.donor_id, donor_verification.first_name from request left join request_verification on request.v_id=request_verification.v_id left join donor on request.donor_id = donor.id left join donor_verification on donor.v_id = donor_verification.v_id where req_status = 'COMPLETED' and hosp_id = {hosp_id};"
    cursor.execute(query)
    completed = cursor.fetchall()
    print(completed)
 
    query = f"select donor.id, first_name, last_name, blood_group, blood_polarity from donor left join donor_verification on donor.v_id=donor_verification.v_id"
    cursor.execute(query)
    donors = cursor.fetchall()

    requests={"processing": processing, "completed": completed, "donors": donors}
    print(requests)
    return render_template('request-view.html', requests=requests)


@app.route('/view_donor/doctor', methods=["GET", "POST"])
def view_donor():
    user = restrictedViewCheck('doctor', 'view_donor')
    if user == "hospital":
        return redirect('/')

    if request.method == "POST":
        # delete from donor_verification and donor tables
        query = f"delete from donor where v_id = '{request.form.get('donor_id')}'"
        print(query)
        cursor.execute(query)
        conn.commit()
        query = f"delete from donor_verification where v_id = '{request.form.get('donor_id')}'"
        print(query)
        cursor.execute(query)
        conn.commit()

    query = f"select * from donor_verification where d_id = '{session.get('doctor_id')}'"
    cursor.execute(query)
    verified = cursor.fetchall()
    requests = {"verified": verified}
    return render_template('donor-view.html', requests=requests)


@app.route('/req_process', methods=['POST'])
def req_process():
    # Parsing sex and blood polarity from form
    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    hosp_data=request.form.get('hosp')
    print(hosp_data)
    print("This is the hospital data : ", hosp_data)
    hosp_id,b=hosp_data.split('.')
    hosp_name,hosp_locality,c=b.split(', ')
    hosp_city,hosp_pin=c.split(' - ')
    locality=request.form.get('local')
    v_id=request.form.get('v_id')
    print(c,hosp_locality,hosp_pin,hosp_city)
    print(locality)
    
    # checking request_verification table for existing recepient
    query = f"select id from locality where locality_name = '{locality}'"
    print(query)
    cursor.execute(query)
    x = cursor.fetchone()
    locality_id=x[0]
    query = f"SELECT first_name,last_name,aadhar_id FROM request_verification WHERE v_id={v_id}" ##error_handling
    cursor.execute(query)
    y = cursor.fetchone()
    query = f"select id from locality where locality_name = '{hosp_locality}'"
    cursor.execute(query)
    x = cursor.fetchone()
    hosp_locality_id=x[0]
    query = f"select id from city where name ='{hosp_city}'"
    cursor.execute(query)
    x = cursor.fetchone()
    hosp_city_id=x[0]
    print(hosp_locality_id,hosp_city_id)
    if(y[0].strip().lower()==request.form.get('first_name').lower().strip()) and y[1].strip().lower()==request.form.get('last_name').lower().strip() and y[2].lower()==request.form.get('aadhar'):
        session.pop("error", None)

        # Already existing request check
        query = f"select * from request where v_id = {v_id}"
        cursor.execute(query)
        results = cursor.fetchall()

        if len(results) == 0:        
            query = 'INSERT INTO REQUEST(sex,phone,issue,blood_group,blood_polarity,hosp_id,v_id,locality_id) VALUES ("' + sex + '","' + request.form.get('phone') + '", "' + request.form.get('issue') + '","' + request.form.get('blood_group') + '", "' + str(blood_polarity) + '", ' + str(hosp_id) +' , ' + str(v_id) +' , ' + str(locality_id) + ')'
            print(query)
            cursor.execute(query)
            conn.commit()

        # Query to read from donor table in database
        query='SELECT phone FROM DONOR WHERE blood_group="' + request.form.get('blood_group') + '" AND blood_polarity="' + str(blood_polarity) +'" AND locality_id="' + str(hosp_locality_id) + '"'
        x=cursor.execute(query)
        x=cursor.fetchall()
        if len(x)>=5:
            print("Enough donors in vicinity")
            # Code to iterate through database results and send SMS to all prospective donors (in the same location)
            for i in x:
                phone = "+91" + i[0]
                print(phone, blood_polarity)
                blood_polarity = "+" if request.form.get("blood_polarity") else "-"
                message = "A patient is in need of " + request.form.get('blood_group').upper() + blood_polarity + " blood at "+ hosp_name + " hospital in " + hosp_locality +"."
                sendSMS(message, phone)

        else:
            # Code to iterate through database results and send SMS to all prospective donors (in the same city)
            print("Not enough so sent to all")
            blood_sign = "+" if request.form.get("blood_polarity") == "plus" else "-"
            blood_polarity = 1 if request.form.get("blood_polarity") == "plus" else 0
            print("This is the blood_polarity : ", request.form.get('blood_polarity'))
            query = f"select phone from donor left join locality on donor.locality_id=locality.id left join city on locality.c_id = {hosp_city_id} where blood_group = '{request.form.get('blood_group')}' and blood_polarity = {blood_polarity};"
            print(query)
            cursor.execute(query)
            results = cursor.fetchall()
            print(results)
            for i in results:
                phone = "+91" + i[0]
                print(phone)
                message = "A patient is in need of " + request.form.get('blood_group').upper() + blood_sign + " blood at "+ hosp_name + " hospital in " + hosp_locality +"."
                sendSMS(message, phone)

    else:
        session["error"] = "Recepient not found"
        return redirect('/request')
    return render_template('success.html', requests = {})


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
    elif results[0][0].lower().strip() != request.form.get('first_name').lower().strip():
        print(results[0][0].lower().strip(), request.form.get('first_name').lower().strip())
        session["error"] = "First name does not match"
        return redirect('/donate')

    elif results[0][1].lower() != request.form.get('last_name').lower():
        session["error"] = "Last name does not match"
        return redirect('/donate')

    elif results[0][2].lower() != request.form.get('aadhar').lower():
        print(results[0][2].lower(),request.form.get('aadhar').lower())
        session["error"] = "Aadhar Number does not match"
        return redirect('/donate')

    # Removing any existing errors
    session.pop('error', None)

    # Getting the locality ID
    locality = request.form.get('locality')
    query = f"select id from locality where locality_name = '{locality}'"
    cursor.execute(query)
    results = cursor.fetchone()
    locality_id = results[0]

    sex = request.form.get('sex')[0]
    blood_polarity = 1 if request.form.get('blood_polarity') == "plus" else 0
    v_id = request.form.get('v_id')
    
    # Already existing donor check
    query = f"select * from donor where v_id = {v_id}"
    cursor.execute(query)
    results = cursor.fetchall()

    if len(results) == 0:
        query = 'INSERT INTO DONOR(sex,phone,blood_group,blood_polarity,v_id,locality_id) VALUES ("' + sex + '", "' + request.form.get('phone') +'", "' + request.form.get('blood_group') + '", ' + str(blood_polarity) + ', "' +  str(v_id) + '","' + str(locality_id) + '")'
        print(query)
        cursor.execute(query)
        conn.commit()


    # Pending requests check
    query='SELECT request.hosp_id from request where req_status="PROCESSING" and request.locality_id=' + str(locality_id) + ' and request.blood_group="' +str(request.form.get('blood_group'))+ '" and request.blood_polarity= ' + str(blood_polarity) + ' ;'
    print(query)
    cursor.execute(query)
    x=cursor.fetchone()

    if x != None:
        phone = "+91" + request.form.get('phone')
        print(phone, blood_polarity)
        blood_polarity = "+" if request.form.get("blood_polarity") else "-"
        query=f"select hospital_table.hosp_name, locality.locality_name from hospital_table left join locality on hospital_table.hosp_locality = locality.id where hospital_table.id = {x[0]};"
        cursor.execute(query)
        hosp_details=cursor.fetchone()
        hosp_name,hosp_locality=hosp_details[0],hosp_details[1]

        message = "A patient is in need of " + request.form.get('blood_group').upper() + blood_polarity + " blood in the hospital "+ hosp_name + " at " + hosp_locality +"."
        sendSMS(message, phone)

    return render_template('success.html', requests = {})


@app.route('/verification/<user>', methods=["POST", "GET"])
def verification(user):

    if request.method == "POST":
        userType = "doctor" if user == "donor" else "hospital"
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        aadhar = request.form.get('aadhar')
        another_id = session.get(f'{userType}_id')
        which_id = "d_id" if user == "donor" else "h_id"
        query = f"insert into {user}_verification (first_name, last_name, aadhar_id, {which_id}) values ('{first_name}', '{last_name}', '{aadhar}', '{another_id}')"
        print(query)
        cursor.execute(query)
        conn.commit()
        query = f"select v_id from {user}_verification where aadhar_id = '{aadhar}'"
        print(query)
        cursor.execute(query)
        vid = cursor.fetchone()
        requests = vid[0]

        return render_template('success.html', requests=requests)

    user = restrictedViewCheck(user, 'verification')
    user = "donor" if user == "doctor" else "request"
    if session.get("doctor_logged_in", None) or session.get('hospital_logged_in', None):
        return render_template('verification.html', message={"user": user})
    else:
        print("inside donor_verification function")
        return redirect('/')


@app.route('/profile/<user>')
def profile(user):
    user = restrictedViewCheck(user, 'profile')
    print(user, session.get('doctor_logged_in', None), session.get('hospital_logged_in', None))

    if session.get(f"{user}_logged_in", None):
        query = f"select * from {user}_table where id = '{session.get(f'{user}_id', None)}'"
        cursor.execute(query)
        results = cursor.fetchall()
        if user == "doctor":
            return render_template('profile.html', message={"user": user, "id": results[-1][0], "name": results[-1][1]})
        else:
            id = results[-1][3]
            name = results[-1][0]
            cityid = results[-1][1]
            query = f"select * from city where id = {cityid}"
            cursor.execute(query)
            city = cursor.fetchall()
            city = city[-1][0]

            localityid = results[-1][2]
            query = f"select * from locality where id = {localityid}"
            cursor.execute(query)
            locality = cursor.fetchall()
            locality = locality[-1][0]
            return render_template('profile.html', message={"user": user, "id": id, "name": name, "city": city, "locality": locality})
    else:
        return redirect(url_for('login', user = user))


@app.route('/login/<user>', methods=["GET"])
def login_page(user):
    user = restrictedViewCheck(user, 'login_page')
    if not session.get(f'{user}_logged_in', None):
        error = session.get(f'{user}_login_error', "")
        return render_template(f'{user}-login.html', message={"error": error})
    else:
        return redirect(f'/{user}')

@app.route('/login/<user>', methods=["POST"])
def login(user):
    user = restrictedViewCheck(user, 'login')
    userid = request.form.get("userid")
    password = request.form.get("password")
    query = f"select * from {user}_table where id = '{userid}'"
    print(query)
    cursor.execute(query)
    results = cursor.fetchall()
    if not results:
        session[f"{user}_login_error"] = "User ID & Password combination does not exist"
        return redirect(f'/login/hospital')
    else:
        print("THIS IS THE SALT : ", results[-1][-1])
        pwhash = bcrypt.hashpw(password.encode("utf-8"), results[-1][-1].encode("utf-8")).decode("utf-8")
        if pwhash == results[-1][-2]:
            session[f"{user}_logged_in"] = True
            session[f"{user}_id"] = userid
            print(userid)
            session.pop(f"{user}_login_error", None)
            print('came here')
            return redirect(f'/{user}')
        else:
            session[f"{user}_login_error"] = "User ID & Password combination does not exist"
            return redirect(f'/login/{user}')


@app.route('/logout/<user>', methods=["POST"])
def logout(user):
    user = restrictedViewCheck(user, 'logout')
    print('logging out')
    print(session.get('hospital_logged_in', None), session.get('hospital_id', None), session.get('hospital_name', None))
    session.pop(f'{user}_logged_in', None)
    session.pop(f"{user}_id", None)
    print(session.get('hospital_logged_in', None), session.get('hospital_id', None), session.get('hospital_name', None))
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug = True, port = 5001)