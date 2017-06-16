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

gotousers = 'mgr -l GEA\r\nuser\r\n'
goto_profile_create = 'mgr -l GEA\r\nprofile\r\ncreate\r\n'

e = '\r\n'
c = '\003'
v = '\026'
u = '\033OA'
d = '\033OB'
l = '\033OD'
r = '\033OC'
b = '\b'
page_end = 'qqj'


# ------------------------------------------------------------------
# 選單的選擇
menu_choice = 0
# 要執行 profile 動作的原分機號碼群
profile_user_num_1 = ''
# 要執行 profile 動作的新分機號碼群
profile_user_num_2 = ''
# 使用者輸入 1
users_input_1 = ''
# 使用者輸入 2
users_input_2 = ''
# 分開' '後的分機號碼
splited_num = ''
# [ [user, address, type, entity], [user, address, type, entity], ... ]
# 用於計算
user_info_list = {}
# 用於儲存現在分機的值
user_info_list_now = {}
# 發生錯誤的分機
error_user_list = []


def initial_var():
	global menu_choice, profile_user_num_1, profile_user_num_2
	global users_input_1, users_input_2, splited_num
	global user_info_list, user_info_list_now, error_user_list

	menu_choice = 0
	profile_user_num_1 = ''
	profile_user_num_2 = ''
	users_input_1 = ''
	users_input_2 = ''
	user_info_list = {}
	user_info_list_now = {}
	error_user_list = []
	splited_num = ''
# ------------------------------------------------------------------