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

def telnet_cmd(cmd_list, wait=0, tn=''):
	if tn=='':
		tn = var.tn
	cmd_list = cmd_list.split(',')
	for cmd in cmd_list:
		tn.write(cmd)
		if wait!=0:
			time.sleep(wait)
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
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# 讓使用者輸入分機號碼
	var.profile_user_num_1 = raw_input("原來的分機號碼: ")
	var.profile_user_num_2 = raw_input("修改後的分機號碼: ")
	# 檢查輸入的分機號碼有沒有太誇大
	debug = str(var.profile_user_num_1)+" "+str(var.profile_user_num_2)
	if not user_num_debug(debug):
		print '[-] 分機號碼輸入錯誤'
		return 0
	# 將輸入的原來的分機號碼，依照空格去分開，因為可以輸入多個分機，如: 100 101 ..
	user_num_1 = var.profile_user_num_1.split(' ')
	user_num_2 = var.profile_user_num_2.split(' ')
	# 針對每一個分機去取得 address, type, entity 三個資料，並將原 user 的 address 設為 255-255-255
	for user in user_num_1:
		print '-------------------------------------------------'
		cmd = ''
		cmd += var.gotousers+'consult'+e+d+e+'she'+(e*5)+v+d+d
		cmd += user+v
		print '[+] 讀取 '+user+' 的資料'
		wait = 0.001
		telnet_cmd( cmd, wait )
		cmd = c*4
		telnet_cmd( cmd )
		result = detect_error('csa')
		if not key_in_string('Shelf,Board,Equipment,Type,Entity', result):
			print result
			wait*=10
			telnet_cmd( cmd, wait )
			if wait>1:
				print '[-] '+user+' 讀取資料錯誤'
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
		setting_users_ports( user_port_list, var.tn )
	# profile user form user1 and setting
	user1_for_profile = []
	user2_for_profile = []
	for user in user_num_2:
		user2_for_profile.append(user)
	data_for_profile = []
	for user_info in var.user_info_list:
		user1_for_profile.append(user_info[0])
		arr = [ user_info[2], user_info[3], user_info[1] ]
		data_for_profile.append(arr)
	profile_user( user1_for_profile, user2_for_profile, data_for_profile )
	user_for_delete = user1_for_profile
	delete_user( user_for_delete )
	return 1

def delete_user( user_for_delete ):
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	cmd = var.gotousers+'delete'+e+d
	telnet_cmd( cmd )
	for user in user_for_delete:
		cmd = b*8+user+v
		telnet_cmd( cmd )
		try:
			res = var.tn.read_until('succeeded', timeout=1)
		except:
			try:
				res = var.tn.read_until('no Such Object', timeout=1)
				print '[-] Delete '+user+' 分機號碼不存在'
			except:
				try:
					res = var.tn.read_until('Bad value', timeout=1)
					print '[-] Delete '+user+' Bad value'
				except:
					print '[-] Delete '+user+' timeout'
		cmd = v
		telnet_cmd( cmd )



def profile_user( old, new, data='', key='' ):
	print '[+] porfile user '
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end

	cmd = var.goto_profile_create
	telnet_cmd( cmd )
	i = 0
	for user in old:
		cmd = u*16+d+(b*8)+new[i]
		if data=='':
			cmd+=u*8
			cmd+=(b*8)+user
		else:
			cmd += (d*3)+e+data[i][0]+e+d+(b*8)+data[i][1]
			addr = data[i][2].split('-')
			cmd += d+(b*8)+addr[0]+d+(b*8)+addr[1]+d+(b*8)+addr[2]
			cmd += d
			cmd += (b*8)+user+d
			if data[i][0]!='analog':
				cmd += (b*8)+user
		cmd += v*2
		telnet_cmd( cmd )
		i += 1
	cmd = c*3
	telnet_cmd( cmd )
	var.tn.read_until('csa')

def setting_users_ports( user_port_list, tn ):
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end

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

def key_in_string(key_list,string):
	key_list = key_list.split(',')
	for key in key_list:
		if key in string:
			continue
		else:
			return 0
	return 1

def detect_error(key_list='', tn=''):
	r = 0
	if tn=='':
		tn = var.tn
	if key_list!='':
		key_list = key_list.split(',')
		for key in key_list:
			try:
				print key
				r = tn.read_until(key, timeout=0.001)
			except:
				try:
					print key
					r= tn.read_until(key, timeout=0.01)
				except:
					try:
						print key
						r= tn.read_until(key, timeout=0.1)
					except:
						try:
							print key
							r= tn.read_until(key, timeout=1)
						except:
							try:
								print key
								tn.read_until('no Such Object', timeout=0.1)
								print '[-] no Such Object'
								return 1
							except:
								try:
									print key
									tn.read_until('Bad value', timeout=0.1)
									print '[-] Bad value'
									return 1
								except:
									try:
										print key
										tn.read_until('Invalid', timeout=0.1)
										print '[-] Invalid'
										return 1
									except:
										print key
										print '[-] Timeout'
										return 1
	return r




def user_num_debug(user_list):
	user_list = user_list.split(' ')
	for user in user_list:
		if( int(user)>=100000000 or int(user)<=99 ):
			return 0
	return 1