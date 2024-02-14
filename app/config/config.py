from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_ECHO = True
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/static/uploads')
WKHTMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
