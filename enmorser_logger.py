from tkinter import *
import sqlite3
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
import sys
from datetime import datetime

now = datetime.utcnow() # current UTC date and time

year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")

ymdate = now.strftime("%Y-%m-%d")
utc_time = now.strftime("%H%M")

root = Tk()
root.title("EnMorser Contact Log")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width = 480
height = 320

x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry('%dx%d+%d+%d' % (width, height, x, y))
root.resizable(0, 0)        # Load the image file from disk.

#icon = root.PhotoImage(file="em_icon1.png")
# Set it as the window icon.
#root.iconphoto(True, icon)

#==================================METHODS============================================

def UpdateNow():
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    ymdate = now.strftime("%Y-%m-%d")
    utc_time = now.strftime("%H%M")

    string = now.strftime(' %I:%M:%S %p ')

def Database():
    global conn, cursor
    conn = sqlite3.connect('enmorser_log.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `enmorser_log` (mem_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, contact TEXT, ymd TEXT, utctime TEXT, notes TEXT)")

def Create():
    UpdateNow()
    UTC_TIME.set("")
    UTC_TIME.set(utc_time)
    if  CONTACT_CALL.get() == "" or YM_DATE.get() == "" or UTC_TIME.get() == "" or NOTES.get() == "":
        txt_result.config(text="Enter required fields.", fg="red")
    else:
        Database()
        cursor.execute("INSERT INTO 'enmorser_log' (contact, ymd, utctime, notes) VALUES(?, ?, ?, ?)", (str(CONTACT_CALL.get()), str(YM_DATE.get()), str(UTC_TIME.get()), str(NOTES.get())))
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM `enmorser_log` ORDER BY `ymd` desc, `utctime` desc")
        fetch = cursor.fetchall()
        for data in fetch:
            tree.insert('', 'end', values=(data[0], data[1], data[2], data[3], data[4]))
        conn.commit()
        cursor.close()
        conn.close()
        CONTACT_CALL.set("")
        YM_DATE.set("")
        YM_DATE.set(ymdate)
        UTC_TIME.set("")
        UTC_TIME.set(utc_time)
        NOTES.set("")
        txt_result.config(text="Log record entered.", fg="green")

def Read():
    tree.delete(*tree.get_children())
    Database()
    cursor.execute("SELECT * FROM `enmorser_log` ORDER BY `ymd` desc, `utctime` desc")
    fetch = cursor.fetchall()
    for data in fetch:
        tree.insert('', 'end', values=(data[0], data[1], data[2], data[3], data[4]))
    cursor.close()
    conn.close()
    UpdateNow()
    CONTACT_CALL.set("")
    YM_DATE.set(ymdate)
    UTC_TIME.set(utc_time)
    NOTES.set("")
    btn_create.config(state=NORMAL)
    btn_read.config(state=NORMAL)
    btn_update.config(state=DISABLED)
    btn_delete.config(state=DISABLED)
    txt_result.config(text="Listed the latest entries in the log.", fg="black")

def Update():
    Database()
    tree.delete(*tree.get_children())
    cursor.execute("UPDATE `enmorser_log` SET `contact` = ?, `ymd` = ?, `utctime` =?,  `notes` = ? WHERE `mem_id` = ?", (str(CONTACT_CALL.get()), str(YM_DATE.get()), str(UTC_TIME.get()), str(NOTES.get()), int(mem_id)))
    conn.commit()
    cursor.execute("SELECT * FROM `enmorser_log` ORDER BY `ymd` desc, `utctime` desc")
    fetch = cursor.fetchall()
    for data in fetch:
        tree.insert('', 'end', values=(data[0], data[1], data[2], data[3], data[4]))
    cursor.close()
    conn.close()
    CONTACT_CALL.set("")
    YM_DATE.set(ymdate)
    UTC_TIME.set(utc_time)
    NOTES.set("")
    btn_create.config(state=NORMAL)
    btn_read.config(state=NORMAL)
    btn_update.config(state=DISABLED)
    btn_delete.config(state=NORMAL)
    txt_result.config(text="Successfully updated the log record", fg="black")


def OnSelected(event):
    global mem_id;
    curItem = tree.focus()
    contents =(tree.item(curItem))
    selecteditem = contents['values']
    mem_id = selecteditem[0]
    CONTACT_CALL.set("")
    YM_DATE.set("")
    UTC_TIME.set("")
    NOTES.set("")
    CONTACT_CALL.set(selecteditem[1])
    YM_DATE.set(selecteditem[2])
    UTC_TIME.set(selecteditem[3])
    NOTES.set(selecteditem[4])
    btn_create.config(state=DISABLED)
    btn_read.config(state=NORMAL)
    btn_update.config(state=NORMAL)
    btn_delete.config(state=NORMAL)

def Delete():
    if not tree.selection():
       txt_result.config(text="Please select an item first", fg="red")
    else:
        result = tkMessageBox.askquestion('EnMorser Contact Log', 'Are you sure you want to delete this record?', icon="warning")
        if result == 'yes':
            curItem = tree.focus()
            contents =(tree.item(curItem))
            selecteditem = contents['values']
            tree.delete(curItem)
            Database()
            cursor.execute("DELETE FROM `enmorser_log` WHERE `mem_id` = %d" % selecteditem[0])
            conn.commit()
            cursor.close()
            conn.close()
            CONTACT_CALL.set("")
            YM_DATE.set(ymdate)
            UTC_TIME.set(utc_time)
            NOTES.set("")
            btn_create.config(state=NORMAL)
            btn_read.config(state=NORMAL)
            btn_update.config(state=DISABLED)
            btn_delete.config(state=DISABLED)
            txt_result.config(text="Successfully deleted the log record", fg="black")


def Exit():
    result = tkMessageBox.askquestion('EnMorser Contact Log', 'Are you sure you want to exit?', icon="warning")
    if result == 'yes':
        root.destroy()
        sys.exit()

#==================================VARIABLES==========================================
CONTACT_CALL = StringVar()
YM_DATE = StringVar()
UTC_TIME = StringVar()
NOTES = StringVar()

#==================================FRAME==============================================
#Top = Frame(root, width=900, height=50, bd=8, relief="raise")
Top = Frame(root, width=480, height=40, bd=8)
Top.pack(side=TOP)
#Left = Frame(root, width=300, height=500, bd=8, relief="raise")
Left = Frame(root, width=100, height=40, bd=8)
Left.pack(side=LEFT)
#Right = Frame(root, width=600, height=500, bd=8, relief="raise")
Right = Frame(root, width=360, height=40, bd=8)
Right.pack(side=RIGHT)
Forms = Frame(Left, width=260, height=40)
Forms.pack(side=TOP)
#Buttons = Frame(Left, width=300, height=100, bd=8, relief="raise")
Buttons = Frame(Left, width=200, height=40, bd=8)
Buttons.pack(side=BOTTOM)

#==================================LABEL WIDGET=======================================
txt_title = Label(Top, width=230, font=('arial', 14), text = "EnMorser Contact Log")
txt_title.pack()
txt_contact = Label(Forms, text="Contact Call:", font=('arial', 12), bd=5)
txt_contact.grid(row=0, sticky="e")
txt_ymd = Label(Forms, text="Date:", font=('arial', 12), bd=5)
txt_ymd.grid(row=1, sticky="e")
txt_utctime = Label(Forms, text="UTC Time:", font=('arial', 12), bd=5)
txt_utctime.grid(row=2, sticky="e")
txt_notes = Label(Forms, text="Notes:", font=('arial', 12), bd=5)
txt_notes.grid(row=3, sticky="e")
txt_result = Label(Buttons)
txt_result.pack(side=TOP)

#==================================ENTRY WIDGET=======================================
contact = Entry(Forms, textvariable=CONTACT_CALL, width=20)
contact.grid(row=0, column=1)
ymd = Entry(Forms, textvariable=YM_DATE, width=20)
ymd.grid(row=1, column=1)
utctime = Entry(Forms, textvariable=UTC_TIME, width=20)
utctime.grid(row=2, column=1)
notes = Entry(Forms, textvariable=NOTES, width=20)
notes.grid(row=3, column=1)

#==================================BUTTONS WIDGET=====================================
btn_create = Button(Buttons, width=5, text="Add", command=Create)
btn_create.pack(side=LEFT)
btn_read = Button(Buttons, width=5, text="List", command=Read)
btn_read.pack(side=LEFT)
btn_update = Button(Buttons, width=6, text="Update", command=Update, state=DISABLED)
btn_update.pack(side=LEFT)
btn_delete = Button(Buttons, width=6, text="Delete", command=Delete, state=DISABLED)
btn_delete.pack(side=LEFT)
btn_exit = Button(Buttons, width=5, text="Exit", command=Exit)
btn_exit.pack(side=LEFT)

#==================================LIST WIDGET========================================

tree = ttk.Treeview(Right, columns=("MemberID", "contact", "date", "time", "notes"),
       selectmode="extended", height=10)
tree.heading('MemberID', text="")
tree.heading('contact', text=" Call  ", anchor=W)
tree.heading('date', text="   Date   ", anchor=W)
tree.heading('time', text="Time ", anchor=W)
tree.heading('notes', text="Notes  ", anchor=W)
tree.column('#0', stretch=NO, width=0)
tree.column('#1', stretch=NO, width=0)
tree.column('#2', width=45)
tree.column('#3', width=70)
tree.column('#4', width=35)
tree.pack()
tree.bind('<Double-Button-1>', OnSelected)
Read()

#==================================INITIALIZATION=====================================
if __name__ == '__main__':
    root.mainloop()
