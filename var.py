#-*- coding: utf-8 -*-
#-*- coding: cp950 -*-
host = '191.254.1.2'
port = 23
timeout = 5
user = 'mtcl'
passwd = 'mtcl'
tn = ''
login_key = 'login:'
passwd_key = 'Password:'

menu_choice = 0
profile_user_num_1 = ''
profile_user_num_2 = ''
users_input_1 = ''
users_input_2 = ''

gotousers = 'mgr -l GEA\r\nuser\r\n'
goto_profile_create = 'mgr -l GEA\r\nprofile\r\ncreate\r\n'

user_info_list = []
# [ [user, address, type, entity], [user, address, type, entity], ... ]

e = '\r\n'
c = '\003'
v = '\026'
u = '\033OA'
d = '\033OB'
l = '\033OD'
r = '\033OC'
b = '\b'
page_end = 'qqj'

def modify_user( user, address='', user_type='', entity='' ):
	# 引用全域變數
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	cmd = var.gotousers+'consult'+e+d+e
	# 先將所有設定選項都準備好
	if address!='':
		cmd+='she'+(e*3)
	if user_type!='':
		cmd+='type'+e
	if entity!='':
		cmd+='entity'+e
	cmd+=v+(d*2)
	# 將設定內容輸入到使用者
	cmd+=user+v
	if address!='':
		address = address.split('-')
		cmd+=(b*3)+address[0]+d+(b*3)+address[1]+d+(b*3)+address[0]+d
	if user_type!='':
		cmd+=e+user_type+e+d
	if entity!='':
		cmd+=(b*3)+entity
	# 輸入完成，執行
	cmd+=v*2
	telnet_cmd( cmd, sleep=0.01 )
	# 回到初始畫面
	cmd = c*3
	telnet_cmd( cmd )

