from flask import Flask, render_template, request, session, redirect, url_for
import ibm_db
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# from flask_mail import Mail
from datetime import timedelta
from werkzeug.utils import secure_filename
from pathlib import Path

try:
    conn = ibm_db.connect(
        "DATABASE=bludb;HOSTNAME=98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30875;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=bkp88188;PWD=6kMh6xYbM0hAwn8D",
        '', '')
except:
    print(ibm_db.conn_errormsg())

app = Flask(__name__)
app.secret_key = 'a'


def send_confirmation_mail(user, mail):
    message = Mail(
        from_email="vigneshwaransam877@gmail.com",
        to_emails=mail,
        subject="Congrats! Your Account was created Successfully",
        html_content=f"<strong>Congrats {user}!</strong><br>Account Created with username {mail}"
    )

    SENDGRID_API_KEY = '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'
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(f"Some error in sendgrid, {e}")


def request_mail(user, mail, ea, c, s, p, co):
    message = Mail(
        from_email="vigneshwaransam877@gmail.com",
        to_emails=mail,
        subject="Blood Needed",
        html_content=f"<strong>Your Attention Please</strong><br>{user} Needs your blood<br>Check your app for details<br> blood bank name : {user} <br> blood bank email : {ea} <br> city : {c} <br> contact : {co} <br> state: {s} <br> pincode : {p} "
    )

    SENDGRID_API_KEY = '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'
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(f"Some error in sendgrid, {e}")


# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    global userId
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            session['user'] = username

            return redirect('docs', code=302)
        else:
            msg = "Incorrect username/password"
        return render_template('login.html', msg=msg)

    return render_template("login.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        username = request.form['name']
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('signup.html', msg="You are already a member, please login")
        else:
            insert_sql = "INSERT INTO users VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
        send_confirmation_mail(username, email)

        return render_template('signup.html', msg="User Created Successfuly..")

    return render_template("signup.html")


@app.route("/forgotpassword", methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['npassword']
        sql = "select * from users where email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            sql1 = "update users set password=? where email=?"
            stmt = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(stmt, 1, password)
            ibm_db.bind_param(stmt, 2, email)

            ibm_db.execute(stmt)
            return render_template('forgotpwd.html', msg="Password Changed")
        else:
            return render_template('forgotpwd.html', msg="Incorrect Email")

    return render_template("forgotpwd.html")


# @app.route("/forgotpassword", methods=['GET', 'POST'])
# def forgotpassword():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['npassword']
#         sql = "select * from users where email=?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, email)
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#         if account:
#             sql1 = "update users set password=? where email=?"
#             stmt = ibm_db.prepare(conn, sql1)
#             ibm_db.bind_param(stmt, 1, password)
#             ibm_db.bind_param(stmt, 2, email)
#
#             ibm_db.execute(stmt)
#             return render_template('forgotpwd.html', msg="Password Changed")
#         else:
#             return render_template('forgotpwd.html', msg="Incorrect Email")


@app.route("/docs")
def docs():
    if "user" in session:
        return render_template("docs.html")
    else:
        return render_template("404.html")


# @app.route('/addrec', methods=['POST', 'GET'])
# def addrec():
#     if request.method == 'POST':
#
#         username = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#
#         sql = "SELECT * FROM users WHERE username =?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, username)
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             return render_template('signup.html', msg="You are already a member, please login")
#         else:
#             insert_sql = "INSERT INTO users VALUES (?,?,?)"
#             prep_stmt = ibm_db.prepare(conn, insert_sql)
#             ibm_db.bind_param(prep_stmt, 1, username)
#             ibm_db.bind_param(prep_stmt, 2, email)
#             ibm_db.bind_param(prep_stmt, 3, password)
#             ibm_db.execute(prep_stmt)
#
#         return render_template('signup.html', msg="User Created Successfuly..")
#

# @app.route('/authenticate', methods=['POST', 'GET'])
# def authenticate():
#     global userId
#     if request.method == 'POST':
#
#         username = request.form['username']
#         password = request.form['password']
#
#         sql = "SELECT * FROM users WHERE username =? AND password=?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, username)
#         ibm_db.bind_param(stmt, 2, password)
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['USERNAME']
#             userId = account['USERNAME']
#             session['username'] = account['USERNAME']
#             return render_template('docs.html', msg="Logged in Successfully!!")
#         else:
#             msg = "Incorrect username/password"
#         return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('bbuser', None)
    return render_template('login.html')


# @app.route('/dashboard')
# def DashboardPage():
#     if 'loggedin' in session:
#         return render_template('dashboard.html')
#     else:
#         return ''


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/bbregister', methods=['GET', 'POST'])
def bbregister():
    if 'user' in session:

        if request.method == 'POST':

            username = request.form['bbname']
            email = request.form['bbemail']
            password = request.form['password']
            city = request.form['city']
            state = request.form['state']
            pincode = request.form['pincode']
            contact = request.form['contact']

            sql = "SELECT * FROM bbusers WHERE bbname =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)

            if account:
                return render_template('bbregister.html', msg="You are already a member, please login")
            else:
                insert_sql = "INSERT INTO bbusers VALUES (?,?,?,?,?,?,?)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt, 1, username)
                ibm_db.bind_param(prep_stmt, 2, email)
                ibm_db.bind_param(prep_stmt, 3, password)
                ibm_db.bind_param(prep_stmt, 4, city)
                ibm_db.bind_param(prep_stmt, 5, state)
                ibm_db.bind_param(prep_stmt, 6, pincode)
                ibm_db.bind_param(prep_stmt, 7, contact)
                ibm_db.execute(prep_stmt)

            return render_template('bbregister.html', msg="User Created Successfuly..")

        return render_template('bbregister.html')
    else:
        return render_template('404.html')


@app.route('/bblogin', methods=['GET', 'POST'])
def bblogin():
    if 'user' in session:
        global userId
        if request.method == 'POST':

            bbname = request.form['bbname']
            password = request.form['bbpassword']
            email = request.form['bbemail']

            sql = "SELECT * FROM bbusers WHERE bbname =? AND password=? AND email=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, bbname)
            ibm_db.bind_param(stmt, 2, password)
            ibm_db.bind_param(stmt, 3, email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)

            if account:
                session['user'] = bbname
                return redirect('donorlistfunc', code=302)
            else:
                msg = "Incorrect username/password"
            return render_template('bblogin.html', msg=msg)

        return render_template('bblogin.html')
    else:
        return render_template("404.html")


@app.route('/donorlistfunc', methods=['GET', 'POST'])
def donorlistfunc():
    if 'user' in session:
        donors = []
        sql = "SELECT * FROM dousers"
        stmt = ibm_db.exec_immediate(conn, sql)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            donors.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if "user" in session:
            return render_template('donorlistfunc.html', donors=donors)
        else:
            return render_template('404.html')


# @app.route('/bbaddrec', methods=['POST', 'GET'])
# def bbaddrec():
#     if request.method == 'POST':
#
#         username = request.form['bbname']
#         email = request.form['bbemail']
#         password = request.form['password']
#         city = request.form['city']
#         state = request.form['state']
#         pincode = request.form['pincode']
#         contact = request.form['contact']
#
#         sql = "SELECT * FROM bbusers WHERE bbname =?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, username)
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             return render_template('bbregister.html', msg="You are already a member, please login")
#         else:
#             insert_sql = "INSERT INTO bbusers VALUES (?,?,?,?,?,?,?)"
#             prep_stmt = ibm_db.prepare(conn, insert_sql)
#             ibm_db.bind_param(prep_stmt, 1, username)
#             ibm_db.bind_param(prep_stmt, 2, email)
#             ibm_db.bind_param(prep_stmt, 3, password)
#             ibm_db.bind_param(prep_stmt, 4, city)
#             ibm_db.bind_param(prep_stmt, 5, state)
#             ibm_db.bind_param(prep_stmt, 6, pincode)
#             ibm_db.bind_param(prep_stmt, 7, contact)
#             ibm_db.execute(prep_stmt)
#
#         return render_template('bbregister.html', msg="User Created Successfuly..")
#

# @app.route('/bbauthenticate', methods=['POST', 'GET'])
# def bbauthenticate():
#     global userId
#     if request.method == 'POST':
#
#         bbname = request.form['bbname']
#         password = request.form['bbpassword']
#         email = request.form['bbemail']
#
#         sql = "SELECT * FROM bbusers WHERE bbname =? AND password=? AND email=?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, bbname)
#         ibm_db.bind_param(stmt, 2, password)
#         ibm_db.bind_param(stmt, 3, email)
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['BBNAME']
#             userId = account['BBNAME']
#             session['bbname'] = account['BBNAME']
#             return render_template('donor_list.html', msg="Logged in Successfully!!")
#         else:
#             msg = "Incorrect username/password"
#         return render_template('bblogin.html', msg=msg)


@app.route('/doregister', methods=['GET', 'POST'])
def doregister():
    if "user" in session:
        if request.method == 'POST':

            username = request.form['name']
            email = request.form['email']
            city = request.form['city']
            state = request.form['state']
            pincode = request.form['pincode']
            contact = request.form['contact']
            blood = request.form['bg']
            disease = request.form['disease']
            date = request.form['date']

            sql = "SELECT * FROM dousers WHERE email =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)

            if account:
                return render_template('doregister.html', msg="You are already a registered")
            else:
                insert_sql = "INSERT INTO dousers VALUES (?,?,?,?,?,?,?,?,?)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt, 1, username)
                ibm_db.bind_param(prep_stmt, 2, email)
                ibm_db.bind_param(prep_stmt, 3, city)
                ibm_db.bind_param(prep_stmt, 4, state)
                ibm_db.bind_param(prep_stmt, 5, pincode)
                ibm_db.bind_param(prep_stmt, 6, contact)
                ibm_db.bind_param(prep_stmt, 7, blood)
                ibm_db.bind_param(prep_stmt, 8, disease)
                ibm_db.bind_param(prep_stmt, 9, date)
                ibm_db.execute(prep_stmt)

            return render_template('doregister.html', msg="Donor Registered Successfuly..")

        return render_template('doregister.html')
    else:
        return render_template("404.html")


# @app.route('/dologin',methods=['GET','POST'])
# def dologin():
#     global userId
#     if request.method == 'POST':
#         password = request.form['password']
#         email = request.form['email']
#
#         sql = "SELECT * FROM dousers WHERE email =? AND password=?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, email)
#         ibm_db.bind_param(stmt, 2, password)
#
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['EMAIL']
#             userId = account['EMAIL']
#             session['email'] = account['EMAIL']
#             return render_template('donor_list.html', msg="Logged in Successfully!!")
#         else:
#             msg = "Incorrect username/password"
#         return render_template('dologin.html', msg=msg)
#
#     return render_template('dologin.html')
#

# @app.route('/dolog', methods=['POST', 'GET'])
# def dolog():
#     global userId
#     if request.method == 'POST':
#         password = request.form['password']
#         email = request.form['email']
#
#         sql = "SELECT * FROM dousers WHERE email =? AND password=?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, email)
#         ibm_db.bind_param(stmt, 2, password)
#
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['EMAIL']
#             userId = account['EMAIL']
#             session['email'] = account['EMAIL']
#             return render_template('donor_list.html', msg="Logged in Successfully!!")
#         else:
#             msg = "Incorrect username/password"
#         return render_template('dologin.html', msg=msg)


# @app.route('/doregi', methods=['POST', 'GET'])
# def doregi():
#     if request.method == 'POST':
#
#         username = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#         city = request.form['city']
#         state = request.form['state']
#         pincode = request.form['pincode']
#         contact = request.form['contact']
#         blood = request.form['bg']
#
#         sql = "SELECT * FROM dousers WHERE username =?"
#         stmt = ibm_db.prepare(conn, sql)
#         ibm_db.bind_param(stmt, 1, username)
#         ibm_db.execute(stmt)
#         account = ibm_db.fetch_assoc(stmt)
#
#         if account:
#             return render_template('doregister.html', msg="You are already a member, please login")
#         else:
#             insert_sql = "INSERT INTO dousers VALUES (?,?,?,?,?,?,?,?)"
#             prep_stmt = ibm_db.prepare(conn, insert_sql)
#             ibm_db.bind_param(prep_stmt, 1, username)
#             ibm_db.bind_param(prep_stmt, 2, email)
#             ibm_db.bind_param(prep_stmt, 3, password)
#             ibm_db.bind_param(prep_stmt, 4, city)
#             ibm_db.bind_param(prep_stmt, 5, state)
#             ibm_db.bind_param(prep_stmt, 6, pincode)
#             ibm_db.bind_param(prep_stmt, 7, contact)
#             ibm_db.bind_param(prep_stmt, 8, blood)
#             ibm_db.execute(prep_stmt)
#
#         return render_template('doregister.html', msg="User Created Successfuly..")
#


@app.route('/donorlist')
def donorlist():
    if "user" in session:
        donors = []
        sql = "SELECT * FROM dousers"
        stmt = ibm_db.exec_immediate(conn, sql)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            donors.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if donors:
            return render_template('donor_list.html', donors=donors)
    else:
        return render_template("404.html")


# @app.route('/list')
# def list():
#   students = []
#   sql = "SELECT * FROM Students"
#   stmt = ibm_db.exec_immediate(conn, sql)
#   dictionary = ibm_db.fetch_both(stmt)
#   while dictionary != False:
#     # print ("The Name is : ",  dictionary)
#     students.append(dictionary)
#     dictionary = ibm_db.fetch_both(stmt)
#
#   if students:
#     return render_template("list.html", students = students)

@app.route('/requesthandler', methods=['GET', 'POST'])
def requesthandler():
    if "user" in session:
        user = session['user']
        if request.method == 'POST':
            username = request.form['username']
            sql = "SELECT * FROM transac WHERE duser =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)

            if account:
                return render_template('rh.html', msg="Donor is Busy", msg1="Try another donor in donor list")
            else:
                insert_sql = "INSERT INTO transac VALUES (?,?)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt, 1, user)
                ibm_db.bind_param(prep_stmt, 2, username)
                ibm_db.execute(prep_stmt)
                # sql1 = "select * from dousers where name=?"
                # prepa_stmt = ibm_db.prepare(conn, sql1)
                # ibm_db.bind_param(prepa_stmt, 1, username)
                # ibm_db.execute(prepa_stmt)
                # account1 = ibm_db.fetch_assoc(prep_stmt)
                # print(account1)
                sql1 = "SELECT * FROM dousers WHERE name =?"
                stmte = ibm_db.prepare(conn, sql1)
                ibm_db.bind_param(stmte, 1, username)
                ibm_db.execute(stmte)
                account = ibm_db.fetch_assoc(stmte)
                sql2 = "SELECT * FROM bbusers WHERE bbname =?"
                stmter = ibm_db.prepare(conn, sql2)
                ibm_db.bind_param(stmter, 1, user)
                ibm_db.execute(stmter)
                account1 = ibm_db.fetch_assoc(stmter)
                e = account["EMAIL"]
                ea = account1["EMAIL"]
                c = account1["CITY"]
                s = account1["STATE"]
                p = account1["PINCODE"]
                co = account1["CONTACT"]

                request_mail(user, e, ea, c, s, p, co)
        return render_template('rh.html', msg="user requested", msg1="we will convey with donor")


@app.route('/transaction')
def transaction():
    if "user" in session:
        tran = []
        sql = "SELECT * FROM transac"
        stmt = ibm_db.exec_immediate(conn, sql)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            tran.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if tran:
            return render_template('transaction.html', tran=tran)
        return render_template('transaction.html')
    else:
        return render_template("404.html")


@app.route('/trandis', methods=['GET', 'POST'])
def trandis():
    if "user" in session:

        if request.method == "POST":
            username = request.form['username']
            sql = "select * from bbusers where bbname=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            print(account)
            n = account["BBNAME"]
            e = account["EMAIL"]
            c = account["CITY"]
            s = account["STATE"]
            p = account["PINCODE"]
            co = account["CONTACT"]

            return render_template('trandis.html', account=account, n=n, e=e, c=c, s=s, p=p, co=co)
        else:
            return render_template("404.html")

#
# @app.route('/up')
# def up():
#     return render_template('up.html')
#
# @app.route('/uploader', methods = ['GET', 'POST'])
# def uploader():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(secure_filename(f.filename))
#       print(f.filename)
#       # n=f.filename
#       # file_extns=n.split(".")
#       # q=repr(file_extns[0])
#       # w=repr(file_extns[-1])
#       # a2 = q.strip("\'")
#       # print(q)
#       a = f.filename
#       b = a[:-1]
#       c = b[:-1]
#       d = c[:-1]
#       e = d[:-1]
#       print(e)
#       return render_template('up.html',msg=e)
