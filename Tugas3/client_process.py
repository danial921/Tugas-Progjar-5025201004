import sys
import socket
import logging
import time
import threading
from multiprocessing import Process

max_thread = 0
def kirim_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.warning("membuka socket")

    server_address = ('172.16.16.101', 45000)
    logging.warning(f"opening socket {server_address}")
    sock.connect(server_address)

    try:
        # Send data
        message = 'TIME\r\n'
        logging.warning(f"[CLIENT] sending {message}")
        sock.sendall(message.encode('utf-8'))
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(1024).decode('utf-8')
            amount_received += len(data)
            logging.warning(f"[DITERIMA DARI SERVER] {data}")
    finally:
        logging.warning("===================")
        logging.warning("closing")
        global max_thread
        max_thread = max(max_thread,threading.active_count())
        logging.warning("===================\n")
        sock.close()
    return


if __name__=='__main__':
    process = []
    for i in range(4):
        proces = Process(target=kirim_data)
        process.append(proces)
        proces.start()
    print("process Max Active: ", max_thread)
    print("processMax Active Sekarang: ", threading.active_count())
    for proces in process:
       proces.join()

    
