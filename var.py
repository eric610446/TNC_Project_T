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
�|Ū���Ҧ����^�� telnet �r��A������Ĥ@�� succeeded�A�άO�L�F 0.1 ��
�ҥH�p�G�S���X�{ succeeded �٬O�|Ū���Ҧ����^�СA�ӥBŪ��������A�b read_until �@���NŪ������F��F�A�]�����w�g�QŪ�����F�C
�� try except �ӻ��Aread_until �� timeout ��F���|��O exception
'''