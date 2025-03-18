# import
import tkinter as tk

#new class
class gradeGUI(tk.Tk):
    #init function for class gradegui
    def __init__(self,*args,**kwargs):
        #init for class
        tk.Tk.__init__(self,*args,**kwargs)
        #new container
        container = tk.Frame(self)
        container.pack(side = 'top',fill = 'both',expand = True)
        #new empty frames
        self.frames = {}

        #get all of the page layouts
        for F in (HomePage,):
            frame = F(container,self)
            self.frames[F] = frame
            #pack the frame
            frame.pack(fill="both", expand=True)

        #show the homepage
        self.show_frame(HomePage)
        #show the current frame
    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()

#homepage class
class HomePage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        #homepage text
        homepagelabel = tk.Label(self,text = "Welcome to the PGUA^2 Grade Analyzer",font=("Arial",18,"bold"),padx=20,pady=30)
        #apply grid
        homepagelabel.pack()
        

#run gui
gradeGUI().mainloop()