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
saleh_value = []
nuraini_value = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    # if method is GET and user is logged in
    if 'access_token' in session:
        return """
                <html>
                    <body>
                        <h1>Transform a file demo</h1>

                        <form action="/transform" method="post" enctype="multipart/form-data">
                            <input type="file" name="data_file" />
                            <input type="submit" />
                        </form>
                    </body>
                </html>
            """
        # if method is GET and user is not logged in
    return render_template("home.html")

    # if method is POST

@app.route("/transform", methods=["POST"])
def transform():
    global file
    file = request.files['data_file']
    if file and allowed_file(file.filename):
        df = pd.read_csv(file.stream)
        print(list(df))
        for index, row in df.iterrows():
            print(row['Transaction Date'], row['Amount'])
        return render_template("transform.html",transactions=df)
    return redirect(url_for("/"))
    # return "done"
    # if not file:
    #     return "No file"
    # if file and allowed_file(file.filename):
    #     stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    #     global csv_input 
    #     csv_input = csv.reader(stream)

    #     next(csv_input)
    #     #print("file contents: ", file_contents)
    #     #print(type(file_contents))
    #     # print(csv_input)
    #     # for row in csv_input:
    #     #     print(row[0])
    #     return render_template("transform.html",transactions=csv_input)
    # return redirect(url_for("transform"))
    # file = request.files['data_file']
    
@app.route("/submission", methods=["POST"])
def submission():
    global df
    global nuraini_value
    global saleh_value
    # csv_input.seek(0)
    nuraini_value = request.form.getlist('Nuraini') 
    print(nuraini_value)
    saleh_value = request.form.getlist('Saleh')
    print(saleh_value) 
    # result = request.form
    # for key, value in result.items():
    #     print(key)
    #     print(value)
    return redirect(url_for("friends"))


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



@app.route("/friends")
def friends():
    if 'access_token' not in session:
        return redirect(url_for("home"))

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])

    # print sObj.getCurrentUser().getId()

    # groups = sObj.getGroups()
    # for g in groups:
    #     print g.getName(), g.getId()

    friends = sObj.getFriends()

    ###################### CODE TO COMPARE TRANSACTIONS #######################
    # expenses = sObj.getExpenses(limit=1000, group_id = 6456733, dated_after='01/03/2018', dated_before='31/03/2018')
    # print (len(expenses))
    # countSplit = {}
    # paymentSum = 0
    # expenseCostSplit = []
    # for expense in expenses:
    #     # print(type(expense.getCost()))
    #     if expense.getDescription() != 'Payment' and expense.getDeletedAt() == None:
    #         expenseCostSplit.append(expense.getCost())
    #         date = datetime.datetime.strptime(expense.getDate()[:-10], '%Y-%m-%d').strftime('%m/%d/%y')
    #         if date in countSplit:
    #             countSplit[date] += 1
    #         else:
    #             countSplit[date] = 1
    #     else:
    #         paymentSum +=1
    # print(sum(countSplit.values()), paymentSum, paymentSum+sum(countSplit.values()))
    # # for key, value in sorted(countSplit.items(), key = lambda x: datetime.datetime.strptime(x[0], '%m/%d/%y')):
    # #     print (key, value)

    # countPayPal = {}
    # expenseCostPayPal = []
    # with open(sys.argv[1], 'r') as paypal_csv:
    #     paypal_output = csv.DictReader(paypal_csv)

    #     for line in paypal_output:
    #         if line['Description'] != 'PAYMENT - THANK YOU':
    #             expenseCostPayPal.append(str(abs(float(line['Amount']))))
    #             date = datetime.datetime.strptime(line['Transaction Date'], '%m/%d/%y').strftime('%m/%d/%y')
    #             if date in countPayPal:
    #                 countPayPal[date] += 1
    #             else:
    #                 countPayPal[date] = 1
    # # for key, value in sorted(countPayPal.items(), key = lambda x: datetime.datetime.strptime(x[0], '%m/%d/%y')):
    # #     if key in countSplit:
    # #         if countSplit[key] != value:
    # #             print ('PayPal: %s: %d' % (key, value))
    # #             print ('Splitwise %s: %d' % (key, countSplit[key]))
    # #     else:
    # #         print ('%s not found in splitwise' % key)
    #     # print (key, value)

    # # value = { k : countPayPal[k] for k in set(countPayPal) - set(countSplit) }

    # for key, value in sorted(countPayPal.items(), key = lambda x: datetime.datetime.strptime(x[0], '%m/%d/%y')):
    #     if key in countSplit:
    #         if value != countSplit[key]:
    #             print ('%s: %d %d' % (key, value, countSplit[key]))
    #     else:
    #         print ('%s: %d' % (key, value))

    # # expenseCostSplit.sort()
    # # expenseCostPayPal.sort()

    # # print(len(expenseCostPayPal))

    # # for i in range(len(expenseCostSplit)):
    # #     if expenseCostSplit[i] != expenseCostPayPal[i]:
    # #         print ('PayPal: %s' % (expenseCostPayPal[i]))
    # #         print ('Splitwise %s' % (expenseCostSplit[i])) 

    ################## CODE TO IMPORT TRANSACTIONS #######################
    # with open(sys.argv[1], 'r') as paypal_csv:
    #     paypal_output = csv.DictReader(paypal_csv)

    #     for line in paypal_output:
    #         saleh = ExpenseUser()
    #         saleh.setId(2242086)

    #         paypal = ExpenseUser()
    #         paypal.setId(13080887)

    #         nuraini = ExpenseUser()
    #         nuraini.setId(2705458)

    #         users = []
    #         users.append(saleh)
    #         users.append(paypal)
    #         users.append(nuraini)

    #         saleh.setPaidShare('0.00')
    #         nuraini.setPaidShare('0.00')
    #         paypal.setPaidShare('0.00')
            
    #         saleh.setOwedShare('0.00')
    #         nuraini.setOwedShare('0.00')
    #         paypal.setOwedShare('0.00')

    #         expense = Expense()
    #         expense.setUsers(users)
    #         expense.setGroupId(6456733)
    #         expense.setCost(str(abs(float(line['Amount']))))
    #         expense.setDescription(line['Description'])
    #         # print (datetime.datetime.strptime(line['Date'], '%m/%d/%y').strftime('%d/%m/%Y'))
    #         expense.setDate(datetime.datetime.strptime(line['Date'], '%m/%d/%y').strftime('%d/%m/%Y'))

    #         if float(line['Amount']) > 0 and line['Payer'] != 'Payment':
    #             print ("Refund", line['Payer'], line['Date'], line['Description'], line['Amount'])
    #             if line['Payer'] == 'Saleh':
    #                 paypal.setOwedShare(str(abs(float(line['Amount']))))
    #                 saleh.setPaidShare(str(abs(float(line['Amount']))))
    #             elif line['Payer'] == 'Nuraini':
    #                 paypal.setOwedShare(str(abs(float(line['Amount']))))
    #                 nuraini.setPaidShare(str(abs(float(line['Amount']))))
    #             elif line['Payer'] == 'Split':
    #                 paypal.setOwedShare(str(abs(float(line['Amount']))))
    #                 nuraini.setPaidShare(str(abs(float(line['Amount'])/2)))
    #                 saleh.setPaidShare(str(abs(float(line['Amount'])/2)))

                
    #             expense = sObj.createExpense(expense)
    #             print (expense.getId())

    #         elif line['Payer'] != 'Payment':
    #             print ("Charge", line['Payer'], line['Date'], line['Description'], line['Amount'])
    #             if line['Payer'] == 'Saleh':
    #                 saleh.setOwedShare(str(abs(float(line['Amount']))))
    #                 paypal.setPaidShare(str(abs(float(line['Amount']))))
    #             elif line['Payer'] == 'Nuraini':
    #                 nuraini.setOwedShare(str(abs(float(line['Amount']))))
    #                 paypal.setPaidShare(str(abs(float(line['Amount']))))
    #             elif line['Payer'] == 'Split':
    #                 if line['Saleh\'s Share'] or line['Nuraini\'s Share']:
    #                     nuraini.setOwedShare(str(abs(float(line['Nuraini\'s Share']))))
    #                     saleh.setOwedShare(str(abs(float(line['Saleh\'s Share']))))
    #                     paypal.setPaidShare(str(abs(float(line['Amount']))))
    #                 else:
    #                     nuraini.setOwedShare(str(abs(float(line['Amount'])/2)))
    #                     saleh.setOwedShare(str(abs(float(line['Amount'])/2)))
    #                     paypal.setPaidShare(str(abs(float(line['Amount']))))

    #             expense = sObj.createExpense(expense)
    #             print (expense.getId())


    ################### CODE TO FIND MONTHLY EXPENSE ##########################
    # compare_date_1 = datetime.datetime(2018, 2, 1).replace(tzinfo=tz.gettz('America/Chicago'))
    # compare_date_2 = datetime.datetime(2018, 3, 1).replace(tzinfo=tz.gettz('America/Chicago'))
    
    # expenses = sObj.getExpenses(limit=0, dated_after=compare_date_1.strftime('%d/%m/%Y'), dated_before=compare_date_2.strftime('%d/%m/%Y'))
    # existing_expenses = [expense for expense in expenses if (expense.getDescription() != '..' and expense.getDescription() != 'Payment' and expense.getDeletedAt() == None and not 'multi' in expense.getDescription()) ]
    # saleh_expenses = [expense for expense in existing_expenses for users in expense.getUsers() if users.getId() == 2242086]
    # count = 0
    # totalcost = 0
    # for expense in saleh_expenses:
    #     new_date = iso8601.parse_date(expense.getDate()).astimezone(tz.gettz('America/Chicago'))
    #     if (new_date >= compare_date_1 and new_date < compare_date_2):
    #         count += 1
    #         cost = 0
    #         for users in expense.getUsers():
    #             if users.getId() == 2242086:
    #                 cost = users.getOwedShare()
    #         print (str(count).ljust(2), expense.getDescription()[:55].ljust(55), str(cost).ljust(6), new_date.strftime('%m/%d/%Y'))
    #         totalcost += float(cost)
    # print ("Total cost was: ", round(totalcost,2))


    return render_template("friends.html",friends=friends)




if __name__ == "__main__":
    app.run(threaded=True,debug=True)
