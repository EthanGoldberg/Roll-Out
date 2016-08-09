import threading 
import bluetooth
import subprocess
import time
import serial

def sh_taken_rfcomm_devices():
	ls = subprocess.Popen(['ls', '/dev'], stdout=subprocess.PIPE)
	grep = subprocess.Popen(["grep", "rfcomm*"], stdin=ls.stdout, stdout=subprocess.PIPE)
	ls.stdout.close()
	output = grep.communicate()[0]
	ls.wait()
	return output

def sh_get_all_paired_devices():
	try:
		output = subprocess.check_output(["bt-device", "-l"])
		output = output.replace("Added devices:", "")
		output = output.replace("(","")
		output = output.replace(")","")
		output = output.split()
		export = []
		for i in xrange(0, len(output), 2):
			export.append((output[i], output[i+1]))
		return export
	except Exception, e:
		return []

def sh_release_rfcomm_device(device):
	return subprocess.check_output([
		"rfcomm", 
		"release",
		"%d" % device
	])

def sh_bind_rfcomm_device(btdevice_mac, dev_num):
	return subprocess.check_output([
		"rfcomm",
		"bind",
		"%d" % dev_num,
		btdevice_mac,
		"1"
	])


def paired_devices():
	return sh_get_all_paired_devices()

def taken_rfcomm_devices():
	raw = sh_taken_rfcomm_devices()
	return raw.split()

def is_device_in_use(device):
	return ("rfcomm%d" % device) in taken_rfcomm_devices()

def is_device_free(device):
	return not is_device_in_use(device)

def release_device(device):
	return is_device_free(device) or sh_release_rfcomm_device(device) 

def bind_device(mac, device):
	if is_device_in_use(device):
		raise Exception("Device is already in use")
	else:
		return sh_bind_rfcomm_device(mac, device)

def bind_all_devices():
	""" Binds all paired devices to rfcomm ports and opens serial connections for each. """
	pd = paired_devices()
	ports = []
	port = 0
	num_paired = 0
	while num_paired < len(pd) and port < 32:
		if is_device_free(port):
			ports.append(port)
			num_paired += 1
		port += 1

	if num_paired != len(pd):
		raise Exception("Not enough open ports")	

	ser_connections = []
	for i in range(0, len(pd)):
		dev, mac = pd[i]
		p = ports[i]
		bind_device(mac, p)
		ser_connections.append((p, connect_to_serial(p)))			
	return ser_connections

def connect_to_serial(port):
	""" Opens serial connection to port. """
	comm_port = "/dev/rfcomm%d" % port
	ser = serial.Serial(comm_port, 9600, timeout=1)
	return ser

def write_to_device(ser, data):
	""" Writes data to serial. """
	if ser != None:
		ser.write(data)
	else:
		raise ValueError("Never established serial connection to device")

def read_from_device(ser):
	""" Reads data from serial.  Returns a list of values. """
	if ser != None:
		msg = ser.readline()
		return msg[:-2].split("_")
	else:
		raise ValueError("Never established serial connection to device")
