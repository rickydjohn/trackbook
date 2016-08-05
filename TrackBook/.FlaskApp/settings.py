#!/usr/bin/python

import MySQLdb
from login import connector
from gc import collect

def insert(nwdat):
	quer = "insert into userSettings"+str(tuple(nwdat.keys())).replace("'", "")+" values"+str(tuple(nwdat.values()))
	conn, curs = connector()
	curs.execute(quer)
	conn.commit()
	conn.close()
	collect()

def update(nwdat):
	conn, curs = connector()
	username = nwdat['username']
	nwdat.pop('username')
	for i in nwdat:
		quer = "update userSettings set "+str(i)+"=\""+str(nwdat[i])+"\" where username=\""+username+"\"" 
		curs.execute(quer)
		conn.commit()
	conn.close()
	collect()

def checker(username):
	conn, curs = connector()
	quer = "select username, preferCurrency, spendingLimit, emailAddress, annualSalary, gender from userSettings where username='"+str(username)+"'"
	curs.execute(quer)
	dat = curs.fetchall()
	conn.close()
	collect()
	if len(dat) > 0:
		return True, dat[0][0], dat[0][1], dat[0][2], dat[0][3], dat[0][4], dat[0][5]
	else:
		return False, None, None, None, None, None, None

def modify(data):
	nwdat = {}
	for i in data:
		nwdat[i[0]] = i[1]
	dat = checker(nwdat['username'])
	if dat[0] == False:
		insert(nwdat)		
	else:
		update(nwdat)
