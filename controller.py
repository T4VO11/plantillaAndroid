import pymongo
import flet as ft

uri = "mongodb+srv://gdltech:gdltech12345@cluster0.7lopmuz.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "condominios"
COLLECTION_NAME = "usuarios"

try:
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000) # Timeout de 5 seg
    db = client[DATABASE_NAME]
    # 'collection' hará referencia a la colección de usuarios
    collection = db[COLLECTION_NAME]
    counters_collection = db["counters"]

    #Agregamos la colección 'reservaciones' para hacer los apartados de amenidades. 
    #De esta manera en el 'model.py' podremos hacer uso de esta colección.
    reservaciones_collection = db["reservaciones"] if db is not None else None
    
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
from model import Reservacion, Usuario

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


    #Metodos para reservaciones para la vista
    def crear_reservacion(self, nombre_residente, telefono, fecha_evento, servicios_extra=None):
        from model import Reservacion, get_next_sequence_value
        r = Reservacion(nombre_residente, telefono, fecha_evento, servicios_extra=servicios_extra)
        exito, resultado = r.crear(get_next_sequence_value)
        return exito, resultado

    def listar_reservaciones_por_residente(self, nombre_residente):
        from model import Reservacion
        return Reservacion.listar_por_residente(nombre_residente)

    def cancelar_reservacion(self, reservacion_id):
        from model import Reservacion
        return Reservacion.cancelar(reservacion_id)
    

""" EJEMPLOS PARA BUSCAR EVENTOS EN UNA FECHA ESPECIFICA
from datetime import datetime, timedelta
fecha = datetime(2025, 11, 15)
inicio = datetime.combine(fecha.date(), datetime.min.time())
fin = datetime.combine(fecha.date(), datetime.max.time())
ok, docs = Reservacion.listar_por_fecha(inicio, fin)
"""