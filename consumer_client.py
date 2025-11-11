import socket
import time
import sys
import xml.etree.ElementTree as ET
# Import our class and functions
from student_handler import ITstudent, unwrap_from_xml_string # We will define this helper function

# --- Network Configuration ---
HOST = '127.0.0.1' 
PORT = 65432       
ROLE = "CONSUMER"

# --- Helper function (since we are dealing with strings now, not files) ---
def unwrap_from_xml_string(xml_string):
    """Parses an XML string and returns an ITstudent object."""
    try:
        root = ET.fromstring(xml_string)
        
        name = root.find("Name").text
        student_id = int(root.find("StudentID").text)
        programme = root.find("Programme").text
        
        courses = {}
        for course in root.find("Courses"):
            course_name = course.find("Name").text
            mark = int(course.find("Mark").text)
            courses[course_name] = mark
            
        return ITstudent(name, student_id, programme, courses)
    except Exception as e:
        print(f"Error unwrapping XML string: {e}")
        return None


# --- Consumer Logic ---
def run_consumer_client():
    while True:
        # 1. Connect and Request
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(ROLE.encode('utf-8')) # Identify self

                # 2. Receive size header
                data_size_header = s.recv(1024).decode()
                
                if not data_size_header:
                     # This happens if the server closes the connection (e.g., due to an error)
                     print("Consumer Client: Server did not send a header. Retrying...")
                     time.sleep(1)
                     continue

                data_size = int(data_size_header.split(":")[1])
                print(f"Consumer Client: Receiving {data_size} bytes of student data...")

                # 3. Receive the full XML data
                full_data = b''
                bytes_received = 0
                while bytes_received < data_size:
                    chunk = s.recv(min(4096, data_size - bytes_received))
                    if not chunk:
                        break
                    full_data += chunk
                    bytes_received += len(chunk)

                xml_string = full_data.decode('utf-8')

                # 4. Process Item (outside the network code)
                student = unwrap_from_xml_string(xml_string)
                
                if student:
                    print(f"🔴 Consumer Client: Received and processed student data.")
                    # Print full report including Avg and Pass/Fail
                    print(student)
                
        except ConnectionRefusedError:
            print("Consumer Client: Connection refused. Is the server running?")
        except Exception as e:
            # Catch exceptions like socket errors or parsing errors
            print(f"Consumer Client Error: {e}")
        
        time.sleep(random.uniform(1, 4)) # Consumption delay

if __name__ == "__main__":
    try:
        run_consumer_client()
    except KeyboardInterrupt:
        print("\nConsumer Client shutting down.")
        sys.exit(0)