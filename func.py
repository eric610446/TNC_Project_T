#-*- coding: utf-8 -*-
#-*- coding: cp950 -*-
import var
import telnetlib
import time
import os

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
	print "\n\t1. 修改分機號碼"
	print "\n\t0. 結束"
	var.menu_choice = input("\n\t選擇: ")
	if var.menu_choice==0:
		return 'exit'
	if var.menu_choice==1:
		if not change_user_num():
			return 0
	return 1

def change_user_num():
	os.system('cls')
	print '\n\n\t\t[ 修改分機號碼 ]\n\t'+'-'*80
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# 讓使用者輸入分機號碼
	get_users_input()
	user_num_1 = var.users_input_1
	user_num_2 = var.users_input_2
	# log
	#print '\n\t[*] user_num_1 : ',user_num_1
	#print '\n\t[*] user_num_2 : ',user_num_2

	# 將 profile data 每個 user1 對應到自己的 user2 號碼
	i=0
	for user in user_num_1:
		var.user_info_list[user] = {}
		var.user_info_list[user]['new_number'] = user_num_2[i]
		i+=1

	# 針對每一個分機去取得 address, type, entity 三個資料，並將原 user 的 address 設為 255-255-255
	error_user_list = []
	for user in var.user_info_list:
		print '\n\n\n\n\t>>>>>>  讀取分機 '+user+' 設定並登出  <<<<<<'

		# 閱覽分機號碼設定
		error = read_user_settings( user )
		if error:
			# 如果在這邊讀取設定失敗了，要把 user 踢出修改分機號碼的清單，var.user_info_list
			print '\n\t[-] 在讀取分機 '+user+' 的設定時發生錯誤 : '+error
			error_user_list.append(user)
			continue

		# 將要修改分機號碼的使用者 port 改為 255
		error = modify_user( user, address='255-255-255' )
		if error:
			# 如果在這邊讀取設定失敗了，要把 user 踢出修改分機號碼的清單，var.user_info_list
			print '\n\t[-] 在 logout 分機 '+user+' 時發生錯誤 : '+error
			error_user_list.append(user)
			continue
	# 將有產生錯誤的 user 踢掉
	for user in error_user_list:
		var.user_info_list.pop(user, None)

	# 如果沒有抓到任何一支分機的資料，回傳 0
	if not bool(var.user_info_list):
		return 0

	# 拷貝新分機
	profile_data = var.user_info_list
	profile_user( profile_data )
	print var.user_info_list

	'''
	delete_user( user_for_delete )
	'''
	return 1

# 取得 分機號碼 的輸入
def get_users_input():
	# 讓使用者輸入分機號碼
	var.users_input_1 = raw_input("\n\t原來的分機號碼：")
	var.users_input_2 = raw_input("\n\t修改後的分機號碼：")
	# 檢查輸入的分機號碼有沒有太誇大
	debug_num_list = str(var.users_input_1)+" "+str(var.users_input_2)
	if not check_num_format( 'users', debug_num_list ):
		print '\n\t[-] 分機號碼輸入錯誤'
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

def modify_user( user, address='', user_type='', entity='' ):
	log = '\n\t[+] 設定分機 '+user
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'consult'+e+d+e

	# 先將所有設定選項都準備好
	info_change = 0
	if address!='':
		log += ' address='+address
		cmd+='she'+(e*3)
		if address!=var.user_info_list[user]['user_address']:
			info_change = 1
	if user_type!='':
		log += ' user_type='+user_type
		cmd+='type'+e
		if user_type!=var.user_info_list[user]['user_type']:
			info_change = 1
	if entity!='':
		log += ' entity='+entity
		cmd+='entity'+e
		if entity!=var.user_info_list[user]['user_entity']:
			info_change = 1
	cmd+= v+d+d+user+v
	print log
	telnet_cmd( cmd )

	# 先讀到 running 頁面，以確保接下來顯示的是結果
	res = tn.read_until('running', timeout=1)
	res = tn.read_until(page_end, timeout=0.01)
	# 接下來讀取結果頁面
	res = tn.read_until('Directory Number', timeout=1)
	if len(res.split('Directory Number'))>1:
		res = tn.read_until(page_end, timeout=0.01)

	# 檢查有沒有錯誤
	error = response_identify( res, user )
	if error:
		print '\n\t[-] '+user+' '+error
		return error

	# 將設定內容輸入到使用者
	cmd = ''
	if address!='':
		address = address.split('-')
		cmd+=(b*3)+address[0]+d+(b*3)+address[1]+d+(b*3)+address[0]+d
	if user_type!='':
		cmd+=e+user_type+e+d
	if entity!='':
		cmd+=(b*3)+entity

	# 輸入完成，執行
	cmd+=v
	telnet_cmd( cmd )
	# 偵測成功回應
	cmd = ''
	if info_change:
		# 先讀到 running 頁面，以確保接下來顯示的是結果
		res = tn.read_until('running', timeout=1)
		res = tn.read_until(page_end, timeout=0.01)
		# 接下來讀取結果頁面
		res = tn.read_until('succeeded', timeout=1)
		if len(res.split('succeeded'))>1:
			res = tn.read_until(page_end, timeout=0.01)

		# 檢查有沒有錯誤
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] modify '+user+' '+error
			# 回到指令頁面
			cmd = c*4
			telnet_cmd( cmd )
			tn.read_until('csa')
			return error
		cmd = v
		telnet_cmd( cmd )

	# 回到指令頁面
	cmd = c*3
	telnet_cmd( cmd )
	tn.read_until('csa')

# 讀取 分機號碼 設定資料
def read_user_settings( user ):# 引用全域變數
	print '\n\t[+] 讀取 '+user+' 分機資料'
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = ''
	cmd += var.gotousers+'consult'+e+d+e+'she'+(e*5)+v+d+d+user
	telnet_cmd( cmd )

	# 讀取到 Consult/Modify: Users 頁面
	res = tn.read_until('Consult/Modify: Users')
	# 再讀取到 Consult/Modify: Users 頁尾
	res = tn.read_until(page_end, timeout=0.01)

	# 執行搜尋分機的設定
	cmd = v
	telnet_cmd( cmd )

	# 先讀到 running 頁面，以確保接下來顯示的是結果
	res = tn.read_until('running', timeout=1)
	res = tn.read_until(page_end, timeout=0.01)
	# 接下來讀取結果頁面
	res = tn.read_until('Directory Number', timeout=1)
	if len(res.split('Directory Number'))>1:
		res = tn.read_until(page_end, timeout=0.01)

	# 檢查有沒有錯誤
	error = response_identify( res, user )
	if error:
		#print '\n\t[-] '+user+' '+error
		# 回到指令頁
		cmd = c*4
		telnet_cmd( cmd )
		# 偵測成功回應
		res = tn.read_until('csa')
		return error

	# 儲存分機設定參數
	var.user_info_list[user]['user'] = user
	var.user_info_list[user]['user_address'] = get_user_info(res,'address')
	var.user_info_list[user]['user_type'] = get_user_info(res,'type')
	var.user_info_list[user]['user_entity'] = get_user_info(res,'entity')

	# 回到指令頁
	cmd = c*4
	telnet_cmd( cmd )
	# 偵測成功回應
	res = tn.read_until('csa')

	return 0

def delete_user( user_for_delete ):
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'delete'+e+d
	telnet_cmd( cmd )
	for user in user_for_delete:
		cmd = b*8+user+v
		telnet_cmd( cmd )
		try:
			res = tn.read_until('succeeded', timeout=1)
		except:
			try:
				res = tn.read_until('no Such Object', timeout=1)
				print '\n\t[-] Delete '+user+' 分機號碼不存在'
			except:
				try:
					res = tn.read_until('Bad value', timeout=1)
					print '\n\t[-] Delete '+user+' Bad value'
				except:
					print '\n\t[-] Delete '+user+' timeout'
		cmd = v
		telnet_cmd( cmd )

'''
{'4101':
	{'user_address': '255-255-255',
	 'user': '4101',
	 'user_entity': '1',
	 'user_type': 'ANALOG',
	 'new_number' '4001'
	},
...}
'''
def profile_user( data='', key='' ):
	print '\n\t[+] porfile user '
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn

	cmd = var.goto_profile_create
	telnet_cmd( cmd )
	res = tn.read_until('Create: Profiled Users')
	error_user_list=[]
	for user in data:
		print '\n\n\n\n\t>>>>>>  複製分機 '+user+' 為分機 '+data[user]['new_number']+' <<<<<<'
		cmd = u*16+d+(b*8)+data[user]['new_number']
		if data=='':
			cmd+=d*8
			cmd+=(b*8)+user
		else:
			cmd += (d*3)
			if 'user_type' in data[user]:
				cmd += e+data[user]['user_type']+e
			cmd += d
			if 'user_entity' in data[user]:
				cmd += (b*8)+data[user]['user_entity']
			cmd += d
			if 'user_address' in data[user]:
				addr = data[user]['user_address'].split('-')
				cmd += (b*8)+addr[0]+d+(b*8)+addr[1]+d+(b*8)+addr[2]
			cmd += d
			cmd += (b*8)+user+d
			if data[user]['user_type']!='analog':
				cmd += (b*8)+user
		cmd += v
		telnet_cmd( cmd )
		# 先讀到 running 頁面，以確保接下來顯示的是結果
		res = tn.read_until('running', timeout=1)
		res = tn.read_until(page_end, timeout=0.01)
		# 接下來讀取結果頁面
		res = tn.read_until('succeeded', timeout=1)
		if len(res.split('succeeded'))>1:
			res = tn.read_until(page_end, timeout=0.01)

		# 檢查有沒有錯誤
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] 從 '+user+' profile 一個新分機 '+ data[user]['new_number'] + ' 時發生錯誤：' + error
			error_user_list.append(user)
		cmd = v
		telnet_cmd( cmd )

	# 將有產生錯誤的 user 踢掉
	for user in error_user_list:
		var.user_info_list.pop(user, None)

	cmd = c*3
	telnet_cmd( cmd )
	tn.read_until('csa')


def read_user_info():
	print '\n\tread user info :'
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
def response_identify(string='', expect=''):
	tn = var.tn
	error=0

	# 偵測成功訊息
	tmp = string.split(expect)
	if len(tmp)>1:
		return error

	# no Such Object Instance
	tmp = string.split('no Such Object Instance')
	if len(tmp)>1:
		error = '分機號碼錯誤'
		return error

	# already exists
	tmp = string.split('already exists')
	if len(tmp)>1:
		error = '分機號碼已經存在了'
		return error

	# Invalid translator number
	tmp = string.split('Invalid translator')
	if len(tmp)>1:
		error = '號碼規則錯誤'
		return error

	# Bad length
	tmp = string.split('Bad length')
	if len(tmp)>1:
		error = '輸入不完全'
		return error

	# Station Profil From
	tmp = string.split('Station Profil From')
	if len(tmp)>1:
		error = '參考分機輸入錯誤 Station Profile From 錯誤'
		return error

	# 未知錯誤
	print '\n\t[-] 發生未知的錯誤'
	#return '\n'*10+string+'\n'*10
	return '\n\tretrun 發生未知的錯誤'

	'''
	if not error:
		try:
			res = tn.read_until('Facilities', timeout=1)
			print res
		except:
			try:
				res = tn.read_until('Invalid', timeout=1)
				print '[-] Invalid'
			except EOFError as e:
				print '[-] timeout ERROR'
	'''
	return error
