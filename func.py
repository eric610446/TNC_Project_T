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

def telnet_cmd(cmd,tn=''):
	if tn=='':
		tn = var.tn
	tn.write("mgr\r\nuser\r\n")
	tn.write("\033OQ")
	tn.write("\033OQ")
	tn.write("config 0\r\n")

	#tn.write("config 1\r\n")
	print tn.read_until('csa')
	#tn.write("\n")
	#print tn.read_until('qqqj')
	var.tn = tn

def test(tn):
	telnet_cmd("mgr",tn)
	#print tn.read_until('qqj')
	'''
	telnet_cmd("cre\n")
	telnet_cmd("\x16\x16")
	print tn.read_until('Bad length')
	'''
	#print tn.read_until('mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj')
	#telnet_cmd("mgr\n")