import pymongo
import flet as ft

uri = "mongodb+srv://gdltech:gdltech12345@cluster0.7lopmuz.mongodb.net/?appName=Cluster0&retryWrites=true&w=majority"
DATABASE_NAME = "condominios"
COLLECTION_NAME = "usuarios"

try:
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000) # Timeout de 5 seg
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    counters_collection = db["counters"]
    client.admin.command('ping')
    print("Conexión a MongoDB Atlas exitosa.")
except pymongo.errors.ConnectionFailure as e:
    print(f"No se pudo conectar a MongoDB: {e}")
    client = None
    db = None
    collection = None
    counters_collection = None
except Exception as e:
    print(f"Ocurrió un error en la conexión a DB: {e}")
    client = None
    db = None
    collection = None
    counters_collection = None

# Importar después de inicializar la DB para evitar que model.py falle
from model import Usuario

class Controlador:
    def __init__(self, page: ft.Page):
        self.page = page

    def handle_login(self, correo_input, password_input):
        if not correo_input or not password_input:
            print("Error: Correo y contraseña no pueden estar vacíos.")
            # Aquí deberías mostrar un error en la UI, no solo en consola
            return
        
        if Usuario.verificar_usuario(correo_input, password_input):
            print("Inicio de sesión exitoso.")
            from home import Homevista # Importación local para evitar ciclos
            self.page.clean()
            Homevista(self.page) # Asumiendo que Homevista es una clase
        else:
            print("Error: Correo o contraseña incorrectos.")
            # Aquí deberías mostrar un error en la UI

    def handle_registro(self, nombre_input, correo_input, telefono_input, password_input):
        if not all([nombre_input, correo_input, telefono_input, password_input]):
            print("Error: Todos los campos son obligatorios.")
            # Mostrar error en la UI
            return
        

        nuevo_usuario = Usuario(
            nombre=nombre_input, 
            email=correo_input, 
            telefono=telefono_input, # Pasamos el string
            password=password_input,
            username=correo_input  # Usamos el email como username
        )
        exito, mensaje = nuevo_usuario.registrar_usuario()

        if exito:
            print(mensaje)
            from login import Loginvista # Importación local
            self.page.clean()
            Loginvista(self.page) # Asumiendo que Loginvista es una clase
        else:
            print(f"Error en el registro: {mensaje}")
            # Mostrar error en la UI
    
    def logout(self):
        from login import Loginvista # Importación local
        self.page.clean()
        Loginvista(self.page)
