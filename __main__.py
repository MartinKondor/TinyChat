import socket
from tkinter import Tk, Menu, Listbox, Label, Scrollbar, Entry, StringVar, SINGLE, END, CENTER, ACTIVE, LEFT, N, S, E, W
from tkinter.ttk import Button, Style
from tkinter.messagebox import showinfo, showerror, askquestion
from tkinter.filedialog import askopenfilename, asksaveasfilename

try:
    from eth import *
except:
    pass


MY_NAME = 'anonymous'


class SetupWindow(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        try:  # Set icon
            self.iconbitmap('icon.ico')
        except Exception:
            pass

        self.wm_title('TinyChat')
        self.resizable(False, False)
        self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))

        self.name = 'anonymous'
        self.other_ip = socket.gethostbyname(socket.gethostname() )
        self.is_server = True

        self.name_label = Label(self, text='Name')
        self.other_ip_label = Label(self, text='IP')
        self.server_label = Label(self, text='Server')

        self.name_entry = Entry(self, textvariable=StringVar(), bd=1, width=30, bg='white', fg='black')
        self.other_ip_entry = Entry(self, textvariable=StringVar(), bd=1, width=30, bg='white', fg='black')
        self.server_button = Button(self, text='Yes', width=22, command=lambda: self.set_is_server())
        self.apply_button = Button(self, text='Start', width=7, command=self.apply)

        self.name_entry.config(textvariable=StringVar(self, self.name))
        self.other_ip_entry.config(textvariable=StringVar(self, self.other_ip))

        self.name_label.grid(padx=1, pady=2, row=0, column=0)
        self.name_entry.grid(padx=1, pady=2, row=0, column=1)
        self.other_ip_label.grid(padx=1, pady=2, row=1, column=0)
        self.other_ip_entry.grid(padx=1, pady=2, row=1, column=1)
        self.server_label.grid(padx=1, pady=2, row=2, column=0)
        self.server_button.grid(padx=1, pady=2, row=2, column=1)
        self.apply_button.grid(padx=1, pady=5, row=3, column=1)

        self.mainloop()

    def set_is_server(self):
        self.is_server = not self.is_server
        self.server_button.config(text='Yes' if self.is_server else 'No')

    def apply(self):
        global MY_NAME, OTHER_IP, IS_SERVER

        if self.name_entry.get() and self.other_ip_entry.get():
            MY_NAME = self.name_entry.get()
            OTHER_IP = self.other_ip_entry.get()
            IS_SERVER = self.server_button.cget('text') == 'Yes'
            self.destroy()


class TalkGUI(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        try:  # Set icon
            self.iconbitmap('icon.ico')
        except Exception:
            pass

        self.wm_title('TalkGUI')
        self.resizable(False, False)
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
                    MY_NAME = cmd[1].strip()
                    
                return
        
            msg_to_send = MY_NAME + ': ' + msg_to_send
            self.msg_list.insert(END, msg_to_send)
            self.msg_list.yview_moveto('1')  # Scroll down to the last message
            self.ETH.send(eth_encode(msg_to_send))

    def recv_msg(self):
        while True:
            data = eth_decode(self.ETH.recv(1024))
            if data:
                self.msg_list.insert(END, data)
                self.msg_list.yview_moveto('1')  # Scroll down to the last message

    def keypress(self, event):
        # print(repr(event.char))
        # Turned off because \x08 == Ctrl + h and \x08 == Backspace
        # if event.char == '\x08':  # Ctrl + h
            # self.help()

        if event.char == '\r':
            self.send_msg()
            self.msg_list.yview_moveto('1')  # Scroll down to the last message


if __name__ == '__main__':
    SetupWindow()
    TalkGUI()
