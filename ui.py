# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 23:37:27 2019

@author: jujujission
"""

from tkinter import *     
from tkinter import filedialog
from neural import *

root = Tk()
width = 800
height = 600
width_welcome = 500
height_welcome = 100
root.geometry(str(width)+'x'+str(height))    


input_name = StringVar()
output_name = StringVar()

analys_str = StringVar()
train_str = StringVar()
input_path = StringVar()

#Labels
analys_lbl = Label(root, textvariable = analys_str, font=(None,15))
train_lbl = Label(root, textvariable = train_str, font=(None,15), width = 400)



major = 0.0
major_out = 1.0

def identical():
    if major > 0.5 and major_out > 0.5:
        return True
    if major < 0.5 and major_out < 0.5:
        return True
    return False

def analyze():
#    print(input_name.get())
    temp = str(input_name.get())
    major, key, notes = analysis(temp)
    major = round_nearest(major,0.01) * 100
    time = notes *27/558
    time = int(time)
    train_str.set('')
    analys_str.set('Major chord rate: ' + str(major) + '%\n'  + 'Key: ' + key + '\nTraining Time Estimated: ' + str(time) + "mins")
    analys_lbl.place(x=width/3, y = height*3/4, width = 300, height = 100)
    
    
def generate():
    analys_str.set('')
    train_lbl.place(x=width/3, y = height*3/4, width = 300, height = 50)
    temp = str(input_name.get())
    while (identical() == False):
        train(temp,'')
        output = str(input_name.get()) + 's_output.mid'
        major_out, key, notes = analysis(temp)
        major_out = round_nearest(major_out,0.01) * 100
#    train_str.set('Major chord rate: ' + str(major) + '%\n'  + 'Key: ' + key')



train_btn = Button(root, text = 'Train and generate music', 
                command = generate)
analys_btn = Button(root, text = 'Analyze', command = analyze)


input_path.set("Your input path: ")
input_lbl = Label(root, textvariable = input_path)
input_lbl.place(x=300, y = height/10+height_welcome, width = 400, height = 25)
welcome_lbl = Label(root, text = "Welcome to music generator", font=(None,20),fg="green")

    
def loadFile():
    fname = filedialog.askopenfilename(filetypes=(("Midi files", "*.mid"),
                                           ("All files", "*.*")))
    input_path.set("Your input path: " + str(fname))
    input_name.set(str(fname))
    train_btn.place(x=450, y = height*3/5, width = 150, height = 25)
    analys_btn.place(x=150, y = height*3/5, width = 150, height =25)


    
 
btn = Button(root, text = 'Click to select a midi file!', 
                command = loadFile) 

# Set the position of button on the top of window 
welcome_lbl.place(x = width/2-width_welcome/2, y = height/10, width = width_welcome, height = height_welcome)
btn.place(x = 150, y = height/10+height_welcome, width = 150, height = 25)
  
root.mainloop() 