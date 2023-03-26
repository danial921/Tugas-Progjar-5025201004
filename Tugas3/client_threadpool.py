import sys
import socket
import logging
import concurrent.futures
import time
import threading

max_thread = 0
def kirim_data(urutan):
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
        logging.warning(f"closing ke --> {urutan}")
        global max_thread
        max_thread = max(max_thread,threading.active_count())
        sock.close()
    return

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(4):
            executor.submit(kirim_data(i))
        print("Thread Pool Max Active: ", max_thread)
        print("Thread Pool Active Sekarang: ", threading.active_count())
    executor.shutdown(wait=True)