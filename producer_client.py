import socket
import time
import sys
# Import our handler functions
from student_handler import generate_random_student, wrap_to_xml
import xml.etree.ElementTree as ET

# --- Network Configuration ---
HOST = '127.0.0.1' 
PORT = 65432       
ROLE = "PRODUCER"

# --- Producer Logic ---
def run_producer_client():
    
    while True:
        # 1. Produce the item (Generate student data)
        student = generate_random_student()
        
        # Convert student to XML string (not a file)
        root = ET.Element("ITstudent")
        # Reuse wrapping logic to populate the Element Tree
        ET.SubElement(root, "Name").text = student.name
        ET.SubElement(root, "StudentID").text = str(student.student_id)
        ET.SubElement(root, "Programme").text = student.programme
        
        courses_elem = ET.SubElement(root, "Courses")
        for course_name, mark in student.courses.items():
            course = ET.SubElement(courses_elem, "Course")
            ET.SubElement(course, "Name").text = course_name
            ET.SubElement(course, "Mark").text = str(mark)

        xml_string = ET.tostring(root, encoding='utf-8').decode('utf-8')
        
        xml_data = xml_string.encode('utf-8')
        data_size = len(xml_data)

        # 2. Connect and Send
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(ROLE.encode('utf-8')) # Identify self
                time.sleep(0.1)

                # Send size header: PRODUCER:DATA_SIZE
                header = f"PRODUCER:{data_size}".encode('utf-8')
                s.sendall(header)
                time.sleep(0.1)
                
                # Send the actual XML data
                s.sendall(xml_data)
                
                print(f"Producer Client: Sent student {student.name} ({data_size} bytes)")

        except ConnectionRefusedError:
            print("Producer Client: Connection refused. Is the server running?")
        except Exception as e:
            print(f"Producer Client Error: {e}")
        
        time.sleep(random.uniform(0.5, 2)) # Production delay

if __name__ == "__main__":
    try:
        run_producer_client()
    except KeyboardInterrupt:
        print("\nProducer Client shutting down.")
        sys.exit(0)