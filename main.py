#-*- coding: utf-8 -*-
#-*- coding: cp950 -*-
import var
import func
import os


if __name__=="__main__":
	while True:
		func.telnet_connect()
		r = func.menu()
		if r == 'exit':
			break
		elif r:
			print '\n'
		else:
			print '\n'
		var.tn.close()
		os.system('pause')
		os.system('cls')
