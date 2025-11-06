from controller import collection, counters_collection
# import bcrypt # Ya no se usa

def get_next_sequence_value(sequence_name):
    if counters_collection is None:
        return None

    sequence_document = counters_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        upsert=True, 
        return_document=True
    )
    # Asegurarnos que el documento y el valor existen
    if sequence_document:
        return sequence_document.get('sequence_value')
    
    # Si es la primera vez, el valor inicial será 1
    counters_collection.insert_one({'_id': sequence_name, 'sequence_value': 1})
    return 1


class Usuario:
    def __init__(self, nombre, email, telefono, password, username, rol="dueño",
                 condominio_id=None, apellido_paterno=None, apellido_materno=None, 
                 rfc=None, nss=None, imagen=None, imagen_INE=None, 
                 modelo_de_auto=None, color=None, placas=None):
        
        # Asignar los valores recibidos
        self.condominio_id = condominio_id
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.telefono = telefono # Se espera que sea string
        self.rfc = rfc
        self.nss = nss
        self.email = email
        self.imagen = imagen
        self.imagen_INE = imagen_INE
        self.modelo_de_auto = modelo_de_auto
        self.color = color
        self.placas = placas
        self.username = username
        self.password = password
        self.rol = rol

    def registrar_usuario(self):
        if collection is None:
            return False, "DB no inicializada"

        # validar existencia de email/username antes de insertar
        if collection.find_one({"email": self.email}) or collection.find_one({"username": self.username}):
            return False, "Email o username ya registrado"

        # --- INICIO CAMBIO: Quitando BCRYPT ---
        # ADVERTENCIA: Guardar contraseñas en texto plano es muy inseguro.
        # hashed = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        password_a_guardar = self.password # Contraseña en texto plano
        # --- FIN CAMBIO ---
        
        next_id = get_next_sequence_value("usuarioid")
        if next_id is None:
            return False, "No se pudo generar un ID."

        documento = {
            "id": next_id,
            "condominio_id": self.condominio_id,
            "nombre": self.nombre,
            "apellido_materno": self.apellido_materno,
            "apellido_paterno": self.apellido_paterno,
            "telefono": self.telefono,  # string
            "rfc": self.rfc,
            "nss": self.nss,
            "email": self.email,
            "imagen": self.imagen,
            "imagen_INE": self.imagen_INE,
            "modelo_de_auto": self.modelo_de_auto,
            "color": self.color,
            "placas": self.placas,
            "username": self.username,
            "password": password_a_guardar, # Se guarda la contraseña en texto plano
            "rol": self.rol
        }
        
        try:
            user_id = collection.insert_one(documento).inserted_id
            return True, f"Usuario registrado con _id: {user_id}"
        except Exception as e:
            return False, f"Error al insertar en DB: {e}"

    @staticmethod
    def verificar_usuario(email_or_username, password):
        if collection is None:
            print("Error: DB no inicializada en verificar_usuario")
            return False
            
        # buscar por email o username
        q = {"$or": [{"email": email_or_username}, {"username": email_or_username}]}
        user = collection.find_one(q)
        
        if not user:
            print(f"Usuario no encontrado: {email_or_username}")
            return False
            
        stored = user.get("password")
        
        if not stored:
            print(f"Usuario {email_or_username} no tiene contraseña en DB.")
            return False
        
        # --- INICIO CAMBIO: Quitando BCRYPT ---
        # Comparación simple de texto plano.
        es_valido = password == stored
        if not es_valido:
            print(f"Contraseña incorrecta para {email_or_username}")
            
        return es_valido
        # --- FIN CAMBIO ---
