import socket
import numpy as np
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import *
import pyqtgraph.opengl as gl
import sys
import re
import concurrent.futures
import ast
from ast import literal_eval

np.set_printoptions(threshold=sys.maxsize)

class Simulation(object):
    def __init__(self, type):
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setGeometry(480, 270, 800, 600)
        self.window.setWindowTitle("Simulation")
        self.window.setCameraPosition(distance=30, elevation=100)

        self.type = type

        self.points_list = []
        self.points_backup = []

        if self.type == "live":
            self.s = socket.socket()
            while True:
                host = input(str("Insert the host address of the server \n"))
                try:
                    port = 8080
                    self.s.connect((host, port))
                    print ("connected to " + host)
                    break
                except Exception:
                    print("Could not connect :(")
                    continue
            self.window.show()
            self.three_dim_grid()
            file = open("filename.nmspmm", "wb")
            filedata = self.s.recv(9999999)
            file.write(filedata)
            file.flush()
            file.close()
            file = open("filename.nmspmm", "rb")
            filename_list = str(file.read(10240)).split("b", -1)
            #print(filename_list)
            filename = filename_list[1]
            filename = filename.replace(":", "_")
            self.received_filename = "received_"+filename.replace(".", "_")
            self.full_filename = "full_"+filename.replace(".", "_")
            self.animation()
            
            

        elif self.type == "offline":
            self.window.show()
            self.three_dim_grid()
            self.load()

    def three_dim_grid(self):
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.window.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.window.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.window.addItem(gz)

    def recv_data(self):
        while True:
            received_flight_file = open(self.received_filename+".fsm", "wb")
            received_flight_data = self.s.recv(np.int64(10737418240))
            received_flight_file.write(received_flight_data)
            received_flight_file.flush()
            received_flight_file.close()

            received_flight_file = open(self.received_filename+".fsm", "r")
            content = received_flight_file.read(np.int64(10737418240))
            self.splitted = str(content).split()
            self.splitted = [float(index)for index in self.splitted]
            #print(splitted)
            self.new_points = [tuple(self.splitted[i:i+3]) for i in range(0, len(self.splitted), 3)]
            print("received")
            time.sleep(.1)
            #move on recv_data

    def save_all(self):
        while True:
            try:
                full_flight = open(f"{self.full_filename}data.fsm", "w")
                full_flight.write(str(self.points_list))
                full_flight.flush()
                full_flight.close()
                print("saved all")
            except Exception: print("did not save :(")
            time.sleep(.1)

    
    def update(self):
        indexcount = 0
        try:
            for _ in self.new_points:         
                if len(_) == 3: 
                    self.points_list.append(_)
                    continue
                else: _.pop(indexcount)
            try: 
                self.window.removeItem(self.drawpoints)
                print("deleted previous line")
            except Exception: "could not delete previous line :("
            #print(self.points_list)
            print(f"length new points: {len(self.new_points)}")
            print(f"total points: {len(self.points_list)}")
            self.points = np.array(self.points_list) #convert the points list to an array of tuples
            self.drawpoints = gl.GLLinePlotItem(pos=self.points, width=1, antialias=True) #make a variable to store drawing data(specify the points, set antialiasing)
            self.draw() #run the draw function
        except Exception: print("did not draw")
        
    def load(self):
        full_flight_filename = input(str("Write the filename of the saved simulation:\n"))
        try:        
            full_flight = open(full_flight_filename, "r")
        except Exception:
            print("could not find the file :(")
            self.load()
        flight_data = full_flight.read(np.int64(10737418240))
        self.points_list = list(ast.literal_eval(str(flight_data))) #convert the points list to an array of tuples
        print(self.points_list)
        self.points = np.array(self.points_list)
        self.drawpoints = gl.GLLinePlotItem(pos=self.points, width=1, antialias=True) #make a variable to store drawing data(specify the points, set antialiasing)
        self.window.addItem(self.drawpoints) #run the draw function
        self.start()


    def draw(self):
        self.window.addItem(self.drawpoints) #draw the item
        print("drawed line")      

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            if self.type == "live":
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    recv_thread = executor.submit(self.recv_data)
                    save_thread = executor.submit(self.save_all)
                    exec_thread = executor.submit(QtGui.QApplication.instance().exec_())
            elif self.type == "offline":
                QtGui.QApplication.instance().exec_()

def begin():
    menu = input(str("Choose what to do: \n [1]: Live Simulation \n [2]: Load Simulation\n"))
    if menu == "1": 
        if __name__ == "__main__":
            Simulation("live")
    elif menu == "2": Simulation("offline")
    else: begin()

begin()
