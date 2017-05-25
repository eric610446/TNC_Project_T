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

def telnet_cmd(cmd_list, tn='', sleep=0):
	if tn=='':
		tn = var.tn
	cmd_list = cmd_list.split(',')
	for cmd in cmd_list:
		tn.write(cmd)
		time.sleep(sleep)
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
	get_users_input()
	user_num_1 = var.users_input_1
	user_num_2 = var.users_input_2
	# log
	print '[*] user_num_1 : ',user_num_1
	print '[*] user_num_2 : ',user_num_2
	# 針對每一個分機去取得 address, type, entity 三個資料，並將原 user 的 address 設為 255-255-255
	for user in user_num_1:
		print '-------------------------------------------------'

		# 閱覽分機號碼設定
		result = read_user_settings( user )
		# 基本常遇到的錯誤訊息偵測
		error = error_dectect(result)
		if error:
			print '[-] '+user+' '+error
			continue

		# 儲存分機設定參數
		user_address = get_user_info(result,'address')
		user_type = get_user_info(result,'type')
		user_entity = get_user_info(result,'entity')
		arr = [user,user_address,user_type,user_entity]
		# 取得的資料存放在陣列中
		var.user_info_list.append(arr)
		print var.user_info_list

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

# 取得 分機號碼 的輸入
def get_users_input():
	# 讓使用者輸入分機號碼
	var.users_input_1 = raw_input("原來的分機號碼：")
	var.users_input_2 = raw_input("修改後的分機號碼：")
	# 檢查輸入的分機號碼有沒有太誇大
	debug_num_list = str(var.users_input_1)+" "+str(var.users_input_2)
	if not check_num_format( 'users', debug_num_list ):
		print '[-] 分機號碼輸入錯誤'
		return 0
	var.users_input_1 = var.users_input_1.split(' ')
	var.users_input_2 = var.users_input_2.split(' ')

# 數字的格式檢查，參數為 "檢查的號碼類型" 與 "號碼列表"
def check_num_format( num_type, debug_num_list ):
	if num_type == 'users':
		debug_num_list = debug_num_list.split(' ')
		for user in debug_num_list:
			if( int(user)>=100000000 or int(user)<=99 ):
				return 0
		return 1

# 讀取 分機號碼 設定資料
def read_user_settings( user ):# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	cmd = ''
	cmd += var.gotousers+'consult'+e+d+e+'she'+(e*5)+v+d+d+user+v
	print '[+] 讀取 '+user+' 的資料'
	telnet_cmd( cmd, sleep=0.01 )
	cmd = c*4
	telnet_cmd( cmd )
	result = var.tn.read_until('csa')
	return result

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
'''
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
'''
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

# 第一階段，常遇到的錯誤訊息偵測
def error_dectect(string=''):
	error=0
	tmp = string.split('no Such Object Instance')
	if len(tmp)>1:
		error = '分機號碼錯誤'

	try:
		res = tn.read_until('Invalid', timeout=1)
		print '[-] Invalid'
	except EOFError as e:
		print '[-] timeout ERROR'

	return error





def user_num_debug(user_list):
	user_list = user_list.split(' ')
	for user in user_list:
		if( int(user)>=100000000 or int(user)<=99 ):
			return 0
	return 1
