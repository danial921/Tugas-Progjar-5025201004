import sys
import threading
import os
import json
import uuid
import logging
import re
from queue import  Queue

class Chat:
    def __init__(self, domain, cross_server):
        self.domain = domain
        self.sessions={}
        self.emails = {}
        self.users = {}
        self.groups = {}
        
        self.cross_server = cross_server
        
    def proses(self,data):
        j=data.split("\r\n")
        try:
            command=j[0].strip()
            # signup handling
            if (command=='signup'):
                username=j[1].strip()
                password=j[2].strip()
                name=j[3].strip()
                country=j[4].strip()
                logging.warning(
                    "Send Command REGISTER: username : {}, pass : {}, name : {}, country : {}" 
                    . format(username, password, name, country)
                    )
                return self.signup_user(username, password, name, country)

            # login handling
            elif (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                logging.warning(
                    "AUTH: username : {}, password : {}" . 
                    format(username,password)
                    )
                return self.autentikasi_user(username,password)
            
            # Sign Up group handling
            elif (command=='signup_group'):
                sessionid = j[1].strip()
                name_group = j[2].strip()
                password = j[3].strip()
                logging.warning(
                    "REGISTER_GROUP : session : {}, group name : {}, password : {}" 
                    . format(sessionid, name_group, password)
                    )
                return self.signup_group(sessionid, name_group, password)
            
            # Sign in group handling
            elif (command=='signin_group'):
                sessionid = j[1].strip()
                name_group = j[2].strip()
                password = j[3].strip()
                logging.warning(
                    "SIGNIN_GROUP: session : {}, join group name : {},  password : {}" 
                    . format(sessionid, name_group, password)
                    )
                return self.signin_group(sessionid, name_group, password)

            # Send Message    
            elif (command=='send'):
                sessionid = j[1].strip()
                email_destination = j[2].strip()
                message= j[3].strip()
                logging.warning("SEND: session {}, Target destination : {}" . format(sessionid, email_destination))
                return self.send_message(sessionid, email_destination, message)
            
            elif (command=='inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning(
                    "INBOX: {}" 
                    . format(sessionid)
                    )
                return self.get_inbox(username)
            
            else:
                return {'status': 'ERROR','message': '**Protocol Tidak Benar'}
        except KeyError:
            return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR','message': '--Protocol Tidak Benar'}
    
    # signup handling
    def signup_user(self, username, password, name, country):
        
        username += "@"+self.domain
        if (username in self.users):
            return { 'status': 'ERROR', 
                    'message': 'Username allready Use' }
        
        self.emails[username]={ 'password': password, 
                                'type': 'personal'
                                }
        self.users[username] = {'name': name, 
                                'country': country, 
                                'incoming' : {}, 
                                'outgoing': {}
                                }
        return { 'status': 'OK',
                 'email': username,
                 'message':'Register Success',
                 }
        
    # login user handling   
    def autentikasi_user(self,username,password):
        username += "@"+self.domain
        
        if (username not in self.users):
            return { 'status': 'ERROR','message': 'Username Not Found' }
        
        if (self.emails[username]['password'] != password):
            return { 'status': 'ERROR','message': 'Wrong PASSWORD Salah' }
        
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username] }
        return { 'status': 'OK', 
                 'tokenid': tokenid,
                 'message':'Login Success', 
                 }
    
    # Grup Sign Up Handling
    def signup_group(self, sessionid, name_group, password):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR','message': 'Session Not Found'}
        
        name_group +="@"+self.domain
        
        if (name_group in self.groups):
            return {'status': 'ERROR','message': 'Group name Already Used'}
        
        self.emails[name_group] = { 'password' : password, 'type' : 'group' }
        self.groups[name_group] = { 'member' : { self.sessions[sessionid]["username"] } }
        return {'status': 'OK', 
                'email_group' : name_group,
                'message':'Register Group Success',
                }

    # Grup Sign In Handling 
    def signin_group(self, sessionid, name_group, password):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR','message': 'Session Not Found'}
        
        email_source = self.sessions[sessionid]["username"]
        self.cross_server.signin_group(None, email_source, name_group, password)
        return {'status': 'OK'}
    
    # Invite User Handling 
    def invite_user(self, email, name_group, password):
        
        if (name_group not in self.groups):
            return {'status': 'ERROR','message': 'Group Not Found'}
        
        if (email in self.groups[name_group]['member']):
            return {'status': 'ERROR','message': 'Allready Joined Group'}
        
        self.groups[name_group]['member'].add(email)
        return {'status': 'OK',
                'message':'Invite User Success'
                }
    
    def get_user(self,username):
        if (username not in self.users):
            return False
        return self.users[username]
    
    def get_type(self, username):
        if username not in self.emails:
            return False
        return self.emails[username]['type']
    
    def is_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def get_email_from_session(self, session):
        if (session not in self.sessions):
            return False
        return self.sessions[session]['username']
    
    def group_member(self, name_group):
        if name_group not in self.groups:
            return False
        return self.groups[name_group]["member"]
    
    def simpan_message(self, source_email, destination_email, message):
        
        email_type = self.get_type(destination_email)
        
        logging.warning(f"MASUK SINI {destination_email} {email_type}")
        
        if email_type == False:
            return
        
        if email_type == "personal" and destination_email in self.users:
            data_destinasi = self.get_user(destination_email)
            inqueue_receiver = data_destinasi['incoming']
            try:
                inqueue_receiver[source_email].put(message)
            except KeyError:
                inqueue_receiver[source_email]=Queue()
                inqueue_receiver[source_email].put(message)
                
        elif email_type == "group" and destination_email in self.groups:
            member = self.group_member(destination_email)
            
            if source_email in member:
                for email_member in member:
                    if email_member != source_email:
                        self.cross_server.send(None, destination_email, email_member, message)
            
    
    def send_message(self, sessionid, email_destination, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR','message': 'Session Not FOUND'}
        
        if (not self.is_email(email_destination)):
            return {'status': 'ERROR','message': 'Destination Adress Wrong'}
        
        email_from = self.get_email_from_session(sessionid)
        data_pengirim = self.get_user(email_from)

        message_json = { 'msg_from': "{}({})" .format(data_pengirim['name'], email_from), 'msg_to': "{}".format(email_destination), 'msg': message }
        message = json.dumps(message_json)
        
        self.cross_server.send(None, email_from, email_destination, message)
        
        outqueue_sender = data_pengirim['outgoing']
        try:
            outqueue_sender[email_destination].put(message)
        except KeyError:
            outqueue_sender[email_destination]=Queue()
            outqueue_sender[email_destination].put(message)
        
        return {'status': 'OK','message': 'Message Sent'}

    def get_inbox(self,username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs={}
        for users in incoming:
            msgs[users]=[]
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())

        return {'status': 'OK', 'messages': msgs}


if __name__=="__main__":
    domain = "tes.com"
    
    
    from cross_server import CrossServer 
    from server_thread_chat import CrossServerQueueGrabber
    
    cross_server = CrossServer(domain)
    j = Chat(domain, cross_server)
    
    cross_server_queue_grabber = CrossServerQueueGrabber(cross_server.inbox(), j)
    cross_server_queue_grabber.start()
    
    # sesi = j.proses("auth messi surabaya")
    # print(sesi)
    # #sesi = j.autentikasi_user('messi','surabaya')
    # #print sesi
    # tokenid = sesi['tokenid']
    # print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
    # print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

    #print j.send_message(tokenid,'messi','henderson','hello son')
    #print j.send_message(tokenid,'henderson','messi','hello si')
    #print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


    # print("isi mailbox dari messi")
    # print(j.get_inbox('messi'))
    # print("isi mailbox dari henderson")
    # print(j.get_inbox('henderson'))
    
    users = [
        {"username" : "satu", "password" : "satu", "name" : "satu", "country" : "Indonesia"},
        {"username" : "dua", "password" : "dua", "name" : "dua", "country" : "Indonesia"},
        {"username" : "tiga", "password" : "tiga", "name" : "tiga", "country" : "Indonesia"}
    ]
    
    for user in users:
        print(j.proses(f"signup\r\n{user['username']}\r\n{user['password']}\r\n{user['name']}\r\n{user['country']}\r\n\r\n"))
        
    print(j.emails)
        
    token = {}
    for user in users:
        res = j.proses(f"auth\r\n{user['username']}\r\n{user['password']}\r\n\r\n")
        print(res)
        token[user['username']] = res['tokenid']
        
    pesan = [
        f"send\r\n{token[users[0]['username']]}\r\n{users[1]['username']+'@'+domain}\r\nDARI SATU MENUJU DUA\r\n\r\n",
        f"send\r\n{token[users[1]['username']]}\r\n{users[0]['username']+'@'+domain}\r\nDARI DUA MENUJU SATU\r\n\r\n",
    ]
    
    for p in pesan:
        print(j.proses(p))
    
    import time
    
    time.sleep(1)
    
    for user in users:
        print(f"inbox {user['username']+'@'+domain}:")
        print(j.proses(f"inbox\r\n{token[user['username']]}"))
    
    signup_group = f"signup_group\r\n{token[users[0]['username']]}\r\nbilangan\r\nangka\r\n\r\n"
    print(j.proses(signup_group))
    
    signin_group = f"signin_group\r\n{token[users[1]['username']]}\r\n{'bilangan@'+domain}\r\nangka\r\n\r\n"
    print(j.proses(signin_group))
    
    pesan_group_member = f"send\r\n{token[users[1]['username']]}\r\n{'bilangan@'+domain}\r\nDARI DUA MENUJU SEMUA ANGGOTA GRUP BILANGAN\r\n\r\n"
    print(j.proses(pesan_group_member))
    
    pesan_group_non_member = f"send\r\n{token[users[2]['username']]}\r\n{'bilangan@'+domain}\r\nDARI TIGA MENUJU SEMUA ANGGOTA GRUP BILANGAN YANG SEHARUSNYA TIDAK BERHASIL\r\n\r\n"
    print(j.proses(pesan_group_non_member))
    
    
    
    time.sleep(1)
    
    for user in users:
        print(f"inbox {user['username']+'@'+domain}:")
        print(j.proses(f"inbox\r\n{token[user['username']]}"))
    
    print(j.users)
    
    signin_group = f"signin_group\r\n{token[users[2]['username']]}\r\n{'bilangan@'+domain}\r\nangka\r\n\r\n"
    print(j.proses(signin_group))
    
    pesan_group_member = f"send\r\n{token[users[0]['username']]}\r\n{'bilangan@'+domain}\r\nDARI SATU MENUJU SEMUA ANGGOTA GRUP BILANGAN\r\n\r\n"
    print(j.proses(pesan_group_member))
    
    pesan_group_member = f"send\r\n{token[users[1]['username']]}\r\n{'bilangan@'+domain}\r\nDARI DUA MENUJU SEMUA ANGGOTA GRUP BILANGAN\r\n\r\n"
    print(j.proses(pesan_group_member))
    
    time.sleep(1)
    
    for user in users:
        print(f"inbox {user['username']+'@'+domain}:")
        print(j.proses(f"inbox\r\n{token[user['username']]}"))
    
    print(j.users)