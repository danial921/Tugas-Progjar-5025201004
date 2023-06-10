import socket
import os
import json

TARGET_IP = "172.16.16.102"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
        
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            # Command Registration
            if (command=='signup'):
                username=j[1].strip()
                password=j[2].strip()
                name=j[3].strip()
                country=j[4].strip()
                return self.signup(username, password, name, country)
            
            # Command Registration
            elif (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            
            # command send message
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            
            # command makegroup
            elif (command=='makegroup'):
                name_group = j[1].strip()
                password = j[2].strip()
                return self.makegroup(name_group, password)
            
            # command signingroup
            elif (command=='signingroup'):
                name_group = j[1].strip()
                password = j[2].strip()
                return self.signingroup(name_group, password)
            
            # command check inbox 
            elif (command=='inbox'):
                return self.inbox()
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
            
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
        
    # Sign Up Function
    def signup(self, username, password, name, country):
        string = "signup\r\n{}\r\n{}\r\n{}\r\n{}\r\n\r\n".format(username,password,name,country)
        print("signup\r\n username\t : {}\r\n password\t : {}\r\n name \t\t : {}\r\n country\t : {}\r\n"
              . format(username,password, name, country)
              )
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Succesfull SignUp, email created : {}".format(result['email'])
        else:
            return "Error, {}" . format(result['message'])
    
    # Auth function
    def login(self,username,password):
        string="auth\r\n{}\r\n{}\r\n\r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "Succesfull Login, username : {} logged in, token : {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])

    # Sendmessage function 
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, token not authorized"
        string="send\r\n{}\r\n{}\r\n{}\r\n\r\n".format(self.tokenid,usernameto,message)
        print("send message\r\n token id \t : {}\r\n target Uname \t : {}\r\n message \t : {}\r\n\r\n"
              .format(self.tokenid,usernameto,message))
        result = self.sendstring(string)
        if result['status']=='OK':
            return "succesed message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    
    # makegroup function  
    def makegroup(self, name_group, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        string = "signup_group\r\n{}\r\n{}\r\n{}\r\n\r\n".format(self.tokenid, name_group, password)
        print("signup_group\r\n self_token \t:{}\r\n groupname \t : {}\r\n password \t : {}\r\n\r\n"
              .format(self.tokenid, name_group, password))
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Succesed Register Group, email group {}".format(result['email_group'])
        else:
            return "Error, {}" . format(result['message'])
    
    # Join Group Function
    def signingroup(self, name_group, password):
        if (self.tokenid==""):
            return "Error, token not authorized"
        
        string = "signin_group\r\n{}\r\n{}\r\n{}\r\n\r\n".format(self.tokenid,name_group,password)
        print("signin_group\r\n self_token \t : {}\r\n name \t : {}\r\n password \t :{}\r\n\r\n".format(self.tokenid,name_group,password))
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Succesed Join Group, group name {}".format(name_group)
        else:
            return "Error, {}" . format(result['message'])
        
    # Check Inbox function
    def inbox(self):
        if (self.tokenid==""):
            return "Error, token not authorized"
        string="inbox\r\n{}\r\n\r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])



if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))