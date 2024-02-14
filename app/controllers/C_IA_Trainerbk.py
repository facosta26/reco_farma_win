import os
import joblib
import cv2
from flask import Blueprint, json, render_template
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import dlib
from app.controllers.C_People import C_People

from app.forms.F_Trainer import F_Trainer
from app.models.Models import People

class CustomSVM:
    def __init__(self):
        self.model = svm.SVC(kernel='linear')
        self.le = preprocessing.LabelEncoder()

    def train(self, X, y):
        # Codificar etiquetas
        y_encoded = self.le.fit_transform(y)

        # Si hay menos de dos muestras, no dividir los datos
        if len(np.unique(y_encoded)) < 2:
            print("Menos de dos clases, no se puede dividir el conjunto de datos.")
            self.model.fit(X, y_encoded)
        else:
            # Dividir los datos en conjuntos de entrenamiento y prueba
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42)

            # Entrenar el modelo
            self.model.fit(X_train, y_train)

            # Evaluar el modelo
            accuracy = self.model.score(X_test, y_test)
            print(f'Accuracy: {accuracy}')
            
    def save_model(self, file_path):
        # Guardar el modelo y el codificador de etiquetas
        joblib.dump({'model': self.model, 'le': self.le}, file_path)

    def load_model(self, file_path):
        # Cargar el modelo y el codificador de etiquetas
        data = joblib.load(file_path)
        self.model = data['model']
        self.le = data['le']

    def predict(self, img):
        # Preprocesar la imagen
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (64, 64))
        img = img.astype(np.float32) / 255.0
        img = img.reshape(-1, 64 * 64 * 3)

        # Realizar la predicción
        prediction = self.model.predict(img)
        predicted_label = self.le.inverse_transform(prediction)[0]

        return predicted_label


class C_IA_Trainer():
    ia = Blueprint('ia', __name__)

    @ia.route('/ia_trainer')
    def ia_trainer():
        form = F_Trainer()
        return render_template('v_ia_trainer.html', title="Entrenamiento de Modelo de IA", form=form)

    @ia.route('/train', methods=['POST'])
    def train():
        message = {"correcto": '', "alerta": '', "error": ''}
        C_IA_Trainer.train_model()
        message['correcto'] = "Se ha entrenado correctamente, se ha generado un nuevo modelo de apredizaje con los nuevos datos que se recabaron"
        return json.dumps(message)


    def train_model():
        # Obtener una lista de los directorios en el directorio `static/uploads`
        directories = os.listdir('app/static/uploads/people_photo')

        # Crear listas para almacenar las imágenes y sus etiquetas
        X = []
        y = []

        # Leer las imágenes y sus etiquetas
        for directory in directories:
            # Obtener las imágenes en el directorio
            files = os.listdir(f'app/static/uploads/people_photo/{directory}')
            # Leer las imágenes y sus etiquetas
            for file in files:
                # Obtener la imagen
                img = cv2.imread(
                    f'app/static/uploads/people_photo/{directory}/{file}')

                # Convertir la imagen a un vector y agregar a X
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (64, 64))
                img = img.astype(np.float32) / 255.0
                img = img.reshape(-1, 64 * 64 * 3)
                X.append(img)

                # Agregar la etiqueta a y
                y.append(directory)

        # Convertir las listas a arreglos numpy
        X = np.concatenate(X)
        y = np.array(y)

        # Entrenar el modelo SVM
        custom_svm = CustomSVM()
        custom_svm.train(X, y)

        # Guardar el modelo entrenado
        custom_svm.save_model('model_weights.joblib')

    @ia.route('/identify', methods=['POST'])
    def identify():
        message = {"correcto": '', "alerta": '', "error": ''}
        prediction = C_IA_Trainer.identify_person()
        print("Prediccion: {}".format(prediction))
        person_data = People.query.filter_by(peop_dni = prediction).first()
        if person_data is not None:
            message['correcto'] = "La persona identificada mediante la cámara es {}".format(person_data.peop_names+' '+person_data.peop_lastnames)
            message['cod'] = person_data.peop_id
            message['name'] = person_data.peop_names+' '+person_data.peop_lastnames
            message['dni'] = person_data.peop_dni
            message['age'] = C_People.calcular_edad(person_data.peop_birthdate)
            message['birthdate'] = person_data.peop_birthdate.strftime("%d/%m/%Y")
            message['gender'] = "MASCULINO" if person_data.peop_gender == 'M' else 'FEMENINO'
        else:
            message['alerta'] = prediction
        return json.dumps(message)

    def identify_person():
        # Inicializar el detector de caras de dlib
        face_detector = dlib.get_frontal_face_detector()

        # Obtener una imagen de la webcam
        cap = cv2.VideoCapture(0)
        ret, webcam_img = cap.read()

        # Cargar el modelo con joblib
        custom_svm = CustomSVM()
        custom_svm.load_model('model_weights.joblib')

        # Convertir la imagen de la webcam a escala de grises para el detector de caras
        gray_webcam_img = cv2.cvtColor(webcam_img, cv2.COLOR_BGR2GRAY)

        # Detectar caras en la imagen de la webcam
        faces = face_detector(gray_webcam_img)

        if not faces:
            return "No se detectaron caras frente a la cámara"

        # Tomar la primera cara detectada
        face = faces[0]

        # Ajustar las coordenadas de la cara para capturar un área más grande
        x, y, w, h = face.left() - 15, face.top() - 15, face.width() + \
            30, face.height() + 30

        # Asegurar que las coordenadas no sean negativas
        x, y = max(x, 0), max(y, 0)

        # Recortar la cara de la imagen de la webcam
        cropped_webcam_img = webcam_img[y:y+h, x:x+w]

        # Predecir la etiqueta de la cara recortada
        prediction = custom_svm.predict(cropped_webcam_img)

        # Verificar si la predicción es desconocida
        if prediction == "unknown":
            return "Persona desconocida"

        # Devolver la etiqueta
        return prediction
