import os
import cv2
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
import joblib

def train_system():
    X = [] # Features (Image data)
    y = [] # Labels (Student IDs)
    
    print("Loading dataset...")
    
    # Loop through the 'dataset' folder
    if not os.path.exists('dataset'):
        print("Error: 'dataset' folder not found. Run create_dummy_db.py first.")
        return

    for student_id in os.listdir('dataset'):
        student_folder = os.path.join('dataset', student_id)
        
        if os.path.isdir(student_folder):
            for image_name in os.listdir(student_folder):
                image_path = os.path.join(student_folder, image_name)
                
                # Read image in grayscale
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                
                # Resize to standard size
                img = cv2.resize(img, (312, 372))
                
                # Flatten image to 1D array (16384 features)
                img_flat = img.flatten()
                
                X.append(img_flat)
                y.append(student_id)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Loaded {len(X)} images for {len(set(y))} students.")
    
    # Split data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training SVM Model...")
    # Create SVM model
    model = svm.SVC(kernel='rbf', gamma='scale', probability=True)
    model.fit(X_train, y_train)
    
    # Save the model to disk
    joblib.dump(model, 'svm_fingerprint_model.pkl')
    print("Model saved as 'svm_fingerprint_model.pkl'")
    
    # Calculate Accuracy
    acc = model.score(X_test, y_test)
    print(f"Model Accuracy: {acc * 100:.2f}%")

if __name__ == "__main__":
    train_system()