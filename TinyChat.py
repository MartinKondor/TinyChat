import os
import sys
import time
import json
import socket
import threading
from tkinter import Tk, Menu, Listbox, Label, Scrollbar, Entry, StringVar, SINGLE, END, CENTER, ACTIVE, LEFT, N, S, E, W
from tkinter.ttk import Button, Style
from tkinter.messagebox import showinfo, showerror, askquestion
from tkinter.filedialog import askopenfilename, asksaveasfilename

from playsound import playsound

from eth import ETHConnection


MY_NAME = ''
OTHER_IP = ''
IS_SERVER = False
EXITED = False


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class SetupWindow(Tk):
    """
    Little GUI for setting user's name, the partner's ip and that
    the PC is a server or not.
    """

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
        self.other_ip = socket.gethostbyname(socket.gethostname())
        self.is_server = True

        # Read last config from file
        if os.path.isfile('config.json'):
            with open('config.json', 'r') as file:
                config = json.load(file)
                self.name = config['name']
                self.other_ip = config['other_ip']
                self.is_server = config['is_server']

        self.name_label = Label(self, text='Name')
        self.other_ip_label = Label(self, text='IP')
        self.server_label = Label(self, text='Server')

        self.name_entry = Entry(self, textvariable=StringVar(), bd=1, width=30, bg='white', fg='black')
        self.other_ip_entry = Entry(self, textvariable=StringVar(), bd=1, width=30, bg='white', fg='black')
        self.server_button = Button(self, text='Yes' if self.is_server else 'No', width=22, command=lambda: self.set_is_server())
        self.apply_button = Button(self, text='Start', width=7, command=self.apply)

        self.name_entry.config(textvariable=StringVar(self, self.name))
        self.other_ip_entry.config(textvariable=StringVar(self, self.other_ip))
        self.other_ip_entry.config(state='disabled' if self.is_server else 'normal')

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
        self.other_ip_entry.config(state='disabled' if self.is_server else 'normal')

    def apply(self):
        global MY_NAME, OTHER_IP, IS_SERVER

        if self.name_entry.get() and self.other_ip_entry.get():
            MY_NAME = self.name_entry.get()
            OTHER_IP = self.other_ip_entry.get()
            IS_SERVER = self.server_button.cget('text') == 'Yes'

            config = {
                'name': MY_NAME,
                'other_ip': OTHER_IP,
                'is_server': IS_SERVER
            }
            with open('config.json', 'w+') as file:
                json.dump(config, file)

            self.destroy()


class TinyChat(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        try:  # Set icon
            self.iconbitmap('icon.ico')
        except Exception:
            pass

        self.wm_title('TinyChat')
        self.resizable(False, False)
        self.eval('tk::PlaceWindow %s center' % self.winfo_pathname(self.winfo_id()))
        self.bind('<Key>', self.keypress)

        self.sound_played_for_notification = False
        self.new_notification = False
        self.line_width = 42

        self.msg_list = Listbox(self, selectmode=SINGLE, height=10, width=self.line_width, borderwidth=0)
        self.msg_scb = Scrollbar(self, orient='vertical')
        self.msg_scb.grid(padx=0, pady=0, row=0, column=1, sticky=N + S)
        self.msg_list.config(yscrollcommand=self.msg_scb.set)
        self.msg_scb.config(command=self.msg_list.yview)
        
        self.entry_box = Entry(self, textvariable=StringVar(), bd=0, width=self.line_width, bg='white', fg='black')
        self.entry_button = Button(self, text='→', width=3, command=self.send_msg)
        
        self.msg_list.grid(padx=0, pady=0, row=0, column=0)
        self.entry_box.grid(padx=0, pady=0, row=1, column=0)
        self.entry_button.grid(padx=0, pady=0, row=1, column=1)
        
        # Connect on the ethernet port
        self.ETH = ETHConnection(OTHER_IP, IS_SERVER)

        # self.msg_recv_thread = Thread(target=self.recv_msg)
        # self.msg_recv_thread.start()
        # self.notifications_thread = Thread(target=self.notifications)
        # self.notifications_thread.start()
        self.msg_recv_thread = self.recv_msg()
        self.notifications_thread = self.notifications()

        self.wm_attributes('-topmost', 1)
        self.bind('<FocusIn>', self.handle_focus)
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.mainloop()

    def send_msg(self):
        global MY_NAME, OTHER_IP, IS_SERVER
        msg_to_send = self.entry_box.get()
        self.entry_box.delete(0, END)
        
        if msg_to_send:
            if msg_to_send[0] == '/':  # Commands
                cmd = msg_to_send.split(' ')
                
                if cmd[0] == '/?':
                    self.msg_list.insert(END, ' ')
                    self.msg_list.insert(END, 'HELP:')
                    self.msg_list.insert(END, '/setname NAME - Sets your name for the given NAME.')
                    self.msg_list.insert(END, '/re - Tries to reconnect.')
                    self.msg_list.insert(END, '/ip IP - Sets the partner\'s ip to IP.')
                    self.msg_list.insert(END, ' ')
                if cmd[0] == '/setname':
                    MY_NAME = cmd[1].strip()
                if cmd[0] == '/re':
                    self.ETH.reconnect()
                if cmd[0] == '/ip':
                    OTHER_IP = cmd[1].strip()
                    
                return
        
            msg_to_send = MY_NAME + ': ' + msg_to_send
            self.add_msg(msg_to_send)
            
            try:
                self.ETH.send(msg_to_send)
            except:
                self.msg_list.insert(END, 'There is noone on the other end  ¯\\_(ツ)_/¯.')
                
                # Try to reestabilish connection
                self.ETH.reconnect()
                self.msg_recv_thread = self.recv_msg()
                self.msg_recv_thread.start()

    def add_msg(self, msg):
        if len(msg) > self.line_width:
            for i in range(int(len(msg) / self.line_width) + 1):
                self.msg_list.insert(END, msg[i * self.line_width:(i + 1) * self.line_width])
        else:
            self.msg_list.insert(END, msg)
        
        self.msg_list.yview_moveto('1')  # Scroll down to the last message

    def handle_focus(self, e):
        self.new_notification = False

    @threaded
    def recv_msg(self):
        global EXITED
        while not EXITED:
            time.sleep(0.1)

            if not self.ETH:
                continue

            data = self.ETH.recv(1024)
            if data:
                self.add_msg(data)
                self.new_notification = True
                self.sound_played_for_notification = False

    @threaded
    def notifications(self):
        global EXITED
        while not EXITED:
            time.sleep(0.1)

            if self.new_notification:
                if not self.sound_played_for_notification:
                    playsound('audio/notification.wav')
                    self.sound_played_for_notification = True

    def on_closing(self):
        """
        if self.ETH.is_connected:
            self.ETH.send(MY_NAME + ' has left the chat.')
            self.ETH.close()
        """
        global EXITED
        EXITED = True
        self.notifications_thread.join()
        self.msg_recv_thread.join()
        self.destroy()

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

    if MY_NAME:
        TinyChat()
