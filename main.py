#-*- coding: utf-8 -*-
#-*- coding: cp950 -*-
import var
import func


if __name__=="__main__":
	func.telnet_connect()
	if func.menu():
		print '完成'
	else:
		print '失敗'

