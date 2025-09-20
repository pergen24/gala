import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://pergentino:098765@db:5432/gala'
    )

    # Carpeta para subir recibos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')

    # Configuración de correo (Gmail con App Password)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "membilambasipergentino@gmail.com"
    MAIL_PASSWORD = "euwnlfxmgfcpseeh"  # App Password de 16 caracteres
    MAIL_DEFAULT_SENDER = ("Gala Tickets", "membilambasipergentino@gmail.com")
#    SERVER_NAME = "192.168.1.11:5000"

