import cv2
import os
import numpy as np

# Load Haar cascade downloaded previously
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def process_and_save_face(image_path, criminal_id):
    img = cv2.imread(image_path)
    if img is None:
        return False
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    
    if len(faces) == 0:
        return False
    
    # Save the largest face found
    faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
    x, y, w, h = faces[0]
    face_crop = gray[y:y+h, x:x+w]
    
    os.makedirs('dataset', exist_ok=True)
    cv2.imwrite(f'dataset/{criminal_id}.jpg', face_crop)
    return True

def train_recognizer():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []
    
    if not os.path.exists('dataset'):
        return False
        
    for f in os.listdir('dataset'):
        if f.endswith('.jpg'):
            criminal_id = int(f.split('.')[0])
            img_path = os.path.join('dataset', f)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(img)
                labels.append(criminal_id)
                
    if len(faces) > 0:
        recognizer.train(faces, np.array(labels))
        recognizer.write('trainer.yml')
        return True
    return False

def recognize_face(image_path):
    if not os.path.exists('trainer.yml'):
        return None, 0
        
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')
    
    img = cv2.imread(image_path)
    if img is None:
        return None, 0
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    
    if len(faces) == 0:
        return None, 0
        
    # Process largest face
    faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
    x, y, w, h = faces[0]
    face_crop = gray[y:y+h, x:x+w]
    
    # Predict
    label, confidence = recognizer.predict(face_crop)
    
    # LBPH distance (lower is closer/better).
    # Normally, < 65 is a very good match.
    match_percentage = max(0, 100 - confidence)
    
    if confidence < 75:  
        return label, match_percentage
    return None, 0
