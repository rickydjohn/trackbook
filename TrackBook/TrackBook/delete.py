#!/usr/bin/python

from login import connector

def delete():
	conn, curs = connector()
	quer = "show tables"
	curs.execute(quer)
	tables = curs.fetchall()
	table = []
	for i in tables:
		if i[0] != 'users':
			quer = "delete from "+str(i[0])+ " where username='"+str(user)


delete()

