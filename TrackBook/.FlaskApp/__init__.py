#!/usr/bin/python

from flask import Flask, render_template, request, url_for, session, flash, redirect
from gc import collect
from settings import modify
import re
import login

app = Flask(__name__)
app.debug = True
app.secret_key="4ef21738a9c2e5b16ab2f6e7f4cef8a6"
CoName = "Trackbook"

@app.route('/login/', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def main():
	if request.method == "GET":
		if 'username' in session:
			conn, curs = login.connector()
			#total amount
			quer = "select sum(amount) from expense where username=\""+str(session['uname'])+"\""
			curs.execute(quer)
			total = curs.fetchall()[0][0]
			#Personal amount
			pquer = "select sum(amount) from expense where share='personal' and username='"+str(session['uname'])+"'"
			curs.execute(pquer)
			ptotal = curs.fetchall()[0][0]
			#shared amount
			squer = "select sum(amount) from expense where share='shared' and username='"+str(session['uname'])+"'"
			curs.execute(squer)
			stotal = curs.fetchall()[0][0]
			#shared amount
			ttquer = "select spendingLimit from userSettings where username='"+str(session['uname'])+"'"
			curs.execute(ttquer)
			tttotal = curs.fetchall()
			print tttotal
			if len(tttotal) > 0:
				tttotal = tttotal[0][0] - total
			else:
				tttotal = None
			print tttotal
			conn.close()
			collect()
			return render_template('main.html', CoName=CoName, name=session['username'], total=total, ptotal=ptotal, stotal=stotal, tttotal=tttotal)
		else:
			return render_template('main.html', CoName=CoName)
	elif request.method == "POST":
		amI = login.login(request.form['username'], request.form['password'])
		if amI[0] == True:
			session['username'] = amI[1]
			session['uname'] = amI[2]
			conn, curs = login.connector()
			quer = "select sum(amount) from expense where username=\""+str(amI[2])+"\""
			curs.execute(quer)
			total = curs.fetchall()[0][0]
			pquer = "select sum(amount) from expense where share='personal' and username='"+str(session['uname'])+"'"
			curs.execute(pquer)
			ptotal = curs.fetchall()[0][0]
			squer = "select sum(amount) from expense where share='shared' and username='"+str(session['uname'])+"'"
			curs.execute(squer)
			stotal = curs.fetchall()[0][0]
			ttquer = "select spendingLimit from userSettings where username='"+str(session['uname'])+"'"
			curs.execute(ttquer)
			tttotal = curs.fetchall()
			print tttotal
			if len(tttotal) > 0:
				tttotal = tttotal[0][0] - total
			else:
				tttotal = None
			print tttotal
			conn.close()
			collect()
			return render_template('main.html', CoName=CoName, name=session['username'], total=total, ptotal=ptotal, stotal=stotal, tttotal=tttotal)
		else:
			flash("incorrect username or password.")
			return render_template('main.html', CoName=CoName)
		
@app.route('/register/', methods=['POST'])
def register():
	conn, curs = login.connector()
	if request.method == "POST":
		col = []
		val = []
		for i in request.form:
			col.append(i), val.append(request.form[i].encode('ascii', 'ignore'))
		quer = "insert into users"+re.sub('\'', '', str(tuple(col))) + " values"+str(tuple(val))
		try:
			curs.execute(quer)
			conn.commit()
			conn.close()
			collect()
			session['username'] = request.form['fname']
			session['uname'] = request.form['username']
			return render_template('register.html', CoName=CoName, name=session['username'])
		except:
			flash("This username is not available.")
			return render_template('main.html', CoName=CoName)

@app.route('/trackExpense/', methods=['GET', 'POST'])
def trackExpense():
	if request.method == 'GET':
		return render_template('trackExpense.html', CoName=CoName, name=session['username'])
	elif request.method == "POST":
		col = []
		val = []
		for i in request.form:
			col.append(i), val.append(request.form[i].encode('ascii', 'ignore'))
		col.append("username")
		val.append(session['uname'].encode('ascii', 'ignore'))
		quer = "insert into expense"+re.sub('\'', '', str(tuple(col))) + " values"+str(tuple(val))
		conn, curs = login.connector()
		curs.execute(quer)
		conn.commit()
		conn.close()
		collect()
		flash("Data has been saved for further tracking.")
		return render_template('trackExpense.html', CoName=CoName, name=session['username'])
		
@app.route('/settings/', methods=['GET', 'POST'])
def settings():
	if request.method == "GET":
		conn, curs = login.connector()
		quer = "select preferCurrency, spendingLimit, emailAddress, annualSalary, gender from userSettings where username=\""+str(session['uname'])+"\""
		curs.execute(quer)
		dat = curs.fetchall()
		if len(dat) > 0:
			return render_template('settings.html', CoName=CoName, name=session['username'], data=dat)
		else:
			return render_template('settings.html', CoName=CoName, name=session['username'], data=None)
		conn.close()
		collect()
	elif request.method == "POST":
		key = []
		val = []
		for k, v in request.form.iteritems():
			key.append(k.encode('ascii', 'ignore')), val.append(v.encode('ascii', 'ignore'))
		key.append('username')
		val.append(session['uname'].encode('ascii', 'ignore'))
		modify(zip(key, val))
		conn, curs = login.connector()
		quer = "select preferCurrency, spendingLimit, emailAddress, annualSalary, gender from userSettings where username=\""+str(session['uname'])+"\""
		curs.execute(quer)
		dat = curs.fetchall()
		flash("Your settings has been updated.")
		return render_template('settings.html', CoName=CoName, name=session['username'], data=dat)
		conn.close()
		collect()

@app.route('/logout/', methods=['GET'])
def logout():
	session.pop('username', None)
	return render_template('main.html', CoName=CoName)

@app.route('/delete/')
def delete():
	login.delete(session['uname'].encode('ascii', 'ignore'))
	return redirect(url_for('logout'))


@app.route('/error/')
def error_page():
    return render_template('error.html', CoName=CoName, name=session['username'])

@app.errorhandler(500)
@app.errorhandler(405)
@app.errorhandler(404)
def page_not_found(error):
        if 'username' in session:
                return redirect(url_for('error_page'))
        else:
                return "errorr"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
