import xml.etree.ElementTree as ET
import random
import os

# --- 1. Data Lists for Generator ---
FIRST_NAMES = ["Alice", "Bob", "Charlie", "David", "Emily", "Fiona", "George", "Hannah", "Ian", "Julia"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
PROGRAMMES = ["Computer Science", "Information Technology", "Data Science", "Cybersecurity", "Software Engineering"]
COURSES_LIST = ["Programming 101", "Databases", "Networking", "Web Development", "AI and Machine Learning", "Operating Systems", "Data Structures"]

# --- 2. ITstudent Class ---
class ITstudent:
    def __init__(self, name, student_id, programme, courses):
        self.name = name
        self.student_id = student_id
        self.programme = programme
        self.courses = courses # A dictionary like {'Programming 1': 75}

    def get_average(self):
        if not self.courses:
            return 0
        total = sum(self.courses.values())
        return total / len(self.courses)

    def get_pass_fail(self):
        return "Pass" if self.get_average() >= 50 else "Fail"

    def __str__(self):
        # For easy printing by the consumer
        avg = self.get_average()
        status = self.get_pass_fail()
        course_str = ', '.join([f"{course}: {mark}" for course, mark in self.courses.items()])
        
        return (f"\n--- Student Information ---\n"
                f"Name: {self.name}\n"
                f"ID: {self.student_id}\n"
                f"Programme: {self.programme}\n"
                f"Courses: {course_str}\n"
                f"Average: {avg:.2f}\n"
                f"Status: {status}\n"
                f"---------------------------")

# --- 3. Random Student Generator ---
def generate_random_student():
    """Creates a new ITstudent object with random data."""
    
    # Generate simple data
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    student_id = random.randint(10000000, 99999999) # 8 digits
    programme = random.choice(PROGRAMMES)
    
    # Generate 3 to 5 random courses with marks
    courses = {}
    num_courses = random.randint(3, 5)
    # Ensure we pick unique courses
    selected_courses = random.sample(COURSES_LIST, num_courses) 
    
    for course in selected_courses:
        mark = random.randint(30, 100) # Random mark
        courses[course] = mark
        
    return ITstudent(name, student_id, programme, courses)

# --- 4. XML Handling Functions ---
def wrap_to_xml(student, filename):
    """Takes an ITstudent object and writes it to an XML file."""
    try:
        root = ET.Element("ITstudent")
        
        ET.SubElement(root, "Name").text = student.name
        ET.SubElement(root, "StudentID").text = str(student.student_id)
        ET.SubElement(root, "Programme").text = student.programme
        
        courses_elem = ET.SubElement(root, "Courses")
        for course_name, mark in student.courses.items():
            course = ET.SubElement(courses_elem, "Course")
            ET.SubElement(course, "Name").text = course_name
            ET.SubElement(course, "Mark").text = str(mark)
            
        tree = ET.ElementTree(root)
        tree.write(filename)
        return True
    except Exception as e:
        print(f"Error wrapping to XML: {e}")
        return False

def unwrap_from_xml(filename):
    """Reads an XML file and returns an ITstudent object."""
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        
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
        print(f"Error unwrapping XML {filename}: {e}")
        return None

# --- 5. Main Test Block ---
if __name__ == "__main__":
    print("--- 🧪 Testing Student Generator and XML ---")
    
    # 1. Generate a random student
    print("\n[1] Generating random student...")
    my_student = generate_random_student()
    
    # Use the __str__ method to print it
    print(my_student) 
    
    # 2. Wrap the student to an XML file
    test_filename = "test_student.xml"
    print(f"\n[2] Wrapping student data to {test_filename}...")
    wrap_to_xml(my_student, test_filename)
    print(f"Successfully created {test_filename}.")
    
    # 3. Unwrap the student from the XML file
    print(f"\n[3] Unwrapping {test_filename}...")
    unwrapped_student = unwrap_from_xml(test_filename)
    
    if unwrapped_student:
        print("Successfully read data back from XML:")
        print(unwrapped_student)
    
    # 4. Clean up the test file
    if os.path.exists(test_filename):
        os.remove(test_filename)
        print(f"\n[4] Cleaned up {test_filename}.")