from flask import Flask, render_template, redirect, session, url_for, request
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
import config as Config
import sys
import csv
import datetime
import iso8601
from dateutil import tz
import os
import io
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "test_secret_key"
# UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['csv'])
csv_input = 0
file = 0
df = 0

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

@app.route("/")
def home():
    # if method is GET and user is logged in
    if 'access_token' in session:

        return render_template("upload.html")

    return render_template("home.html")

@app.route("/transform", methods=["POST"])
def transform():
    global file
    global df
    file = request.files['data_file']
    if not file:
        return render_template("transform.html",transactions=df)
    if file and allowed_file(file.filename):
        df = pd.read_csv(file.stream)
        return render_template("transform.html",transactions=df)
    return redirect(url_for("/"))
    
@app.route("/submission", methods=["POST"])
def submission():
    global df
    # TODO: add checks beforehand whether the user has clicked on all checkboxes
    # print(request.form)

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])

    saleh = ExpenseUser()
    saleh.setId(2242086)
    paypal = ExpenseUser()
    paypal.setId(18572820)
    nuraini = ExpenseUser()
    nuraini.setId(2705458)

    for key in request.form:
        if not is_number(key):
            continue
        value = request.form[key]
        if value == 'Payment':
            continue # we dont handle payments yet
        print(key, value)
        amount = df.iloc[int(float(key))]['Amount']
        users = []
        users.append(saleh)
        users.append(paypal)
        users.append(nuraini)
        saleh.setPaidShare('0.00')
        nuraini.setPaidShare('0.00')
        paypal.setPaidShare('0.00')
            
        saleh.setOwedShare('0.00')
        nuraini.setOwedShare('0.00')
        paypal.setOwedShare('0.00')

        expense = Expense()
        expense.setUsers(users)
        expense.setGroupId(6456733)
        expense.setCost(str(abs(float(amount))))
        expense.setDescription(df.iloc[int(float(key))]['Description'])

        try:
            expense.setDate(datetime.datetime.strptime(df.iloc[int(float(key))]['Trans Date'], '%m/%d/%Y').strftime('%d/%m/%Y'))
        except:
            expense.setDate(datetime.datetime.strptime(df.iloc[int(float(key))]['Trans Date'], '%m/%d/%y').strftime('%d/%m/%Y'))

        # case where a transaction is refunded
        if float(amount) > 0:
            if value == 'Saleh':
                paypal.setOwedShare(str(abs(float(amount))))
                saleh.setPaidShare(str(abs(float(amount))))
            elif value == 'Nuraini':
                paypal.setOwedShare(str(abs(float(amount))))
                nuraini.setPaidShare(str(abs(float(amount))))   
            expense = sObj.createExpense(expense)
            continue

        # case for expenses
        if value == 'Saleh':
            saleh.setOwedShare(str(abs(float(amount))))
            paypal.setPaidShare(str(abs(float(amount))))
            expense = sObj.createExpense(expense)
        elif value == 'Nuraini':
            nuraini.setOwedShare(str(abs(float(amount))))
            paypal.setPaidShare(str(abs(float(amount))))
            expense = sObj.createExpense(expense)
        elif value == 'Half-Split':
            half = round(abs(float(amount))/2,2)
            other_half = abs(float(amount))-half
            nuraini.setOwedShare(half)
            saleh.setOwedShare(other_half)
            paypal.setPaidShare(str(abs(float(amount))))
            expense = sObj.createExpense(expense)
        elif value == 'Share':
            
            continue
    
    return redirect(url_for("success"))
    


@app.route("/login")
def login():

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    url, secret = sObj.getAuthorizeURL()
    session['secret'] = secret
    return redirect(url)


@app.route("/authorize")
def authorize():

    if 'secret' not in session:
        return redirect(url_for("home"))

    oauth_token    = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
    session['access_token'] = access_token

    return redirect(url_for("home"))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/friends")
def friends():
    if 'access_token' not in session:
        return redirect(url_for("home"))

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])

    friends = sObj.getFriends()


    return render_template("friends.html",friends=friends)




if __name__ == "__main__":
    app.run(threaded=True,debug=True)
