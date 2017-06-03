#-*- coding: utf-8 -*-
#-*- coding: cp950 -*-
import var
import func
import os


if __name__=="__main__":
	func.telnet_connect()
	while True:
		r = func.menu()
		if r == 'exit':
			break
		elif r:
			print '\n'
		else:
			print '\n'
		os.system('pause')
		os.system('cls')
