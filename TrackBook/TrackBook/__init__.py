#!/usr/bin/python

from flask import Flask, render_template, request, url_for, session, flash, redirect
from gc import collect
from settings import modify
from sharesettings import *
import re
import login

app = Flask(__name__)
app.debug = True
app.secret_key="somekey"
CoName = "Trackbook"

@app.route('/login/', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def main():
	if request.method == "GET":
		if 'username' in session:
			conn, curs = login.connector()
			#total amount
			quer = "select sum(amount) from expense where created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW()) and username=\""+str(session['uname'])+"\""
			curs.execute(quer)
			total = curs.fetchall()[0][0]
			if total != None:
				total = total
			else:
				total = 0
			#Personal amount
			pquer = "select sum(amount) from expense where (share='personal' and created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW())) and username='"+str(session['uname'])+"'"
			curs.execute(pquer)
			ptotal = curs.fetchall()[0][0]
			#shared amount
			squer = "select sum(amount) from expense where (share='shared' and created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW())) and username='"+str(session['uname'])+"'"
			curs.execute(squer)
			stotal = curs.fetchall()[0][0]
			#shared amount
			ttquer = "select spendingLimit from userSettings where username='"+str(session['uname'])+"'"
			curs.execute(ttquer)
			tttotal = curs.fetchall()
			if len(tttotal) > 0:
				if tttotal[0][0] != None:
					tttotal = tttotal[0][0] - total
			else:
				tttotal = None
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
			quer = "select sum(amount) from expense where created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW()) and username=\""+str(session['uname'])+"\""
			curs.execute(quer)
			total = curs.fetchall()[0][0]
			if total != None:
				total = total
			else:
				total = 0
			pquer = "select sum(amount) from expense where (share='personal' and created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW())) and username='"+str(session['uname'])+"'"
			curs.execute(pquer)
			ptotal = curs.fetchall()[0][0]
			squer = "select sum(amount) from expense where (share='shared' and created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW())) and username='"+str(session['uname'])+"'"
			curs.execute(squer)
			stotal = curs.fetchall()[0][0]
			ttquer = "select spendingLimit from userSettings where username='"+str(session['uname'])+"'"
			curs.execute(ttquer)
			tttotal = curs.fetchall()
			if len(tttotal) > 0:
				if tttotal[0][0] != None:
					tttotal = tttotal[0][0] - total
			else:
				tttotal = None
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
	else:
		flash("You cannot access this page")
		return redirect(url_for('main'))

@app.route('/trackExpense/', methods=['GET', 'POST'])
def trackExpense():
	if 'username' in session:
		conn, curs = login.connector()
		quer =  "select distinct(spentAt) from expense where username='"+str(session['uname'])+"'"
		curs.execute(quer)
		places = curs.fetchall()
		place = []
		if len(places) > 0:
			for i in places:
				place.append(i[0].rstrip())
		if request.method == 'GET':
			shares = getGroup(session['uname'])
			collect()
			return render_template('trackExpense.html', CoName=CoName, name=session['username'], place=place, shares=shares)
		elif request.method == "POST":
			col = []
			val = []
			mutDict = {}
			for i in request.form:
				mutDict[i] = request.form[i]
			if mutDict['share'] == 'personal':
				mutDict['shareTag']
			if mutDict['share'] == 'personal':
				mutDict.pop('shareTag')
			for j in mutDict:
				col.append(j), val.append(mutDict[j].encode('ascii', 'ignore'))
			col.append("username")
			val.append(session['uname'].encode('ascii', 'ignore'))
			quer = "insert into expense"+re.sub('\'', '', str(tuple(col))) + " values"+str(tuple(val))
			conn, curs = login.connector()
			curs.execute(quer)
			conn.commit()
			shares = getGroup(session['uname'])
			collect()
			flash("Data has been saved for further tracking.")
			return render_template('trackExpense.html', CoName=CoName, name=session['username'], shares=shares, place=place)
	else:
		flash("login to continue")
		return redirect(url_for("main"))
		
@app.route('/settings/', methods=['GET', 'POST'])
def settings():
	if 'username' in session:
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
	else:
		flash("Please login to continue")
		return redirect(url_for("main"))


@app.route('/updatesharingsetting/', methods=["POST"])
@app.route('/sharingsetting/', methods=["GET","POST"])
def sharingsetting():
	if 'username' in session:
		if request.method == "GET":
			dat = sharesForSettings(session['uname'])
			if len(dat) > 0:
				return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=dat)
			else:
				return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=None)
		elif request.method == "POST":
			if request.path == "/sharingsetting/":
				creTag = createTag(session['uname'], request.form['shareTag'], request.form['shareWith'])
				if creTag == True:
					dat = sharesForSettings(session['uname'])
					if len(dat) > 0:
						flash("created new share tag")
						return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=dat)
					else:
						flash("created new share tag")
						return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=None)
				else:
					dat = sharesForSettings(session['uname'])
					if len(dat) > 0:
						flash("This share tag exists. Please create a new one")
						return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=dat)
					else:
						flash("This share tag exists. Please create a new one")
						return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=None)
			elif request.path == "/updatesharingsetting/":
				if request.form['submitaction'] == "delete":
					deleteTag(session['uname'], request.form['shareTag'])		
					dat = sharesForSettings(session['uname'])
					if len(dat) > 0:
						flash("Share Tag has been deleted")
						return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=dat)
					else:
						flash("Share Tag has been deleted")
						return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=None)
				elif request.form['submitaction'] == "update":
					updateShareSettings(session['uname'], request.form['shareTag'], request.form['shareWith'])
					dat = sharesForSettings(session['uname'])
					flash("Share settings has been updated")
					return render_template('sharingsetting.html', CoName=CoName, name=session['username'], data=dat)
	else:
		flash("Please login to browse")
		return redirect(url_for('main'))

@app.route('/spendingTrend/', methods=["POST", "GET"])
def spendingTrend():
	conn, curs = login.connector()
	if 'username' in session:
		if request.method == "GET":
			quer = "select spentOn, spentAt, amount, share, sharetag, created, username from expense where created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW()) and username='"+str(session['uname'])+"'"
			curs.execute(quer)
			dat = curs.fetchall()
			if len(dat) > 0:
				quer = "select sum(amount) from expense where created > (created between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW()) and username='"+str(session['uname'])+"'"
				curs.execute(quer)
				total = curs.fetchall()[0][0]
				dat = dat
			else:
				dat = None
			shares = getGroup(session['uname'])
			return render_template('spendingTrend.html', CoName=CoName, name=session['username'], data=dat, method=request.method, shares=shares, total=total)
		elif request.method == "POST":
			shares = getGroup(session['uname'])
			dat = spendingTrends(session['uname'], request.form)
			collect()
			return render_template('spendingTrend.html', CoName=CoName, name=session['username'], data=dat[0], total=dat[1], method=request.method, fromDate=request.form['fromDate'], toDate=request.form['toDate'], shares=shares)
		conn.close()
	else:
		flash("Please login to browse")
		return redirect(url_for('main'))

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
