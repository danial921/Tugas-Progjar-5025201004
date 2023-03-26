from socket import *
import socket
import threading
import logging
import datetime
import sys
import pytz

class ProcessTheClient(threading.Thread):
        def __init__(self,connection,address):
                self.connection = connection
                self.address = address
                threading.Thread.__init__(self)

        def run(self):
                while True:
                        # baca request dari client
                        data = self.connection.recv(1024).decode('utf-8')

                        # cek apakah data yang diterima sesuai dengan format yang diharapkan
                        if data.startswith('TIME') and data.endswith('\r\n'):
                                # ambil waktu saat ini
                                #response = 'JAM {}{}\r\n'.format(datetime.datetime.now().strftime('%H:%M:%S'), chr(13)+chr(10))
                                # kirim response ke client

                                # ambil waktu saat ini dan konversi ke waktu Indonesia
                                indonesia_timezone = pytz.timezone('Asia/Jakarta')
                                server_time = datetime.datetime.now(tz=indonesia_timezone)
                                # format waktu ke dalam string
                                indonesia_time_str = server_time.strftime('%H:%M:%S')
                                # buat response dan kirim ke client
                                response = f'JAM {indonesia_time_str}\r\n'
                                self.connection.send(response.encode('utf-8'))
                        else:
                                break
                self.connection.close()

class Server(threading.Thread):
        def __init__(self):
                self.the_clients = []
                self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                threading.Thread.__init__(self)

        def run(self):
                self.my_socket.bind(('0.0.0.0',45000))
                self.my_socket.listen(5)
                while True:
                        self.connection, self.client_address = self.my_socket.accept()
                        logging.warning(f"connection from {self.client_address}")

                        clt = ProcessTheClient(self.connection, self.client_address)
                        clt.start()
                        self.the_clients.append(clt)


def main():
        svr = Server()
        svr.start()

if __name__=="__main__":
        main()