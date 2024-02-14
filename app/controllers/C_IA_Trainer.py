import os
from flask import Blueprint, Response, render_template, json, jsonify
from flask import current_app as app
import cv2
import dlib
import numpy as np
from app.controllers.C_People import C_People
from app.forms.F_Trainer import F_Trainer
from app.models.Models import People
from sklearn import preprocessing
from sklearn import svm
from sklearn.model_selection import train_test_split
import joblib

from app.utils.utils import check_role
class CustomSVM:
    def __init__(self):
        self.model = svm.SVC(kernel='linear')
        self.le = preprocessing.LabelEncoder()

    def train(self, X, y):
        y_encoded = self.le.fit_transform(y)

        if len(np.unique(y_encoded)) < 2:
            print("Menos de dos clases, no se puede dividir el conjunto de datos.")
            self.model.fit(X, y_encoded)
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42)

            self.model.fit(X_train, y_train)
            accuracy = self.model.score(X_test, y_test)
            print(f'Accuracy: {accuracy}')

    def save_model(self, file_path):
        joblib.dump({'model': self.model, 'le': self.le}, file_path)

    def load_model(self, file_path):
        data = joblib.load(file_path)
        self.model = data['model']
        self.le = data['le']

    def predict(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (64, 64))
        img = img.astype(np.float32) / 255.0
        img = img.reshape(-1, 64 * 64 * 3)
        prediction = self.model.predict(img)
        predicted_label = self.le.inverse_transform(prediction)[0]

        return predicted_label

class C_IA_Trainer():
    ia = Blueprint('ia', __name__)
    
    @ia.route('/identify', methods=['POST'])
    @check_role(['ADMINISTRADOR', 'MEDICO', 'FARMACEUTICO'])
    def identify():
        message = {"correcto": '', "alerta": '', "error": ''}
        try:
            prediction = C_IA_Trainer.identify_person()
            person_data = People.query.filter_by(peop_dni=prediction).first()

            if person_data is not None:
                message['correcto'] = "La persona identificada mediante la cámara es {}".format(
                    person_data.peop_names+' '+person_data.peop_lastnames)
                message['cod'] = person_data.peop_id
                message['name'] = person_data.peop_names+' ' + \
                    person_data.peop_lastnames
                message['dni'] = person_data.peop_dni
                message['age'] = C_People.calcular_edad(
                    person_data.peop_birthdate)
                message['birthdate'] = person_data.peop_birthdate.strftime("%d/%m/%Y")
                message['gender'] = "MASCULINO" if person_data.peop_gender == 'M' else 'FEMENINO'
            else:
                message['alerta'] = prediction

        except Exception as e:
            message['error'] = str(e)

        return jsonify(message)


    def identify_person():
        face_detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(
            "shape_predictor_68_face_landmarks.dat")
        cap = cv2.VideoCapture(0)

        try:
            _, webcam_img = cap.read()

            gray_webcam_img = cv2.cvtColor(webcam_img, cv2.COLOR_BGR2GRAY)
            faces = face_detector(gray_webcam_img)

            if not faces:
                return "No se detectaron caras frente a la cámara"

            face = faces[0]
            shape = predictor(gray_webcam_img, face)

            x, y, w, h = shape.rect.left() - 15, shape.rect.top() - 15, shape.rect.width() + 30, shape.rect.height() + 30
            x, y = max(x, 0), max(y, 0)

            cropped_webcam_img = webcam_img[y:y+h, x:x+w]

            custom_svm = CustomSVM()
            custom_svm.load_model('model_weights.joblib')

            prediction = custom_svm.predict(cropped_webcam_img)

            if prediction == "unknown":
                return "Persona desconocida"

            return prediction
        except Exception as e:
            raise RuntimeError(f"Error al capturar la imagen de la webcam: {e}")
        finally:
            cap.release()


    @ia.route('/train', methods=['POST'])
    @check_role(['ADMINISTRADOR'])
    def train():
        message = {"correcto": '', "alerta": '', "error": ''}
        try:
            C_IA_Trainer.train_model()
            message['correcto'] = "Se ha entrenado correctamente, se ha generado un nuevo modelo de apredizaje con los nuevos datos que se recabaron"
        except Exception as e:
            message['error'] = str(e)
        return json.dumps(message)


    def train_model():
        directories = os.listdir('app/static/uploads/people_photo')
        X = []
        y = []

        for directory in directories:
            files = os.listdir(f'app/static/uploads/people_photo/{directory}')
            for file in files:
                img = cv2.imread(
                    f'app/static/uploads/people_photo/{directory}/{file}')

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (64, 64))
                img = img.astype(np.float32) / 255.0
                img = img.reshape(-1, 64 * 64 * 3)
                X.append(img)

                y.append(directory)

        X = np.concatenate(X)
        y = np.array(y)

        custom_svm = CustomSVM()
        custom_svm.train(X, y)
        custom_svm.save_model('model_weights.joblib')


    @ia.route('/ia_trainer')
    @check_role(['ADMINISTRADOR'])
    def ia_trainer():
        form = F_Trainer()
        return render_template('v_ia_trainer.html', title="Entrenamiento de Modelo de IA", form=form)

    