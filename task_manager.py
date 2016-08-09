from Queue import Queue
import comms
import cPickle
import nav
import threading
import time

GRAPH_FILE = 'graph.txt'
G = cPickle.load(open(GRAPH_FILE))

BASE_VALUE = 0
READY_VALUE = 1
ERROR_VALUE = 2

task_queue = Queue()
car_queue = Queue()
car_task_locations = {}

class Car(threading.Thread):
	""" Object that maintains car information and queues. """
	def __init__(self, ser, device_id, navStatus="", state=(0, 4, 'E'), response_code=READY_VALUE):
		super(Car, self).__init__()
		self.ser = ser
		self.device_id = device_id
		self.navStatus = navStatus
		self.state = state 
		self.final_destination = None
		self.response_code = response_code
		self.instQ = Queue()
		car_queue.put(self)
		self.queued = True
		self.ready_to_exit = False

	def update_data(self, navStatus, response_code):
		""" Updates car info and adds car to Queue if necessary. """
		self.navStatus = navStatus
		self.response_code = response_code
		if self.can_be_queued():
			car_queue.put(self)
			self.queued = True

	def can_be_queued(self):
		return not self.queued and self.instQ.empty() and self.response_code == READY_VALUE

	def has_path_to_destination(self, goal_node):
		"""Returns a valid path if one exists.  Returns None otherwise."""
		dirs = nav.get_directions(G, self.state, goal_node)
		return dirs

	def add_task(self, path, goal_node):
		if self.final_destination:
			car_task_locations[self.final_destination] = False     
		self.final_destination = goal_node
		car_task_locations[goal_node] = True
		for di in path:
			self.instQ.put(di)
		self.queued = False
		self.wave_hello()

	def respond(self):
		""" Pops a command to the car if one is available and updates intended location data. """
		if self.response_code == READY_VALUE and not self.instQ.empty():
			inst = self.instQ.get()
			instruction_letter = inst[0]
			next_destination = inst[1]
			self.send_command(instruction_letter)
			if instruction_letter == 't':
				nav.reactivate_node(G, self.state)
			if next_destination == self.final_destination:
				nav.reactivate_node(G, self.final_destination)
			self.state = next_destination
			self.response_code = BASE_VALUE 

	def send_command(self, action):
		comms.write_to_device(self.ser, action)

	def read_data(self):
		return comms.read_from_device(self.ser)

	def wave_hello(self):
		self.send_command('h')

	def run(self):
		while not self.ready_to_exit:
			try:
				args = self.read_data()
				if len(args) >= 4:
					navStatus = args[0]
					usDistance = float(args[1])
					temp = float(args[2])
					response_code = int(args[3])
					self.update_data(navStatus, response_code)
			except Exception, e:
				pass

def car_update_loop(car_manager):
	""" Updates data and determines next action. """
	while not car_manager.ready_to_exit:
		if not car_manager.paused:
			bad_tasks = []
			while not task_queue.empty() and not car_queue.empty():
				task = task_queue.get()
				goal_node = nav.translate_to_loc(task)
				if not car_task_locations.setdefault(goal_node, False):
					car = car_queue.get()  
					path = car.has_path_to_destination(goal_node)
					if path is None:
						car_queue.put(car)
						bad_tasks.append(task)
					else:
						print "queueing task %d onto car %s" % (task, car.device_id)
						car.add_task(path, goal_node)

			for bt in bad_tasks:
				task_queue.put(bt)
			bad_tasks[:] = []

			for car in car_manager.cars:
				car.respond()

def stop_and_readjust(car_manager):
	""" Suspends car movements and displays intended locations. """
	car_manager.paused = True
	for car in car_manager.cars:
		print("Car %s should be at position: %s" %(str(car.device_id), str(car.state)))
	raw_input("Press enter to continue.")
	car_manager.paused = False
	for car in car_manager.cars:
		car.wave_hello()

def handle_input(car_manager):
	""" Allows users to input program commands. """
	while not car_manager.ready_to_exit:
		user_input = raw_input("Enter a command or type 'h' for help: ")
		user_input = user_input.lower()
		if user_input.startswith('s'): # Stop and Readjust mode
			stop_and_readjust(car_manager)
		elif user_input.startswith('t'): # Input locations
			tasks = eval(raw_input("Input a list of integer locations (ex. [6, 2, 4]): "))
			if isinstance(tasks, list):
				for task in tasks:
					task_queue.put(task)
			else:
				print("Please format tasks correctly.")
		elif user_input.startswith('h'): # Help
			print "t - Input tasks"
			print "s - Enter stop-and-readjust mode"
			print "q - Quit the program"
		elif user_input.startswith('q'):
			car_manager.quit()
		time.sleep(0.4)

class CarManager():
	""" Discovers and maintains information on all cars. """
	def __init__(self):
		self.cars = []
		self.device_ports = []
		self.paused = False
		self.ready_to_exit = False
		self.discover_cars()

	def discover_cars(self):
		dev_id_count = 0
		devices = comms.bind_all_devices()
		for port, ser in devices:
			self.device_ports.append(port)
			if dev_id_count >= 2:
				car = Car(ser, dev_id_count, state=(0, 0, 'E'))
			else:
				car = Car(ser, dev_id_count)
			car.start()
			print("Connected to car %d" % dev_id_count)
			self.cars.append(car)
			dev_id_count += 1

	def quit(self):
		for car in self.cars:
			car.ready_to_exit = True
			car.ser.close()
		for dp in self.device_ports:
			comms.release_device(dp)
		self.ready_to_exit = True


def main():
	car_manager = CarManager()
	input_thread = threading.Thread(target = handle_input, args = (car_manager,))
	input_thread.start()
	car_update_loop(car_manager)

if __name__ == "__main__":
	main()
