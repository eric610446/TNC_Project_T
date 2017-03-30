#-*- coding: utf-8 -*-　　
#-*- coding: cp950 -*-
import var
import telnetlib
import time

def telnet_connect():
	tn = telnetlib.Telnet(var.host,var.port,var.timeout)
	tn.read_until(var.login_key)
	tn.write(var.user+"\n")
	tn.read_until(var.passwd_key)
	tn.write(var.passwd+"\n")
	tn.read_until("csa>")
	var.tn = tn

def telnet_cmd(cmd_list,tn=''):
	if tn=='':
		tn = var.tn

	cmd_list = cmd_list.split(',')
	for cmd in cmd_list:
		tn.write(cmd)
		time.sleep(0.1)
	'''
	tn.write("mgr\r\nuser\r\n")
	tn.write("\033OQ")
	tn.write("\033OQ")
	tn.write("config 0\r\n")
	'''
	#tn.write("config 1\r\n")
	#tn.write("\n")
	#print tn.read_until('qqqj')
	var.tn = tn

def menu():
	print "1. 修改分機號碼"
	var.menu_choice = input("選擇: ")
	if var.menu_choice==1:
		if not profile_user():
			return 0
	return 1

def profile_user():
	var.profile_user_num_1 = raw_input("原來的分機號碼: ")
	var.profile_user_num_2 = raw_input("修改後的分機號碼: ")
	debug = str(var.profile_user_num_1)+" "+str(var.profile_user_num_2)
	if not user_num_debug(debug):
		return 0
	user_num_1 = var.profile_user_num_1.split(' ')
	for user in user_num_1:
		print user
		cmd = ''
		cmd += 'mgr -l GEA\r\nuser\r\nconsult\r\n\033OB\r\nshe\r\n\r\n\r\n\r\n\r\n\026\033OB\033OB'
		cmd += user+'\026'
		telnet_cmd( cmd )
		cmd = '\003\003\003\003'
		telnet_cmd( cmd )
		result = var.tn.read_until('csa')

	return 1









def user_num_debug(user_list):
	user_list = user_list.split(' ')
	for user in user_list:
		if( int(user)>=100000000 or int(user)<=99 ):
			return 0
	return 1