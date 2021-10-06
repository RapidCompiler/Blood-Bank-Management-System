from flask import Flask, render_template, request

app = Flask(__name__)

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
    print(request.form.get('city'))
    return render_template('success.html')

if __name__ == "__main__":
    app.run(debug = True)