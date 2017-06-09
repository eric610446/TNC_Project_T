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
	print "\n\t1. �ק�������X"
	print "\n\t2. �R���������X"
	print "\n\t0. ����"
	var.menu_choice = input("\n\t���: ")
	if var.menu_choice==0:
		return 'exit'
	if var.menu_choice==1:
		if change_user_num():
			return 1
	if var.menu_choice==2:
		if delete_users():
			return 1
	return 0

def change_user_num():
	os.system('cls')
	print '\n\n\t\t[ �ק�������X ]\n\t'+'-'*80
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# ���ϥΪ̿�J�������X
	get_users_input('change_user_num')
	user_num_1 = var.users_input_1
	user_num_2 = var.users_input_2
	# log
	#print '\n\t[*] user_num_1 : ',user_num_1
	#print '\n\t[*] user_num_2 : ',user_num_2

	# �N profile data �C�� user1 ������ۤv�� user2 ���X
	i=0
	for user in user_num_1:
		var.user_info_list[user] = {}
		var.user_info_list[user]['new_number'] = user_num_2[i]
		i+=1

	# �w��C�@�Ӥ����h���o address, type, entity �T�Ӹ�ơA�ñN�� user �� address �]�� 255-255-255
	for user in var.user_info_list:
		print '\n\n\n\n\t>>>>>>  Ū������ '+user+' �]�w�õn�X  <<<<<<'

		# �\���������X�]�w
		error = read_user_settings( user )
		if error:
			# �p�G�b�o��Ū���]�w���ѤF�A�n�� user ��X�ק�������X���M��Avar.user_info_list
			print '\n\t[-] �bŪ������ '+user+' ���]�w�ɵo�Ϳ��~ : '+error
			var.error_user_list.append(user)
			continue

		# �N�n�ק�������X���ϥΪ� port �אּ 255
		error = modify_user( user, address='255-255-255' )
		if error:
			# �p�G�b�o��Ū���]�w���ѤF�A�n�� user ��X�ק�������X���M��Avar.user_info_list
			print '\n\t[-] �b logout ���� '+user+' �ɵo�Ϳ��~ : '+error
			var.error_user_list.append(user)
			continue
	# �N�����Ϳ��~�� user ��
	for user in var.error_user_list:
		var.user_info_list.pop(user, None)

	# �p�G�S��������@���������ơA�^�� 0
	if not bool(var.user_info_list):
		return 0

	# �����s����
	profile_data = var.user_info_list
	profile_user( profile_data )
	# �N�����Ϳ��~�� user ��
	for user in var.error_user_list:
		var.user_info_list.pop(user, None)

	user_for_delete = var.user_info_list
	delete_user( user_for_delete )

	return 0

# ���o �������X ����J
def get_users_input( function ):
	if function=='change_user_num':
		# ���ϥΪ̿�J�������X
		var.users_input_1 = raw_input("\n\t��Ӫ��������X�G")
		var.users_input_2 = raw_input("\n\t�ק�᪺�������X�G")
		# �ˬd��J���������X���S���Ӹؤj
		debug_num_list = str(var.users_input_1)+" "+str(var.users_input_2)
	elif function=='delete_users':
		# ���ϥΪ̿�J�������X
		var.users_input_1 = raw_input("\n\t�n�R�����������X�G")
		# �ˬd��J���������X���S���Ӹؤj
		debug_num_list = str(var.users_input_1)

	if not check_num_format( 'users', debug_num_list ):
		print '\n\t[-] �������X��J���~'
		return 0

	if function=='change_user_num':
		var.users_input_1 = var.users_input_1.split(' ')
		var.users_input_2 = var.users_input_2.split(' ')
	elif function=='delete_users':
		var.users_input_1 = var.users_input_1.split(' ')

# �Ʀr���榡�ˬd�A�ѼƬ� "�ˬd�����X����" �P "���X�C��"
def check_num_format( num_type, debug_num_list ):
	if num_type == 'users':
		debug_num_list = debug_num_list.split(' ')
		for user in debug_num_list:
			if( int(user)>=100000000 or int(user)<=99 ):
				return 0
		return 1

def modify_user( user, address='', user_type='', entity='' ):
	log = '\n\t[+] �]�w���� '+user
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'consult'+e+d+e

	# ���N�Ҧ��]�w�ﶵ���ǳƦn
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

	# ��Ū�� running �����A�H�T�O���U����ܪ��O���G
	res = tn.read_until('running', timeout=3)
	res = tn.read_until(page_end, timeout=0.01)
	# ���U��Ū�����G����
	res = tn.read_until('Directory Number', timeout=3)
	if len(res.split('Directory Number'))>1:
		res = tn.read_until(page_end, timeout=0.01)

	# �ˬd���S�����~
	error = response_identify( res, user )
	if error:
		print '\n\t[-] '+user+' '+error
		return error

	# �N�]�w���e��J��ϥΪ�
	cmd = ''
	if address!='':
		address = address.split('-')
		cmd+=(b*3)+address[0]+d+(b*3)+address[1]+d+(b*3)+address[0]+d
	if user_type!='':
		cmd+=e+user_type+e+d
	if entity!='':
		cmd+=(b*3)+entity+d

	# ��J�����A����
	cmd+=v
	telnet_cmd( cmd )
	# �������\�^��
	cmd = ''
	if info_change:
		# ��Ū�� running �����A�H�T�O���U����ܪ��O���G
		res = tn.read_until('running', timeout=3)
		res = tn.read_until(page_end, timeout=0.01)
		# ���U��Ū�����G����
		res = tn.read_until('succeeded', timeout=3)

		# �ˬd���S�����~
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] modify '+user+' '+error
			# �^����O����
			cmd = c*4
			telnet_cmd( cmd )
			tn.read_until('csa')
			return error
		cmd = v
		telnet_cmd( cmd )

	# �^����O����
	cmd = c*3
	telnet_cmd( cmd )
	tn.read_until('csa')

# Ū�� �������X �]�w���
def read_user_settings( user ):# �ޥΥ����ܼ�
	print '\n\t[+] Ū�� '+user+' �������'
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = ''
	cmd += var.gotousers+'consult'+e+d+e+'she'+(e*5)+v+d+d+user
	telnet_cmd( cmd )

	# Ū���� Consult/Modify: Users ����
	res = tn.read_until('All instances')
	# �AŪ���� Consult/Modify: Users ����
	res = tn.read_until(page_end, timeout=0.01)

	# ����j�M�������]�w
	cmd = v
	telnet_cmd( cmd )

	# ��Ū�� running �����A�H�T�O���U����ܪ��O���G
	res = tn.read_until('running', timeout=3)
	res = tn.read_until(page_end, timeout=0.01)
	# ���U��Ū�����G����
	res = tn.read_until('Directory Number', timeout=3)
	if len(res.split('Directory Number'))>1:
		res = tn.read_until(page_end, timeout=0.01)

	# �ˬd���S�����~
	error = response_identify( res, user )
	if error:
		#print '\n\t[-] '+user+' '+error
		# �^����O��
		cmd = c*4
		telnet_cmd( cmd )
		# �������\�^��
		res = tn.read_until('csa')
		return error

	# �x�s�����]�w�Ѽ�
	var.user_info_list[user]['user'] = user
	var.user_info_list[user]['user_address'] = get_user_info(res,'address')
	var.user_info_list[user]['user_type'] = get_user_info(res,'type')
	var.user_info_list[user]['user_entity'] = get_user_info(res,'entity')

	# �^����O��
	cmd = c*4
	telnet_cmd( cmd )
	# �������\�^��
	res = tn.read_until('csa')

	return 0

def delete_user( user_for_delete, msg_timeout=3 ):
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn
	cmd = var.gotousers+'delete'+e+d
	telnet_cmd( cmd )
	for user in user_for_delete:
		print '\n\n\n\n\t>>>>>>  �R������ '+user+'  <<<<<<'
		cmd = b*8+user+v
		telnet_cmd( cmd )
		# ��Ū�� running �����A�H�T�O���U����ܪ��O���G
		res = tn.read_until('running', timeout=msg_timeout)
		res = tn.read_until(page_end, timeout=0.01)
		# ���U��Ū�����G����
		res = tn.read_until('succeeded', timeout=msg_timeout)
		# �ˬd���S�����~
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] �R������ '+user+' �ɵo�Ϳ��~�G' + error
			var.error_user_list.append(user)
		cmd = v
		telnet_cmd( cmd )

def delete_users():
	os.system('cls')
	print '\n\n\t\t[ �R���������X ]\n\t'+'-'*80
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end
	# ���ϥΪ̿�J�������X
	get_users_input('delete_users')
	user_num_1 = var.users_input_1
	delete_user(user_num_1, 3)

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
	# �ޥΥ����ܼ�
	e, c, v, u, d, l, r, b, page_end, tn = var.e, var.c, var.v, var.u, var.d, var.l, var.r, var.b, var.page_end, var.tn

	cmd = var.goto_profile_create
	telnet_cmd( cmd )
	res = tn.read_until('Create: Profiled Users')
	for user in data:
		print '\n\n\n\n\t>>>>>>  �ƻs���� '+user+' ������ '+data[user]['new_number']+' <<<<<<'
		cmd = u*16+d+(b*8)+data[user]['new_number']
		if data=='':
			cmd+=d*8
			cmd+=(b*8)+user
		else:
			cmd += (d*3)
			if 'user_type' in data[user]:
				cmd += e+data[user]['user_type']+e
				print '\n\t[+] �]�w���� type �� '+data[user]['user_type']
			cmd += d
			if 'user_entity' in data[user]:
				cmd += (b*8)+data[user]['user_entity']
				print '\n\t[+] �]�w���� entiy �� '+data[user]['user_entity']
			cmd += d
			if 'user_address' in data[user]:
				addr = data[user]['user_address'].split('-')
				cmd += (b*8)+addr[0]+d+(b*8)+addr[1]+d+(b*8)+addr[2]
				print '\n\t[+] �]�w���� address �� '+data[user]['user_address']
			cmd += d
			cmd += (b*8)+user+d
			if data[user]['user_type']!='analog':
				cmd += (b*8)+user
		cmd += v
		telnet_cmd( cmd )
		# ��Ū�� running �����A�H�T�O���U����ܪ��O���G
		res = tn.read_until('running', timeout=3)
		res = tn.read_until(page_end, timeout=0.01)
		# ���U��Ū�����G����
		res = tn.read_until('succeeded', timeout=3)
		# �ˬd���S�����~
		error = response_identify( res, 'succeeded' )
		if error:
			print '\n\t[-] �q '+user+' profile �@�ӷs���� '+ data[user]['new_number'] + ' �ɵo�Ϳ��~�G' + error
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
		error = '�������X�w�g�s�b�F'
		return error

	# Invalid translator number
	tmp = string.split('Invalid translator')
	if len(tmp)>1:
		error = '���X�W�h���~'
		return error

	# Bad length
	tmp = string.split('Bad length')
	if len(tmp)>1:
		error = '��J������'
		return error

	# Station Profil From
	tmp = string.split('Station Profil From')
	if len(tmp)>1:
		error = '�ѦҤ�����J���~ Station Profile From ���~'
		return error

	# Software Protection
	tmp = string.split('Software Protection')
	if len(tmp)>1:
		tmp = tmp[0].split('ATTRIBUTE 0:')
		error = '�b����ʧ@�ɵo�ͳn����v���������D�G'+tmp[1]

	# �������~
	print '\n\t[-] �o�ͥ��������~'
	#return '\n'*10+string+'\n'*10
	return '\n\tretrun �o�ͥ��������~'

	return error
