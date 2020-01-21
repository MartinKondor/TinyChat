# pyinstaller --noconsole __main__.py
from tkinter import Tk, Menu, Listbox, Scrollbar, Entry, StringVar, SINGLE, END, CENTER, ACTIVE, LEFT, N, S, E, W
from tkinter.ttk import Button, Style
from tkinter.messagebox import showinfo, showerror, askquestion
from tkinter.filedialog import askopenfilename, asksaveasfilename

from eth import *


class TalkGUI(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        try:  # Set icon
            self.iconbitmap('icon.ico')
        except Exception:
            pass

        self.MY_NAME = 'anonymous'

        self.wm_title('TalkGUI')
        self.resizable(True, True)
        self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))
        self.bind('<Key>', self.keypress)

        self.msg_list = Listbox(self, selectmode=SINGLE, height=10, width=50, borderwidth=0)
        self.msg_scb = Scrollbar(self, orient='vertical')
        self.msg_scb.grid(padx=0, pady=0, row=0, column=1, sticky=N + S)
        self.msg_list.config(yscrollcommand=self.msg_scb.set)
        self.msg_scb.config(command=self.msg_list.yview)
        
        self.entry_box = Entry(self, textvariable=StringVar(), bd=0, width=50, bg='white', fg='black')
        self.entry_button = Button(self, text='→', width=3, command=self.send_msg)
        
        self.msg_list.grid(padx=0, pady=0, row=0, column=0)
        self.entry_box.grid(padx=0, pady=0, row=1, column=0)
        self.entry_button.grid(padx=0, pady=0, row=1, column=1)
        
        # Connect on the ethernet port
        self.ETH = eth_setup(IS_SERVER)
        Thread(target=self.recv_msg).start()
        
        self.mainloop()

    def send_msg(self):
        msg_to_send = self.entry_box.get()
        self.entry_box.delete(0, END)
        
        if msg_to_send:
            if msg_to_send[0] == '/':  # Commands
                cmd = msg_to_send.split(' ')
                
                if cmd[0] == '/setname':
                    self.MY_NAME = cmd[1].strip()
                    
                return
        
            msg_to_send = self.MY_NAME + ': ' + msg_to_send
            self.msg_list.insert(END, msg_to_send)
            self.msg_list.yview_moveto('1')  # Scroll down
            self.ETH.send(eth_encode(msg_to_send))

    def recv_msg(self):
        while True:
            data = eth_decode(self.ETH.recv(1024))
            if data:
                self.msg_list.insert(END, data)
                self.msg_list.yview_moveto('1')  # Scroll down

    def keypress(self, event):
        # print(repr(event.char))
        # Turned off because \x08 == Ctrl + h and \x08 == Backspace
        # if event.char == '\x08':  # Ctrl + h
            # self.help()

        if event.char == '\r':
            self.send_msg()


if __name__ == '__main__':
    TalkGUI()

