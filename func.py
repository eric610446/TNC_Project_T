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
	print "1. �ק�������X"
	var.menu_choice = input("���: ")
	if var.menu_choice==1:
		if not change_user_num():
			return 0
	return 1

def change_user_num():
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# ���ϥΪ̿�J�������X
	get_users_input()
	user_num_1 = var.users_input_1
	user_num_2 = var.users_input_2
	# log
	print '[*] user_num_1 : ',user_num_1
	print '[*] user_num_2 : ',user_num_2

	# �N profile data �C�� user1 ������ۤv�� user2 ���X
	i=0
	for user in user_num_1:
		var.user_info_list[user] = {}
		var.user_info_list[user]['new_number'] = user_num_2[i]
		i+=1

	# �w��C�@�Ӥ����h���o address, type, entity �T�Ӹ�ơA�ñN�� user �� address �]�� 255-255-255
	for user in var.user_info_list:
		print '-------------------------------------------------'

		# �\���������X�]�w
		error = read_user_settings( user )
		if error:
			# �p�G�b�o��Ū���]�w���ѤF�A�n�� user ��X�ק�������X���M��Avar.user_info_list
			var.user_info_list.pop(user, None)
			continue

		# �N�n�ק�������X���ϥΪ� port �אּ 255
		modify_user( user, address='255-255-255' )
	# �p�G�S��������@���������ơA�^�� 0
	if var.user_info_list=='':
		return 0

	# �����s����
	profile_data = var.user_info_list
	profile_user( profile_data )


	'''
	delete_user( user_for_delete )
	'''
	return 1

# ���o �������X ����J
def get_users_input():
	# ���ϥΪ̿�J�������X
	var.users_input_1 = raw_input("��Ӫ��������X�G")
	var.users_input_2 = raw_input("�ק�᪺�������X�G")
	# �ˬd��J���������X���S���Ӹؤj
	debug_num_list = str(var.users_input_1)+" "+str(var.users_input_2)
	if not check_num_format( 'users', debug_num_list ):
		print '[-] �������X��J���~'
		return 0
	var.users_input_1 = var.users_input_1.split(' ')
	var.users_input_2 = var.users_input_2.split(' ')

# �Ʀr���榡�ˬd�A�ѼƬ� "�ˬd�����X����" �P "���X�C��"
def check_num_format( num_type, debug_num_list ):
	if num_type == 'users':
		debug_num_list = debug_num_list.split(' ')
		for user in debug_num_list:
			if( int(user)>=100000000 or int(user)<=99 ):
				return 0
		return 1

def modify_user( user, address='', user_type='', entity='' ):
	print '[+] �]�w���� '+user
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'consult'+e+d+e

	# ���N�Ҧ��]�w�ﶵ���ǳƦn
	info_change = 0
	if address!='':
		cmd+='she'+(e*3)
		if address!=var.user_info_list[user]['user_address']:
			info_change = 1
	if user_type!='':
		cmd+='type'+e
		if user_type!=var.user_info_list[user]['user_type']:
			info_change = 1
	if entity!='':
		cmd+='entity'+e
		if entity!=var.user_info_list[user]['user_entity']:
			info_change = 1
	cmd+= v+d+d+user+v
	telnet_cmd( cmd )
	# Ū�� running ����
	res = var.tn.read_until('running')
	res = var.tn.read_until(page_end)
	# ���U��Ū�����G�����A�T�wŪ���@�㭶
	res = var.tn.read_until('Directory Number', timeout=0.1)
	res = var.tn.read_until(page_end)
	print res
	# �ˬd���S�����~
	error = response_identify( res, user )
	if error:
		print '[-] '+user+' '+error
		return error

	# �N�]�w���e��J��ϥΪ�
	cmd = ''
	if address!='':
		address = address.split('-')
		cmd+=(b*3)+address[0]+d+(b*3)+address[1]+d+(b*3)+address[0]+d
	if user_type!='':
		cmd+=e+user_type+e+d
	if entity!='':
		cmd+=(b*3)+entity

	# ��J�����A����
	cmd+=v
	telnet_cmd( cmd )
	cmd = ''
	# �������\�^��
	if info_change:
		# Ū�� running ����
		res = var.tn.read_until('running')
		res = var.tn.read_until(page_end)
		# ���U��Ū�����G�����A�T�wŪ���@�㭶
		res = var.tn.read_until('succeeded', timeout=0.1)
		res = var.tn.read_until(page_end)
		# �ˬd���S�����~
		error = response_identify( res, 'succeeded' )
		if error:
			print '[-] modify '+user+' '+error
			# �p�G�b�o��ק異�ѤF�A�n�� user ��X�ק�������X���M��Avar.user_info_list
			var.user_info_list.pop(user, None)
		cmd = v
		telnet_cmd( cmd )

	# �^����O����
	cmd = c*3
	telnet_cmd( cmd )
	tn.read_until('csa')

# Ū�� �������X �]�w���
def read_user_settings( user ):# �ޥΥ����ܼ�
	print '[*] Ū�� '+user+' �������'
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	cmd = ''
	cmd += var.gotousers+'consult'+e+d+e+'she'+(e*5)+v+d+d+user
	telnet_cmd( cmd )

	# Ū���� Consult/Modify: Users ����
	res = var.tn.read_until('Consult/Modify: Users')
	# �AŪ���� Consult/Modify: Users ����
	res = var.tn.read_until(page_end)

	# ����j�M�������]�w
	cmd = v
	telnet_cmd( cmd )
	# Ū�� running ����
	res = var.tn.read_until('running')
	res = var.tn.read_until(page_end)
	# ���U��Ū�����G�����A�T�wŪ���@�㭶
	res = var.tn.read_until('Directory Number', timeout=0.1)
	res = var.tn.read_until(page_end)
	# �ˬd���S�����~
	error = response_identify( res, user )
	if error:
		print '[-] '+user+' '+error
		return error

	print '[+] Ū�� '+user+' �����'

	# �x�s�����]�w�Ѽ�
	var.user_info_list[user]['user'] = user
	var.user_info_list[user]['user_address'] = get_user_info(res,'address')
	var.user_info_list[user]['user_type'] = get_user_info(res,'type')
	var.user_info_list[user]['user_entity'] = get_user_info(res,'entity')

	print '[+] �x�s '+user+' ��Ƨ���'

	# �^����O��
	cmd = c*4
	telnet_cmd( cmd )
	# �������\�^��
	res = var.tn.read_until('csa')
	error = response_identify( res, 'csa' )
	if error:
		print '[-] '+user+' '+error
		return error

	return 0

def delete_user( user_for_delete ):
	# �ޥΥ����ܼ�
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
				print '[-] Delete '+user+' �������X���s�b'
			except:
				try:
					res = var.tn.read_until('Bad value', timeout=1)
					print '[-] Delete '+user+' Bad value'
				except:
					print '[-] Delete '+user+' timeout'
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
	print '[+] porfile user '
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn

	cmd = var.goto_profile_create
	telnet_cmd( cmd )
	res = var.tn.read_until('Create: Profiled Users')
	for user in data:
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
		# �������\�^��
		res = tn.read_until('succeeded', timeout=0.1)
		response_identify( res, 'succeeded' )

		cmd = v
		telnet_cmd( cmd )
	cmd = c*3
	telnet_cmd( cmd )
	var.tn.read_until('csa')
'''
def setting_users_ports( user_port_list, tn ):
	# �ޥΥ����ܼ�
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
				print '[-] '+user[0]+' �]�w address '+user[1]+' : Invalid physical address'
			except EOFError as e:
				print '[-] '+user[0]+' �]�w address '+user[1]+' timeout ERROR'
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

# �Ĥ@���q�A�`�J�쪺���~�T������
def response_identify(string='', expect=''):
	tn = var.tn
	error=0

	# �������\�T��
	tmp = string.split(expect)
	if len(tmp)>1:
		return error

	# no Such Object Instance
	tmp = string.split('no Such Object Instance')
	if len(tmp)>1:
		error = '�������X���~'
		return error

	# already exists
	tmp = string.split('already exists')
	if len(tmp)>1:
		error = '�������X���~'
		return error

	# �������~
	print '[-] �o�ͥ��������~'
	#return '\n'*10+string+'\n'*10
	return ' retrun �o�ͥ��������~'

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
