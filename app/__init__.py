import base64
from datetime import date
import os
from flask import Flask, Response,redirect, send_from_directory, session,url_for,render_template,request
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.config import config
from app.controllers.C_Doctors import C_Doctors
from app.controllers.C_IA_Trainer import CustomSVM
from app.controllers.C_IA_Trainerbk import C_IA_Trainer
from app.controllers.C_Login import C_Login
from app.controllers.C_Maintenance import C_Maintenance
from app.controllers.C_People import C_People
from app.controllers.C_Pharma import C_Pharma
from app.controllers.C_Reports import C_Reports
from app.controllers.C_Users import C_Users
from app.models.Models import Users, db
from flask_socketio import SocketIO
from flask_qrcode import QRcode
import cv2
import dlib
import numpy as np
csrf = CSRFProtect()
qrcode = QRcode()
def create_app():
    app=Flask(__name__)
    app.config.from_object(config)
    migrate = Migrate(app, db)
    socketio = SocketIO(app)
    login = C_Login
    users = C_Users
    people = C_People
    doctors = C_Doctors
    ia = C_IA_Trainer
    pharma = C_Pharma
    maintenance = C_Maintenance
    report = C_Reports
    db.init_app(app)
    migrate.init_app(app)
    csrf.init_app(app)
    qrcode.init_app(app)
    app.register_blueprint(login.login)
    app.register_blueprint(users.usuarios)
    app.register_blueprint(people.peop)
    app.register_blueprint(ia.ia)
    app.register_blueprint(doctors.doctors)
    app.register_blueprint(pharma.pharma)
    app.register_blueprint(maintenance.maint)
    app.register_blueprint(report.report)
    face_detector = dlib.get_frontal_face_detector()
    @app.template_filter()
    def imagen_a_base64(ruta_imagen):
        with open(ruta_imagen, "rb") as imagen_archivo:
            # Lee el contenido de la imagen en bytes
            imagen_bytes = imagen_archivo.read()

            # Codifica los bytes en base64
            imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")

        return imagen_base64

    app.jinja_env.filters['base64'] = imagen_a_base64

    @app.template_filter()
    def calcular_edad(fecha_nacimiento):
        # Obtiene la fecha de hoy
        fecha_hoy = date.today()

        # Obtiene la diferencia de años entre las dos fechas
        diferencia_de_anios = fecha_hoy.year - fecha_nacimiento.year

        # Verifica si la fecha de hoy es menor que la fecha de nacimiento
        if fecha_hoy < fecha_nacimiento:
            # La fecha de hoy aún no ha llegado, por lo que la edad es la diferencia de años menos 1
            edad = diferencia_de_anios - 1
        else:
            # La fecha de hoy ya ha llegado, por lo que la edad es la diferencia de años
            edad = diferencia_de_anios

        # Verifica si la fecha de hoy es menor que la fecha de nacimiento
        if fecha_hoy.month < fecha_nacimiento.month:
            # La fecha de hoy aún no ha llegado al mes de cumpleaños, por lo que la edad es la diferencia de años menos 1
            edad = edad - 1
        elif fecha_hoy.day < fecha_nacimiento.day:
            # La fecha de hoy aún no ha llegado al día de cumpleaños, por lo que la edad es la diferencia de años menos 1
            edad = edad - 1
        return edad


    app.jinja_env.filters['base64'] = calcular_edad
    
    @app.route('/img/<filename>')
    def img(filename):
        return send_from_directory('/app/static/img', filename)

    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login.index'))
    
    def generate_frames():
        camera = cv2.VideoCapture(0)  # 0 para la cámara predeterminada
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
        while True:
            success, frame = camera.read()
            if not success:
                break

            # Convertir el marco a escala de grises para la detección de rostros
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detectar rostros en la imagen
            faces = face_detector(gray_frame)

            for face in faces:
                x, y, w, h = face.left(), face.top(), face.width(), face.height()

                # Dibujar un rectángulo alrededor del rostro
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # Extraer la región de interés (ROI) que contiene el rostro
                roi = frame[y:y+h, x:x+w]

                gray_webcam_img = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                faces = face_detector(gray_webcam_img)

                if not faces:
                    print("No se detectaron caras frente a la cámara")
                    continue

                face = faces[0]
                shape = predictor(gray_webcam_img, face)

                x, y, w, h = shape.rect.left() - 15, shape.rect.top() - 15, shape.rect.width() + 30, shape.rect.height() + 30
                x, y = max(x, 0), max(y, 0)

                cropped_webcam_img = frame[y:y+h, x:x+w]

                custom_svm = CustomSVM()
                custom_svm.load_model('model_weights.joblib')

                prediction = custom_svm.predict(cropped_webcam_img)

                if prediction == "unknown":
                    print("Persona desconocida")
                    socketio.emit('recognized', {'label': "desconocido"})
                else:
                    print(f"Persona identificada: {prediction}")
                    camera.release()
                    socketio.emit('recognized', {'label': prediction})

            # Codificar la imagen como JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        camera.release()


    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/capture')
    def capture():
        camera = cv2.VideoCapture(0)
        success, frame = camera.read()
        if success:
            filename = 'captured_photo.jpg'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            cv2.imwrite(filepath, frame)
            camera.release()
            return f'Captura exitosa. Imagen guardada como {filename} en {app.config["UPLOAD_FOLDER"]}'
        else:
            camera.release()
            return 'Error al capturar la imagen'
    
    return app, socketio

