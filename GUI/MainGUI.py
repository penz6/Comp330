# import
from tkinter import *


# new root window
root = Tk()

#Set title of window
root.title("Grade Analyzer")
#default dimensions
root.geometry('1000x500')

#create a top menu bar
menu = Menu(root)
item = Menu(menu)

#display the home text
homelabel = Label(root,text="Welcome to the PGUA^2 Grade Anaylzer ",anchor=CENTER,height=5,font=("Arial",18,"bold"))
#use pack to dynaimcally resize text
homelabel.pack()

#overall button
overallbutton = Button(root,text="See Overall Performance")
overallbutton.pack(anchor=S)
underperformingbutton = Button(root,text="See Underperforming Students")
underperformingbutton.pack(anchor=S)
#run tkinter
root.mainloop()