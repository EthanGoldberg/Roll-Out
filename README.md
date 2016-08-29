# Roll-Out
## Information
Based on the project I implemented as an intern at the Accenture Tech Labs in San Jose.  For more information, please read my post [here](https://medium.com/@emgoldberg1/autobots-roll-iot-80a77c099a20).

####Project Concept: 
A user picks a set of locations to visit, and a fleet of cars dispatch to every location in that set.

####Basic Required Utilities:
* ELEGO Robot Cars (Arduino-based)
* Linux gateway
* Poster board
* Wide black tape (should be at least 2” width)

####Included Files:
* **pilot.ino** – The very bottom of the stack.  Controls Arduino I/O to define basic movements and sensor functions.  Utilizes these basic actions to establish consistent discrete steps.
* **mapmaker.py** – Creates the graph to be used for pathfinding.  Translates input task locations to their corresponding states.
* **comms.py** – Handles programmatic communication and the setup of serial connections with devices.
* **nav.py** – Finds the shortest path between two states and provides the discrete instructions required to take it.  Also provides tools to manage collision prevention.
* **task_manager.py** – The control center.  Keeps track of all cars, determines necessary actions, and sends the commands to carry them out.

## Instructions
1.	Download pybluez using ```sudo apt-get install pybluez```.
2.	Pair the cars to Bluetooth.  (In Ubuntu, this step can be carried out in the ```Settings>Bluetooth``` menu.)
3.	Run the file ```mapmaker.py``` if using the original layout.  Otherwise, this file should be customized to match the state space graph for your own layout.  The graph file should ultimately be pickled into the file ```graph.txt```.
4.	Place the first two cars on the bottom left corner of the map and any others in the top left corner (or change the initial locations in ```task_manager.py```).
5.	Run ```task_manager.py```.
6.	Using the command line interface, input a list of tasks.  The cars will dispatch automatically.
