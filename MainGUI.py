# import
import os
import tkinter as tk
import sv_ttk as sv
from pandastable import Table, TableModel, config
from tkinter import filedialog
from GoodAndBadList import Lists
import run_parser
#global vars
filepath = ""
options = config.load_options()
bigfont = ("Arial",18,"bold")
buttonfont = ("Arial",11)
#

#new class
class gradeGUI(tk.Tk):
    #init function for class gradegui
    def __init__(self,*args,**kwargs):
        #init for class
        tk.Tk.__init__(self,*args,**kwargs)
        #set theme
        sv.set_theme("dark")
        #table options
        options.update({
        'cellbackgr': '#2b2b2b',
        'textcolor': '#ffffff',
        'grid_color': '#444444',
        'rowselectedcolor': '#44475a',
        'font': 'TkDefaultFont',
        'fontsize': 10,
        'rowheight': 20,
        'colheadercolor': '#1e1e1e',
        'colheaderfg': '#ffffff',
        'fontsize': 14,
        })
        #new container
        container = tk.Frame(self)
        container.pack(side = 'top',fill = 'both',expand = True)
        #style
        style = tk.ttk.Style()
        style.configure("TButton", font=buttonfont,padding=(10, 20))
        #new empty frames
        self.frames = {}
        #get all of the page layouts
        for F in (HomePage,DashBoard,SectionAverage,BottomPerformers,TopPerformers):
            frame = F(container,self)
            self.frames[F] = frame
            #pack the frame
            frame.pack(fill="both", expand=True)

        #show the homepage
        self.show_frame(HomePage)
        #show the current frame
    def show_frame(self,cont):
        #hide non active frames
        for frame in self.frames.values():
            frame.pack_forget()
        #if need to load data
        if cont in (TopPerformers, BottomPerformers, SectionAverage):
            self.frames[cont].load_data()

        #now pack frame
        self.frames[cont].pack(fill="both", expand=True)
    #export files to excel
    def exportToHtml(self,df):
        folder_path = filedialog.askdirectory()
        if folder_path == "":
            #nothing
            print("Cancelled")
        else:
            df.to_html(open(os.path.join(folder_path,"gradeExport.html"), 'w'))

#homepage class
class HomePage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #homepage text
        homepagelabel = tk.Label(self,text = "Welcome to the PGUA^2 Grade Analyzer",font=bigfont,padx=20,pady=30)
        #apply grid
        homepagelabel.pack()
        #open file dialog
        openfilebutton = tk.ttk.Button(self,text="Select Your Run File",command=lambda:self.getFilePath(controller),style="TButton")
        openfilebutton.pack(padx=10, pady=10)
    #get the file path
    def getFilePath(self,controller):
        global filepath
        filepath = filedialog.askopenfilename()
        #throw error
        try:
            if filepath == "" or filepath.split(".")[1].lower() != "run":
                #raise error
                raise Exception("Incorrect file type")
            controller.show_frame(DashBoard)
        #catch
        except:
            tk.messagebox.showerror("Please choose a .run file to get started") 


#dashboard
class DashBoard(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #dashboard
        dashboardlabel= tk.Label(self,text="Here Is Your Dashboard", font=bigfont,padx=20,pady=30)
        dashboardlabel.pack()
        #buttons to go to different tabs
        lowestperformersbutton = tk.ttk.Button(self,text="See Work List",command=lambda:controller.show_frame(BottomPerformers),style="TButton")
        topperformersbutton = tk.ttk.Button(self,text="See Good List",command=lambda:controller.show_frame(TopPerformers),style="TButton")
        sectionaveragebutton = tk.ttk.Button(self,text="See Section Averages",command=lambda:controller.show_frame(SectionAverage),style="TButton")
        #pack the buttons
        lowestperformersbutton.pack(padx=10, pady=10)
        topperformersbutton.pack(padx=10, pady=10)
        sectionaveragebutton.pack(padx=10, pady=10)


#search students
class SectionAverage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X)
        #pack the home button
        homebutton = tk.ttk.Button(button_frame, text="Home", command=lambda: controller.show_frame(DashBoard))
        homebutton.pack(side=tk.LEFT)
        #export button
        # Initialize with sample data
        exportbutton = tk.ttk.Button(button_frame,text="Export", command=lambda: controller.exportToHtml(self.table))
        exportbutton.pack(side=tk.LEFT)
        #define the button list frame 
        self.button_list_frame = None
    def load_data(self):
        global filepath
        #button frame
        if self.button_list_frame:
            self.button_list_frame.destroy()
        
        self.button_list_frame = tk.Frame(self)
        self.button_list_frame.pack(pady=20)
        for i in run_parser.runReader(filepath):
            #add the button
            groupbutton = tk.ttk.Button(self.button_list_frame,text=os.path.basename(i),command=lambda: self.loadtable())
            groupbutton.pack(side=tk.LEFT)
    #load the table
    def loadtable(self,groupdf):
        #create the new table
        self.table = Table(self.table_frame, dataframe=groupdf, showtoolbar=False, showstatusbar=False, editable=False, config=options)
        config.apply_options(options, self.table)
        self.table.autoResizeColumns()
        self.table.setRowHeight(50)
        self.table.show() 
        

#top performers
class TopPerformers(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X)
        #pack the home button
        homebutton = tk.ttk.Button(button_frame, text="Home", command=lambda: controller.show_frame(DashBoard))
        homebutton.pack(side=tk.LEFT)
        #export button
        # Initialize with sample data
        exportbutton = tk.ttk.Button(button_frame, text="Export", command=lambda: controller.exportToHtml(self.df))
        exportbutton.pack(side=tk.LEFT)
        #display the data frame
        # create a container
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True)
        # Initialize table to None
        self.table = None

    def load_data(self):
        global filepath
        #get data
        if filepath:
            self.df = Lists.goodList(filepath)
        else:
            #if its empty
            self.df = TableModel.getSampleData()
        #remove old table
        if self.table:
            self.table.destroy()
        #create the new table
        self.table = Table(self.table_frame, dataframe=self.df, showtoolbar=False, showstatusbar=False, editable=False, config=options)
        config.apply_options(options, self.table)
        self.table.autoResizeColumns()
        self.table.setRowHeight(50)
        self.table.show() 


#bottom performers
class BottomPerformers(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X)
        #pack the home button
        homebutton = tk.ttk.Button(button_frame, text="Home", command=lambda: controller.show_frame(DashBoard))
        homebutton.pack(side=tk.LEFT)
        #export button
        exportbutton = tk.ttk.Button(button_frame, text="Export", command=lambda: controller.exportToHtml(self.df))
        exportbutton.pack(side=tk.LEFT)
        # create a container
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True)
        # Initialize table to None
        self.table = None

    def load_data(self):
        global filepath
        #get data
        if filepath:
            self.df = Lists.badList(filepath)
        else:
            #if its empty
            self.df = TableModel.getSampleData()
        #remove old table
        if self.table:
            self.table.destroy()
        #create the new table
        self.table = Table(self.table_frame, dataframe=self.df, showtoolbar=False, showstatusbar=False, editable=False, config=options)
        config.apply_options(options, self.table)
        self.table.autoResizeColumns()
        self.table.setRowHeight(50)
        self.table.show()


#run gui
gradeGUI().mainloop()



"""
# Suggestions

1. Organize code by separating GUI logic from data processing.
   - Move data loading and exporting functions into a separate module.
 
2. Avoid global variables where possible.
   - Store shared state (like the selected file path) as attributes of the main GUI class.

3. Reduce code duplication.
   - If multiple classes share similar methods (like load_data), create a base class or utility function.

4. Add docstrings to all classes and methods.
   - This helps everyone (and your future self) understand what each part does.

5. Use context managers for file operations.
   - Example: with open(filename, 'w') as f: ...

6. Follow Python naming conventions.
   - Class names: CamelCase (e.g., GradeGUI)
   - Method and variable names: snake_case (e.g., load_data)

Good work so far! Keep crushing it!

"""
