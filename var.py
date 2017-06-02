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

# [ [user, address, type, entity], [user, address, type, entity], ... ]
user_info_list = {}

e = '\r\n'
c = '\003'
v = '\026'
u = '\033OA'
d = '\033OB'
l = '\033OD'
r = '\033OC'
b = '\b'
page_end = 'qqj'


'''
# read_until('succeeded', timeout=0.1)
會讀取所有的回傳 telnet 字串，直到找到第一個 succeeded，或是過了 0.1 秒
所以如果沒有出現 succeeded 還是會讀取所有的回覆，而且讀取完之後，在 read_until 一次就讀取不到東西了，因為都已經被讀取完了。
對 try except 來說，read_until 的 timeout 到了不會算是 exception
'''