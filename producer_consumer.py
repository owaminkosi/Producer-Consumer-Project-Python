import threading
import time
import random
import os

# Import all our functions from the first file
from student_handler import ITstudent, generate_random_student, wrap_to_xml, unwrap_from_xml

# --- 1. Shared State and Constants ---
MAX_SIZE = 10
XML_DIR = "student_xmls"  # A dedicated folder for our XML files

# The shared buffer that holds the file numbers (1-10)
buffer = [] 

# The three key synchronization primitives
mutex = threading.Lock() # For Rule 3: Mutual Exclusion
empty_slots = threading.Semaphore(MAX_SIZE) # For Rule 1: Producer waits if full
full_slots = threading.Semaphore(0)        # For Rule 2: Consumer waits if empty

# --- 2. The Producer Thread Function ---
def producer():
    """
    Generates a student, wraps to XML, and adds the file number to the buffer.
    """
    file_number = 1
    
    while True:
        # --- Produce Item (outside the lock) ---
        # Generate a new student. This is the "work".
        student = generate_random_student()
        
        # --- Wait for an empty slot ---
        # This blocks if the buffer is full (empty_slots count is 0)
        empty_slots.acquire()
        
        # --- Acquire lock for exclusive buffer access ---
        mutex.acquire()
        
        # --- START CRITICAL SECTION ---
        # We now have exclusive access to the buffer
        filename = f"student{file_number}.xml"
        filepath = os.path.join(XML_DIR, filename)
        
        # Wrap student to XML file
        wrap_to_xml(student, filepath)
        
        # Add the *integer* to the buffer
        buffer.append(file_number)
        
        print(f"✅ Producer: Created {filename}. Buffer: {buffer}")
        
        # Update file number to loop 1-10
        file_number = (file_number % 10) + 1
        # --- END CRITICAL SECTION ---
        
        # --- Release lock and signal consumer ---
        mutex.release()
        
        # Signal that a slot is now full
        full_slots.release()
        
        # Simulate time taken to produce
        time.sleep(random.uniform(0.5, 2))

# --- 3. The Consumer Thread Function ---
def consumer():
    """
    Reads a file number from the buffer, unwraps XML, prints info, and deletes file.
    """
    while True:
        # --- Wait for a full slot ---
        # This blocks if the buffer is empty (full_slots count is 0)
        full_slots.acquire()
        
        # --- Acquire lock for exclusive buffer access ---
        mutex.acquire()
        
        # --- START CRITICAL SECTION ---
        # We now have exclusive access to the buffer
        
        # Get the file number from the buffer
        file_number = buffer.pop(0) # Remove from the front
        
        filename = f"student{file_number}.xml"
        filepath = os.path.join(XML_DIR, filename)
        
        print(f"🔴 Consumer: Reading {filename}. Buffer: {buffer}")
        # --- END CRITICAL SECTION ---
        
        # --- Release lock and signal producer ---
        mutex.release()
        
        # Signal that a slot is now empty
        empty_slots.release()
        
        # --- Process Item (outside the lock) ---
        # This is the "work". We do it outside the lock so the
        # producer isn't blocked by the consumer's work.
        
        student = unwrap_from_xml(filepath)
        
        if student:
            # Print all the student's info (uses the __str__ method)
            print(student)
            
            # Clean up the file as required
            try:
                os.remove(filepath)
                print(f"🗑️ Consumer: Processed and deleted {filename}.\n")
            except OSError as e:
                print(f"Error deleting file {filepath}: {e}")
        
        # Simulate time taken to consume and process
        time.sleep(random.uniform(1, 4))

# --- 4. Main script execution ---
if __name__ == "__main__":
    print("--- 🚀 Starting Producer-Consumer Simulation ---")
    
    # Create the directory for XML files if it doesn't exist
    os.makedirs(XML_DIR, exist_ok=True)
    print(f"XML files will be stored in: {os.path.abspath(XML_DIR)}")
    
    # Create the threads
    # daemon=True means the threads will stop when the main program stops
    p_thread = threading.Thread(target=producer, daemon=True)
    c_thread = threading.Thread(target=consumer, daemon=True)

    # Start the threads
    p_thread.start()
    c_thread.start()
    
    print("--- Threads are running. Press Ctrl+C to stop. ---")
    
    # Keep the main thread alive to let daemons run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- 🛑 Shutting down simulation ---")