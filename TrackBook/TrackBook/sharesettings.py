#!/usr/bin/python

from login import connector

def checkuser(usernames):
	confuser = []
	conn, curs = connector()
	for i in usernames.split(","):
		user = i.encode('ascii', 'ignore').rstrip().lstrip()
		quer = "select username from users where username='"+str(user)+"'"
		curs.execute(quer)
		if curs.rowcount > 0:
			confuser.append(user)
	return confuser

def deleteTag(username, shareTag):
	conn, curs = connector()
	quer = "select shareTagID from shares where username='"+username+"' and shareTag='"+shareTag+"'"
	curs.execute(quer)
	dat = curs.fetchall()
	if len(dat) > 0:
		quer = "delete from sharesWith where shareTagID='"+str(dat[0][0])+"'"
		curs.execute(quer)
		conn.commit()
		quer = "delete from shares where username='"+username+"' and shareTag='"+shareTag+"'"
		curs.execute(quer)
		conn.commit()
		return True
	else:	
		return False
	conn.close()

def sharingWith(uname, shareTag, usernames):
	conn, curs = connector()
	quer = "select shareTagID from shares where username='"+uname+"' and shareTag='"+shareTag+"'"
	curs.execute(quer)
	shareId = curs.fetchall()[0][0]
	username = checkuser(usernames)
	for i in username:
		if i != str(uname):
			quer = "insert into sharesWith(username, shareTagID) values('"+i.encode('ascii', 'ignore').rstrip().lstrip()+"', '"+str(shareId)+"')"
			curs.execute(quer)
			conn.commit()
		
def createTag(username, shareTag, meshare):
	conn, curs = connector()
	quer = "select shareTag from shares where shareTag='"+str(shareTag)+"'"
	curs.execute(quer)
	ifexit = curs.fetchall()
	if len(ifexit) == 0:
		quer = "insert into shares(username, shareTag) values('"+username+"','"+shareTag+"')"
		curs.execute(quer)
		conn.commit()
		sharingWith(username, shareTag, meshare)
		return True
	else:
		return False
	conn.close()

def getGroup(username):
	shares = []
	conn, curs = connector()
	quer = "select shareTag from shares where username='"+str(username)+"'"
	curs.execute(quer)
	if curs.rowcount > 0:
		for i in curs.fetchall():
			shares.append(i[0])
	quer = "select shares.shareTag from shares join sharesWith on shares.shareTagID=sharesWith.shareTagID where sharesWith.username='"+str(username)+"'"
	curs.execute(quer)
	if curs.rowcount > 0:
		for i in curs.fetchall():
			shares.append(i[0])
	conn.close()
	if len(shares) > 0:
		return shares
	else:
		return None


def spendingTrends(username, form):
	conn, curs = connector()
	if form['shareTag'] == "None":
		quer = "SELECT spentOn, spentAt, amount, share, sharetag, created, username FROM expense WHERE DATE_FORMAT(created, '%Y-%m-%d') BETWEEN '"+str(form['fromDate'])+"' AND '"+str(form['toDate'])+"' and username='"+str(username)+"'"
		curs.execute(quer)
		dat = curs.fetchall()
		if len(dat) > 0:
			quer = "SELECT sum(amount) FROM expense WHERE DATE_FORMAT(created, '%Y-%m-%d') BETWEEN '"+str(form['fromDate'])+"' AND '"+str(form['toDate'])+"' and username='"+str(username)+"'"
			curs.execute(quer)
			total = curs.fetchall()[0][0]
			return dat, total
		else:
			return None, None
	else:
		quer = "SELECT spentOn, spentAt, amount, share, sharetag, created, username FROM expense WHERE DATE_FORMAT(created, '%Y-%m-%d') BETWEEN '"+str(form['fromDate'])+"' AND '"+str(form['toDate'])+"' and shareTag='"+str(form['shareTag'])+"'"
		curs.execute(quer)
		dat = curs.fetchall()
		if len(dat) > 0:
			quer = "SELECT sum(amount) FROM expense WHERE DATE_FORMAT(created, '%Y-%m-%d') BETWEEN '"+str(form['fromDate'])+"' AND '"+str(form['toDate'])+"' and shareTag='"+str(form['shareTag'])+"'"
			curs.execute(quer)
			total = curs.fetchall()[0][0]
			return dat, total
		else:
			return None, None
	conn.close()


def sharesForSettings(username):
	myshares = {}
	conn, curs = connector()
	quer = "select shareTag, shareTagID from shares where username='"+str(username)+"'"
	curs.execute(quer)
	if curs.rowcount > 0:
		dat = curs.fetchall()
		for i in dat:
			myshares[i[0]] = {}
			quer = "select username from sharesWith where shareTagID='"+str(i[1])+"'"
			curs.execute(quer)
			if curs.rowcount > 0:
				sharings = []
				for j in curs.fetchall():
					sharings.append(j[0])
				myshares[i[0]]['sharingWith'] = sharings
	conn.close()
	return myshares


def deleteWith(uname, shareTag, usernames):
	conn, curs = connector()
	quer = "select shareTagID from shares where username='"+uname+"' and shareTag='"+shareTag+"'"
	curs.execute(quer)
	shareId = curs.fetchall()[0][0]
	username = checkuser(usernames)
	for i in username:
		if i != str(uname):
			quer = "delete from sharesWith where username='"+str(i.rstrip().lstrip())+"' and shareTagID='"+str(shareId)+"'"
			curs.execute(quer)
			conn.commit()
		
def updateShareSettings(uname, shareTag, shareWith):
	conn, curs = connector()
	quer = "select ShareTagID from shares where shareTag='"+str(shareTag)+"'"
	curs.execute(quer)
	shareTagID=curs.fetchall()[0][0]
	curShares = []
	quer = "select username from sharesWith where shareTagID='"+str(shareTagID)+"'"
	curs.execute(quer)
	if curs.rowcount > 0:
		for i in curs.fetchall():
			curShares.append(i[0])
	exshares = checkuser(shareWith)
	new = []
	for i in exshares:
		if i in curShares:
			curShares.remove(i)
		elif i not in curShares:
			new.append(i)
	if len(curShares) == 0 and len(new) == 0:
		pass
	elif len(curShares) > 0 and len(new) > 0:
		for j in curShares:
			deleteWith(uname, shareTag, j)
		for k in new:
			sharingWith(uname, shareTag, k)
	elif len(curShares) == 0 and len(new) > 0:
		for k in new:
			sharingWith(uname, shareTag, k)
	elif len(curShares) > 0 and len(new) == 0:
		for j in curShares:
			deleteWith(uname, shareTag, j)
