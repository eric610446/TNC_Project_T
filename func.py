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
		if not change_user_num():
			return 0
	return 1

def change_user_num():
	# 引用全域變數
	global e, c, v, u, d, l, r, b
	# 讓使用者輸入分機號碼
	var.profile_user_num_1 = raw_input("原來的分機號碼: ")
	var.profile_user_num_2 = raw_input("修改後的分機號碼: ")
	# 檢查輸入的分機號碼有沒有太誇大
	debug = str(var.profile_user_num_1)+" "+str(var.profile_user_num_2)
	if not user_num_debug(debug):
		return 0
	# 將輸入的原來的分機號碼，依照空格去分開，因為可以輸入多個分機，如: 100 101 ..
	user_num_1 = var.profile_user_num_1.split(' ')
	user_num_2 = var.profile_user_num_2.split(' ')
	# 針對每一個分機去取得 address, type, entity 三個資料，並將原 user 的 address 設為 255-255-255
	for user in user_num_1:
		#print user
		cmd = ''
		cmd += var.gotousers+'consult'+e+d+e+'she'+(e*5)+v+d+d
		cmd += user+v
		telnet_cmd( cmd )
		cmd = c*4
		telnet_cmd( cmd )
		result = var.tn.read_until('csa')
		error = error_dectect(result)
		if error:
			print '[-] '+user+' '+error
			continue
		user_address = get_user_info(result,'address')
		user_type = get_user_info(result,'type')
		user_entity = get_user_info(result,'entity')
		arr = [user,user_address,user_type,user_entity]
		# 取得的資料存放在陣列中
		var.user_info_list.append(arr)
		# 將要修改分機號碼的使用者 port 改為 255
		user_port_list = []
		user_port = [user,'255-255-255']
		user_port_list.append(user_port)
		setting_users_ports( user_port_list, tn )
	# profile user form user1 and setting
	for user_info in var.user_info_list:
		user1_for_profile.append(user_info[0])
		arr = [ user_info[2], user_info[3], user_info[1] ]
		data_for_profile.append(arr)
	profile_user( user1_for_profile, user_num_2, data_for_profile )
	return 1


def profile_user( user1, user2, data='', key='' ):
	# 引用全域變數
	global e, c, v, u, d, l, r, b

	cmd = goto_profile_create
	i = 0
	for user in user1:
		cmd += u*16+d+(b*8)+user
		if data=='':
			cmd+=u*8
			cmd+=(b*8)+user2[i]
		else:
			cmd += (d*3)+e+data[i][0]+e+d+(b*8)+data[i][1]
			addr = data[i][2].split('-')
			cmd += d+(b*8)+addr[0]+d+(b*8)+addr[1]+d+(b*8)+addr[2]
			cmd += d
			cmd += (b*8)+user2[i]+d
			if key=='':
				cmd += (b*8)+user2[i]

		i += 1

def setting_users_ports( user_port_list, tn ):
	# 引用全域變數
	global e, c, v, u, d, l, r, b

	cmd = var.gotousers+'consult'+e+d+e+'she'+(e*3)+v+(d*2)
	telnet_cmd( cmd, tn )
	for user in user_port_list:
		address = user[1].split('-')
		cmd = b*8+user[0]+v+(b*8)+address[0]+d+(b*8)+address[1]+d+(b*8)+address[2]+v
		telnet_cmd( cmd, tn )
		try:
			res = tn.read_until('succeeded', timeout=1)
			cmd = v
		except:
			try:
				res = tn.read_until('Invalid', timeout=1)
				print '[-] '+user[0]+' 設定 address '+user[1]+' : Invalid physical address'
			except EOFError as e:
				print '[-] '+user[0]+' 設定 address '+user[1]+' timeout ERROR'
		telnet_cmd( cmd, tn )

	cmd = c*3
	telnet_cmd( cmd, tn )
	tn.read_until('csa')
	var.tn = tn

def read_user_info():
	print 'read user info :'
	for user in var.user_info_list:
		print user
		for info in user:
			print info


def get_user_info(string,info):
	result = ''
	if info=='address':
		tmp = string.split('Shelf Address : ')
		tmp = tmp[1].split('[')
		result += tmp[0][:-1]
		tmp = string.split('Board Address : ')
		tmp = tmp[1].split('[')
		result += "-"+tmp[0][:-1]
		tmp = string.split('Equipment Address : ')
		tmp = tmp[1].split('[')
		result += "-"+tmp[0][:-1]
	if info=='type':
		tmp = string.split('Set Type + ')
		tmp = tmp[1].split('[')
		result += tmp[0][:-1]
	if info=='entity':
		tmp = string.split('Entity Number : ')
		tmp = tmp[1].split('[')
		result += tmp[0][:-1]

	return result

def error_dectect(string):
	result=0
	tmp = string.split('no Such Object Instance')
	if len(tmp)>1:
		result = '分機號碼錯誤'
	return result





def user_num_debug(user_list):
	user_list = user_list.split(' ')
	for user in user_list:
		if( int(user)>=100000000 or int(user)<=99 ):
			return 0
	return 1