import os
import cv2
import numpy as np

def create_dummy_dataset():
    print("Creating simulated fingerprint database...")
    
    # Define 5 dummy students
    students = ['219001111', '219002222', '219003333', '219004444', '219005555']
    
    for student_id in students:
        # Create folder for student
        path = os.path.join('dataset', student_id)
        os.makedirs(path, exist_ok=True)
        
        # Create 5 "fingerprint" images per student
        # (In reality, you would copy real scan files here)
        for i in range(1, 6):
            # Create a random noise image (Simulating a print)
            # In a real project, replace this with actual .bmp or .jpg files
            img = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
            
            # Add some structure (circles) so they aren't just pure noise
            cv2.circle(img, (64, 64), 30, (255, 255, 255), 2)
            
            file_path = os.path.join(path, f'finger_{i}.jpg')
            cv2.imwrite(file_path, img)
            
    print("Database created successfully in 'dataset/' folder.")

if __name__ == "__main__":
    create_dummy_dataset()