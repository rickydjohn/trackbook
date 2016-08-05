#!/usr/bin/python

import MySQLdb

def login(username, password):
	conn = MySQLdb.connect('localhost', 'root', 'psne', 'tracker')
	curs = conn.cursor()
	quer = "select fname, username from users where status=\"y\" and (username=\""+str(username)+"\" and password=\""+str(password)+"\")"
	curs.execute(quer)
	dat = curs.fetchall()
	if len(dat) > 0:
		login = True
		fname = dat[0][0]
		uname = dat[0][1]
		return login, fname, uname
	else:
		login = False
		fname = None
		uname = None
		return login, fname, uname
	conn.close()

def delete(username):
	conn = MySQLdb.connect('localhost', 'root', 'psne', 'tracker')
	curs = conn.cursor()
	quer = "update users set status=\"n\" where username=\""+str(username)+"\""
	curs.execute(quer)
	conn.commit()
	conn.close()

def connector():
	conn = MySQLdb.connect('localhost', 'root', 'psne', 'tracker')
	curs = conn.cursor()
	return conn, curs
