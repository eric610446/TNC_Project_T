#-*- coding: utf-8 -*-
#-*- coding: cp950 -*-
import var
import telnetlib
import time
import copy
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
	print "\n\t2. 刪除分機號碼"
	print "\n\t0. 結束"
	var.menu_choice = input("\n\t選擇: ")
	if var.menu_choice==0:
		return 'exit'
	if var.menu_choice==1:
		var.initial_var()
		if change_user_num():
			return 1
	if var.menu_choice==2:
		var.initial_var()
		if delete_users():
			return 1
	return 0

def change_user_num():
	os.system('cls')
	print '\n\n\t\t[ 修改分機號碼 ]\n\t'+'-'*80
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# 讓使用者輸入分機號碼
	if not get_users_input('change_user_num'):
		print '\n\t[-] 取得使用者輸入錯誤'
		return '取得使用者輸入錯誤'
	user_num_1 = var.users_input_1
	user_num_2 = var.users_input_2
	# 將 profile data 每個 user1 對應到自己的 user2 號碼
	i=0
	for user in user_num_1:
		var.user_info_list[user] = {}
		var.user_info_list[user]['new_number'] = user_num_2[i]
		i+=1

	# 針對每一個分機去取得 address, type, entity 三個資料
	for user in var.user_info_list:
		print '\n\n\n\n\t>>>>>>  讀取分機 '+user+' 設定  <<<<<<'
		# 閱覽分機號碼設定
		error = read_user_settings( user )
		if error:
			# 如果在這邊讀取設定失敗了，要把 user 踢出修改分機號碼的清單，var.user_info_list
			print '\n\t[-] 在讀取分機 '+user+' 的設定時發生錯誤 : '+error
			var.error_user_list.append(user)
			continue

	# 將有產生錯誤的 user 踢掉
	for user in var.error_user_list:
		var.user_info_list_now.pop(user, None)
		var.user_info_list.pop(user, None)
	var.error_user_list=[]

	# 將原 user 的 address 設為 255-255-255
	for user in var.user_info_list:
		print '\n\n\n\n\t>>>>>>  登出分機 '+user+'  <<<<<<'
		# 將要修改分機號碼的使用者 port 改為 255
		error = modify_user( user, address='255-255-255' )
		if error:
			# 如果在這邊讀取設定失敗了，要把 user 踢出修改分機號碼的清單，var.user_info_list
			print '\n\t[-] 在 logout 分機 '+user+' 時發生錯誤 : '+error
			var.error_user_list.append(user)
			continue

	# 將有產生錯誤的 user 踢掉
	for user in var.error_user_list:
		var.user_info_list_now.pop(user, None)
		var.user_info_list.pop(user, None)
	var.error_user_list=[]

	# 如果沒有抓到任何一支分機的資料，回傳 0
	if not bool(var.user_info_list):
		return 0

	# 拷貝新分機
	profile_data = copy.deepcopy(var.user_info_list)
	profile_user( profile_data )

	print '\n\n\n\n\t>>>>>>  [+] 將在 profile user 發生錯誤的原來分機還原 address  <<<<<'
	for user in var.error_user_list:
		error = modify_user( user, var.user_info_list[user]['user_address'] )
		if error:
			# 如果在這邊讀取設定失敗了，要把 user 踢出修改分機號碼的清單，var.user_info_list
			print '\n\t[-] 在還原分機 '+user+' 的 address 時發生錯誤 : '+error
			var.user_info_list.pop(user, None)
			continue
		var.user_info_list.pop(user, None)

	user_for_delete = var.user_info_list
	delete_user( user_for_delete )

	return 0

# 取得 分機號碼 的輸入
def get_users_input( function ):
	if function=='change_user_num':
		# 讓使用者輸入分機號碼
		var.users_input_1 = raw_input("\n\t原來的分機號碼：")
		var.users_input_2 = raw_input("\n\t修改後的分機號碼：")
		# 將範圍數字改為單一數字
		var.users_input_1 = range_2_single(var.users_input_1)
		var.users_input_2 = range_2_single(var.users_input_2)
		if var.users_input_1==0 or var.users_input_2==0:
			return 0
		# 檢查分機號碼數量有沒有一樣，要加入 split，否則只會測量字串的字元數，在變更分機號碼長度時會發生錯誤
		if len(var.users_input_1.split(' '))!=len(var.users_input_2.split(' ')):
			print '\n\t[-] 輸入分機號碼數量不一致'
			return 0
		# 檢查輸入的分機號碼有沒有太誇大
		debug_num_list = str(var.users_input_1)+" "+str(var.users_input_2)
	elif function=='delete_users':
		# 讓使用者輸入分機號碼
		var.users_input_1 = raw_input("\n\t要刪除的分機號碼：")
		# 將範圍數字改為單一數字
		var.users_input_1 = range_2_single(var.users_input_1)
		if var.users_input_1==0:
			return 0
		# 檢查輸入的分機號碼有沒有太誇大
		debug_num_list = str(var.users_input_1)
	if check_num_format( 'users', debug_num_list ):
		print '\n\t[-] 分機號碼輸入錯誤'
		return 0

	if function=='change_user_num':
		var.users_input_1 = var.users_input_1.split(' ')
		var.users_input_2 = var.users_input_2.split(' ')
	elif function=='delete_users':
		var.users_input_1 = var.users_input_1.split(' ')

	return 1

# 將範圍數字改為單一數字 ( 100-110 105 120-130 )
# 發生錯誤回傳 0，正確回傳分解出單一數字的字串，以空格做分隔，如 100 101 102 ...
def range_2_single( input_num ):
	tmp = input_num.split(' ')
	result = ''
	for range_num in tmp:
		min_max = range_num.split('-')
		if len(min_max)==1:
			result += range_num+' '
			continue
		elif len(min_max)!=2:
			print '\n\t[-] 數字範圍格式輸入錯誤 如: 100-110-'
			return 0
		if min_max[0]>min_max[1]:
			print '\n\t[-] 數字範圍格式輸入錯誤 小-大 如: 100-110'
			return 0
		for num in range(int(min_max[0]), int(min_max[1])+1):
			result += str(num)+' '
	result = result[0:-1]
	return result

# 數字的格式檢查，參數為 "檢查的號碼類型" 與 "號碼列表"
def check_num_format( num_type, debug_num_list ):
	if num_type == 'users':
		debug_num_list = debug_num_list.split(' ')
		for user in debug_num_list:
			if int(user)>=100000000 or int(user)<=99:
				return 1
		return 0

def modify_user( user, address='', user_type='', entity='' ):
	log = '\n\t[+] 設定分機 '+user
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'consult'+e+d+e

	# 先將所有設定選項都準備好
	info_change = 0
	# 如果參數有輸入，而且要修改的內容與現在的設定有不同，則把紀錄有產生變化的變數設定為 1
	if address!='' and address!=var.user_info_list_now[user]['user_address']:
		log += ' address='+address
		info_change = 1
		cmd+='she'+(e*3)
	if user_type!='' and user_type!=var.user_info_list_now[user]['user_type']:
		log += ' user_type='+user_type
		info_change = 1
		cmd+='type'+e
	if entity!='' and entity!=var.user_info_list_now[user]['user_entity']:
		log += ' entity='+entity
		info_change = 1
		cmd+='entity'+e
	# 如果有需要設定的內容，則就可以輸入 user 並進入設定頁面
	if info_change:
		print log
		cmd+=v+d+d+user+v
		telnet_cmd( cmd )
		# 先讀到 running 頁面，以確保接下來顯示的是結果
		res = tn.read_until('running', timeout=3)
		res = tn.read_until(page_end, timeout=0.01)
		# 接下來讀取結果頁面
		res = tn.read_until('Directory Number', timeout=3)
		if len(res.split('Directory Number'))>1:
			res = tn.read_until(page_end, timeout=0.01)
		# 檢查有沒有錯誤
		error = response_identify( res, user )
		if error:
			print '\n\t[-] '+user+' '+error
			return error
		# 將設定內容輸入到使用者
		cmd = ''
		if address!='' and address!=var.user_info_list_now[user]['user_address']:
			addr = address.split('-')
			cmd+=(b*3)+addr[0]+d+(b*3)+addr[1]+d+(b*3)+addr[2]+d
		if user_type!='' and user_type!=var.user_info_list_now[user]['user_type']:
			cmd+=e+user_type+e+d
		if entity!='' and entity!=var.user_info_list_now[user]['user_entity']:
			cmd+=(b*3)+entity+d
		# 輸入完成，執行
		cmd+=v
		telnet_cmd( cmd )
		# 偵測成功回應
		cmd = ''

		# 先讀到 running 頁面，以確保接下來顯示的是結果
		res = tn.read_until('running', timeout=3)
		res = tn.read_until(page_end, timeout=0.01)
		# 接下來讀取結果頁面
		res = tn.read_until('succeeded', timeout=3)
		# 檢查有沒有錯誤
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] modify '+user+' '+error
			# 回到指令頁面
			cmd = c*4
			telnet_cmd( cmd )
			tn.read_until('csa')
			return error
		else:
			if address!='' and address!=var.user_info_list_now[user]['user_address']:
				var.user_info_list_now[user]['user_address'] = address
			if user_type!='' and user_type!=var.user_info_list_now[user]['user_type']:
				var.user_info_list_now[user]['user_type'] = user_type
			if entity!='' and entity!=var.user_info_list_now[user]['user_entity']:
				var.user_info_list_now[user]['user_entity'] = entity
		cmd = v
		telnet_cmd( cmd )
	# 如果沒有要設定的內容，則需要按 ctrl+c 跳出選單
	else:
		cmd+=c
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
	res = tn.read_until('All instances')
	# 再讀取到 Consult/Modify: Users 頁尾
	res = tn.read_until(page_end, timeout=0.01)

	# 執行搜尋分機的設定
	cmd = v
	telnet_cmd( cmd )

	# 先讀到 running 頁面，以確保接下來顯示的是結果
	res = tn.read_until('running', timeout=3)
	res = tn.read_until(page_end, timeout=0.01)
	# 接下來讀取結果頁面
	res = tn.read_until('Directory Number', timeout=3)
	if len(res.split('Directory Number'))>1:
		res = tn.read_until(page_end, timeout=0.01)

	# 檢查有沒有錯誤
	error = response_identify( res, user )
	if error:
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

	# 使用 dictionary 完整 value 複製要使用 copy.deepcopy
	# dic1 = dic2 會互相引用 ( 參考 )
	# dic1 = dic2.copy() 會參考第一個元素，第二個才會是各自值複製
	var.user_info_list_now = copy.deepcopy(var.user_info_list)
	# 回到指令頁
	cmd = c*4
	telnet_cmd( cmd )
	# 偵測成功回應
	res = tn.read_until('csa')

	return 0

def delete_user( user_for_delete, msg_timeout=3 ):
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'delete'+e+d
	telnet_cmd( cmd )
	for user in user_for_delete:
		res = tn.read_until('Delete: Users')
		print '\n\n\n\n\t>>>>>>  刪除分機 '+user+'  <<<<<<'
		cmd = b*8+user+v
		telnet_cmd( cmd )
		# 先讀到 running 頁面，以確保接下來顯示的是結果
		res = tn.read_until('running', timeout=msg_timeout)
		res = tn.read_until(page_end, timeout=0.01)
		# 接下來讀取結果頁面
		res = tn.read_until('succeeded', timeout=msg_timeout)
		# 檢查有沒有錯誤
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] 刪除分機 '+user+' 時發生錯誤：' + error
			var.error_user_list.append(user)
		cmd = v
		telnet_cmd( cmd )

def delete_users():
	os.system('cls')
	print '\n\n\t\t[ 刪除分機號碼 ]\n\t'+'-'*80
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# 讓使用者輸入分機號碼
	get_users_input('delete_users')
	user_num_1 = var.users_input_1
	delete_user(user_num_1, 0.1)

	return 0

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
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn

	cmd = var.goto_profile_create
	telnet_cmd( cmd )
	res = tn.read_until('Create: Profiled Users')
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
				print '\n\t[+] 設定分機 type 為 '+data[user]['user_type']
			cmd += d
			if 'user_entity' in data[user]:
				cmd += (b*8)+data[user]['user_entity']
				print '\n\t[+] 設定分機 entiy 為 '+data[user]['user_entity']
			cmd += d
			if 'user_address' in data[user]:
				addr = data[user]['user_address'].split('-')
				cmd += (b*8)+addr[0]+d+(b*8)+addr[1]+d+(b*8)+addr[2]
				print '\n\t[+] 設定分機 address 為 '+data[user]['user_address']
			cmd += d
			cmd += (b*8)+user+d
			if data[user]['user_type']!='ANALOG':
				cmd += (b*8)+user
		cmd += v
		telnet_cmd( cmd )
		# 先讀到 running 頁面，以確保接下來顯示的是結果
		res = tn.read_until('running', timeout=3)
		res = tn.read_until(page_end, timeout=0.01)
		# 接下來讀取結果頁面
		res = tn.read_until('succeeded', timeout=3)
		# 檢查有沒有錯誤
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] 從 '+user+' profile 一個新分機 '+ data[user]['new_number'] + ' 時發生錯誤：' + error
			var.error_user_list.append(user)
		cmd = v
		telnet_cmd( cmd )

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
		return 0

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

	# Address already used
	tmp = string.split('Address already used')
	if len(tmp)>1:
		error = '分機 address 已經有被使用了'
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

	# Software Protection
	tmp = string.split('Software Protection')
	if len(tmp)>1:
		tmp = tmp[0].split('ATTRIBUTE 0:')
		error = '在執行動作時發生軟體授權不足的問題：'+tmp[1]

	# Lock
	tmp = string.split('Lock')
	if len(tmp)>1:
		tmp = tmp[0].split('OBJECT -1: ')
		error = '在執行動作時發生軟體授權不足的問題：'+tmp[1]

	# 未知錯誤
	print '\n\t[-] 發生未知的錯誤'
	#return '\n'*10+string+'\n'*10
	return '\n\tretrun 發生未知的錯誤'

	return error
