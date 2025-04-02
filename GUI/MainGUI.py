# import
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import sv_ttk as sv

#global vars
global filepath
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
        #new container
        container = tk.Frame(self)
        container.pack(side = 'top',fill = 'both',expand = True)
        #style
        style = tk.ttk.Style()
        style.configure("TButton", font=buttonfont,padding=(10, 20))
        #new empty frames
        self.frames = {}
        #new icon for home button
        self.homebuttonicon = tk.PhotoImage(file = r"GUI/home.png")
        #resize
        self.homebuttonicon = self.homebuttonicon.subsample(3,3)
        #get all of the page layouts
        for F in (HomePage,DashBoard,SearchStudents,BottomPerformers,TopPerformers):
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
        #now pack frame
        self.frames[cont].pack(fill="both", expand=True)

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
        filepath = askopenfilename()
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
        #demo graph
        self.graph = ImageTk.PhotoImage(Image.open("/home/penn/Documents/Compsci/Comp330/GUI/demograph.png"))
        graphlabel = tk.Label(self,image=self.graph)
        graphlabel.pack(fill="x")
        #buttons to go to different tabs
        lowestperformersbutton = tk.ttk.Button(self,text="See Lowester Performers",command=lambda:controller.show_frame(BottomPerformers),style="TButton")
        topperformersbutton = tk.ttk.Button(self,text="See Top Performers",command=lambda:controller.show_frame(TopPerformers),style="TButton")
        searchstudentsbutton = tk.ttk.Button(self,text="Search Students",command=lambda:controller.show_frame(SearchStudents),style="TButton")
        #pack the buttons
        lowestperformersbutton.pack(padx=10, pady=10)
        topperformersbutton.pack(padx=10, pady=10)
        searchstudentsbutton.pack(padx=10, pady=10)

#search students
class SearchStudents(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #pack the home button
        homebutton = tk.ttk.Button(self, image=controller.homebuttonicon, command=lambda: controller.show_frame(DashBoard))
        homebutton.pack(side=tk.TOP,anchor=tk.NW)
        #create the search bar
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_items)
        self.search_entry = tk.ttk.Entry(self, font=buttonfont,textvariable=self.search_var)
        self.search_entry.pack()

        # Create ColumnView
        self.column_view = tk.ttk.Treeview(self)

        # Populate ColumnView with items
        # Replace this with your own data population logic
        for i in range(10):
            self.column_view.insert('', 'end', text=f'Item {i}')
        self.column_view.pack()

    def filter_items(self, *args):
        search_query = self.search_var.get()


#top performers
class TopPerformers(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #pack the home button
        homebutton = tk.ttk.Button(self, image=controller.homebuttonicon, command=lambda: controller.show_frame(DashBoard))
        homebutton.pack(side=tk.TOP,anchor=tk.NW)
        self.graph = ImageTk.PhotoImage(Image.open("/home/penn/Documents/Compsci/Comp330/GUI/demograph.png"))
        graphlabel = tk.Label(self,image=self.graph)
        graphlabel.pack(fill="x")

#bottom performers
class BottomPerformers(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #pack the home button
        homebutton = tk.ttk.Button(self, image=controller.homebuttonicon, command=lambda: controller.show_frame(DashBoard))
        homebutton.pack(side=tk.TOP,anchor=tk.NW)
        #display the graph
        self.graph = ImageTk.PhotoImage(Image.open("/home/penn/Documents/Compsci/Comp330/GUI/demograph.png"))
        graphlabel = tk.Label(self,image=self.graph)
        graphlabel.pack(fill="x")


#run gui
gradeGUI().mainloop()
