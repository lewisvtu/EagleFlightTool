from Tkinter import *
import utils
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg", warn=False)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import numpy as np
from flightplan_generator import create_flight_path
import copy
import storyB_V2
import os
from PIL import Image, ImageTk


class MainWindow(object):
    '''Main window object for aplication'''
    def __init__(self, master):
        self.fname = ""
        self.master = master
        #Set variable for the persisent data entries in the data_window
        self.data_store = []
        #Creates the initial, empty plot for the graph_window
        self.fig = plt.figure()
        self.fig.add_subplot(111, projection="3d")
        #Set up frames for buttons and image
        self.main_frame = Frame(self.master)
        self.img_frame = Frame(self.master)
        Button(self.main_frame, text="Quit >:(", command=self._quit).grid(row=0, column=0)
        Button(self.main_frame, text="Open Data Set", command=self.open_data).grid(row=0, column=1)
        Button(self.main_frame, text="Open Graph Viewer", command=self.open_graph).grid(row=0, column=2)
        #Load image to display
        photo = ImageTk.PhotoImage(Image.open(os.path.join("resource", "eagleLogo.PNG")))
        img = Label(self.img_frame, image=photo)
        img.image = photo
        img.pack()
        self.main_frame.pack(side=TOP)
        self.img_frame.pack(side=BOTTOM)

    def open_graph(self):
        '''Opens a new window for the graph drawing utils'''
        graph_window = Toplevel(self.master)
        self.graph_window = GraphWindow(graph_window, self.fig)

    def open_data(self):
        '''Opens a new window for the data entry table'''
        data_window = Toplevel(self.master)
        self.data_window = DataWindow(data_window, self.data_store)

    def _quit(self):
        self.master.quit()
        self.master.destroy()

class GraphWindow(object):
    '''Window for drawing graphs'''
    def __init__(self, master, fig):
        self.master = master
        self.frame = Frame(self.master)
        self.graph_f = Frame(self.master)
        self.toolbar =Frame(self.master)
        Button(self.toolbar, text="Close Window", command=self.close_window).grid(row=0, column=0)
        Button(self.frame, text="Draw Graph", command=self.draw_graph).grid(row=3, column=0)
        Button(self.frame, text="Story Board", command=self.gen_story_board).grid(row=3, column=1)
        Label(self.frame, text="Flight File Name: ").grid(row=2,column=0)
        Label(self.frame, text="Simulation Code: ").grid(row=1, column=0)
        #Simulation code entry box
        self.simname_e = Entry(master=self.frame, width=20)
        self.simname_e.grid(row=1, column=1)
        #Default to this sim code   \/\/\/
        self.simname_e.insert(0, "RefL0025N0376")
        self.fname_e = Entry(master=self.frame, width=20)
        self.fname_e.grid(row=2, column=1)
        self.toolbar.pack(side=TOP)
        self.frame.pack(side=LEFT)
        self.graph_f.pack(side=RIGHT)
        self.set_graph(fig, des=False)

    def close_window(self):
        self.master.destroy()

    def gen_story_board(self):
        #Find sim name, file name from entry boxes, then make folder to empty images into
        sim_ref = self.simname_e.get()
        fname = self.fname_e.get()
        fname_root = fname[:-3]
        save_dir = os.path.join(fname_root, "images")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        image_name_base = os.path.join(save_dir, "image_no_")
        storyB_V2.story_board(image_name_base, fname, sim_ref)


    def draw_graph(self):
        #Plots the mpl figure from the flight path file, and sets it to the graph canvas
        fname = self.fname_e.get()
        figure = utils.plot_from_file(fname)
        self.set_graph(figure)

    def set_graph(self, fig, des=True):
        self.canvas = FigureCanvasTkAgg(fig, self.graph_f)
        if des:
            self.canv_widget.destroy()
        self.canv_widget = self.canvas.get_tk_widget()
        self.canv_widget.pack(fill=BOTH, expand=1)
        ax = fig.gca()
        ax.mouse_init()


class DataWindow(object):
    '''Data input table window'''
    def __init__(self, master, data_store):
        self.master = master
        self.data_store = data_store
        self.data_entries = []
        self.frame = Frame(self.master)
        self.data_f = Frame(self.master)
        Button(self.frame, text="Close Window", command=self.close_window).grid(row=0, column=0)
        Button(self.frame, text="Save Data", command=self.read_entry_boxes).grid(row=0,column=1)
        Button(self.frame, text="New Gal", command=self.add_row).grid(row=0, column=2)
        Button(self.frame, text="Clear All", command=self.clear_entries).grid(row=0, column=3)
        Button(self.frame, text="Gen flight file", command=self.gen_flight_plan).grid(row=0, column=5)
        self.fname_e = Entry(self.frame, width=20)
        self.fname_e.grid(row=0, column=4)
        lab_names = ["galaxy", "st fr", "en fr", "st sf", "en sf", "trg x", "y", "z", "rot ax: nx", "ny", "nz", "rv", "av", "ro", "ao", "hv", "ho"]
        for index, name in enumerate(lab_names):
            Label(self.data_f, text=name, width=4).grid(column=index, row=1)
        self.frame.grid(row=0)
        self.data_f.grid(row=1)
        self.draw_entry_boxes()

    def clear_entries(self):
        self.data_store[:] = [] #' CHANGE'
        self.draw_entry_boxes()

    def add_row(self):
        '''TODO:
            *Add ability to remove rows / insert in to table'''
        #Save data in boxes now
        self.read_entry_boxes()
        #Add a new row to this data, and redraw boxes
        self.data_store.append([0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.])
        self.draw_entry_boxes()

    def gen_flight_plan(self):
        self.read_entry_boxes()
        fname = self.fname_e.get()
        inp_data = np.asarray(copy.deepcopy(self.data_store))
        plan_file = create_flight_path(inp_data, True, fname)


    def draw_entry_boxes(self):
        #Destroy all old widgets
        for entry_row in self.data_entries:
            for entry in entry_row:
                entry.destroy()
        #Remove all old widgets from list
        self.data_entries[:] = []
        for row_no, data_row in enumerate(self.data_store):
            lab = Label(self.data_f, text="Galaxy no: %2u"% row_no)
            lab.grid(row=row_no + 2, column = 0)
            entry_row = [lab]
            for col_no, data_piece in enumerate(data_row):
                entry = Entry(master=self.data_f, width=6)
                entry.grid(row=row_no + 2, column=col_no + 1)
                entry_row.append(entry)
                entry.insert(0, data_piece)
            self.data_entries.append(entry_row)

    def read_entry_boxes(self):
        #Store data from each entry box
        for row_no, row in enumerate(self.data_entries):
            for col_no, data_piece in enumerate(row[1:]): #row[0] is a label
                self.data_store[row_no][col_no] = float(data_piece.get())



    def close_window(self):
        self.master.destroy()


if __name__ == "__main__":
    rt = Tk()
    w = MainWindow(rt)
    rt.mainloop()