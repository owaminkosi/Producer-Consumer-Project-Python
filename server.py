import socket
import threading
import time
import random
import os
import sys

#Network Configuration
HOST = '127.0.0.1' # Localhost
PORT = 65432       # Port to listen on

#Buffer State (Shared Resource)
#Buffer size declaration
MAX_SIZE = 10
buffer = [] # Stores the XML string data
buffer_lock = threading.Lock() # Protects the buffer list

# Utility Function for XML Handling; Since clients will send XML data
#  the server stores the strings no the files
# We will use the XML functions from student_handler on the clients.

# Client Handler Function

def handle_producer(conn):
    """Handles incoming data from a Producer Client."""
    global buffer
    
    # 1. Receive data size header
    try:
        data_size_header = conn.recv(1024).decode()
        data_size = int(data_size_header.split(":")[1])
    except Exception:
        print("Server: Producer header error.")
        return

    # 2. Wait for empty space in the buffer
    while True:
        with buffer_lock:
            if len(buffer) < MAX_SIZE:
                # Buffer has space, proceed to receive data
                break
            else:
                # Buffer is full (Rule 1 enforcement)
                print("Server: Producer waiting, buffer is full.")
        
        # Tell the client to wait or simply pause this thread
        time.sleep(1) 

    # 3. Receive the full XML data (string)
    full_data = b''
    bytes_received = 0
    while bytes_received < data_size:
        chunk = conn.recv(min(4096, data_size - bytes_received))
        if not chunk:
            break
        full_data += chunk
        bytes_received += len(chunk)

    # 4. Add to the buffer (CRITICAL SECTION)
    with buffer_lock:
        buffer.append(full_data.decode('utf-8'))
        print(f"✅ Server: Added item to buffer. Size: {len(buffer)}/{MAX_SIZE}")

def handle_consumer(conn):
    """Handles data requests from a Consumer Client."""
    global buffer

    # 1. Wait for data in the buffer
    # Buffer is empty (Rule 2 enforcement)
    while True:
        with buffer_lock:
            if len(buffer) > 0:
                # Buffer has data, proceed to send
                break
            else:
                print("Server: Consumer waiting, buffer is empty.")
                #pause the thread or apply a 'wait signal'
        
        time.sleep(1)

    # 2. Remove from the buffer (CRITICAL SECTION)
    with buffer_lock:
        xml_string = buffer.pop(0)
        print(f"🔴 Server: Item removeds. Size: {len(buffer)}/{MAX_SIZE}")

    # 3. Send the XML string back to the client
    xml_data = xml_string.encode('utf-8')
    data_size = len(xml_data)
    
    # Send a header first: CLIENT_TYPE:DATA_SIZE
    header = f"XML_DATA:{data_size}".encode('utf-8')
    conn.sendall(header)
    time.sleep(0.1) # Brief pause to ensure header is received first

    # Send the actual XML data
    conn.sendall(xml_data)
    print("Server: Data sent to consumer.")


def server_listener():
    """Main server loop that accepts client connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        
        while True:
            # Wait for a connection
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            
            # The first message from the client determines its role
            try:
                client_role = conn.recv(1024).decode().strip()
            except Exception:
                conn.close()
                continue

            if client_role == "PRODUCER":
                # Start a new thread to handle the Producer's request
                thread = threading.Thread(target=handle_producer, args=(conn,))
                thread.start()
            elif client_role == "CONSUMER":
                # Start a new thread to handle the Consumer's request
                thread = threading.Thread(target=handle_consumer, args=(conn,))
                thread.start()
            else:
                print("Server: Unknown client role. Closing connection.")
                conn.close()

if __name__ == "__main__":
    try:
        server_listener()
    except KeyboardInterrupt:
        print("\nServer shutting down.")

        sys.exit(0)
