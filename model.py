from controller import collection, reservaciones_collection, counters_collection
# import bcrypt # Ya no se usa

#Importamos datetime para manejar fechas 
from datetime import datetime, date

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


#CLASE Y METODOS PARA RESERVACIONES
#Inicializamos la clase
class Reservacion : 
    def __init__(self, nombre_residente, telefono, fecha_evento, servicios_extra=None,
                 estado='activa', estado_pago='pendiente', created_at=None, updated_at=None):
        # Asignar los valores recibidos
        self.id = None
        self.nombre_residente = nombre_residente
        self.telefono = telefono  # Se espera que sea string
        #Para aceptar datetime.date o datetime;
        if isinstance(fecha_evento, str):
            #Intentamos parsear IDO date YYYY-MM-DD o IDO datetime
            fecha_evento = datetime.fromisoformat(fecha_evento)
        self.fecha_evento = fecha_evento if isinstance(fecha_evento, datetime) else datetime.combine(fecha_evento, datetime.min.time())
        self.servicios_extra = servicios_extra or [] #Para aceptar una lista de diccionarios
        self.total = self.calcular_total() #Hacemos el cálculo del total dinámicamente al crear la reservación
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


    #Funcion para calcular el costo total de la reservación
    def calcular_total(self):
        """SUma los costos en servicios_extra y devuelve float."""
        total = 0.0
        for s in (self.servicios_extra or []):
            try:
                total += float(s.get('costo', 0) or 0)
            except Exception: 
                #Si el costo no se puede convertir, lo ignora y registra en 0
                total += 0
        return total
    
    #Funcion para insertar los datos recividos de la vista a la base de datos. 
    def guardar_reservacion(self):
        #Hacemos las validaciones necesarias antes de la incercion 

        #Validamos que la colección esté inicializada
        if reservaciones_collection is None:
            return False, "DB no inicializada"

        # validamos que no existan fechas repetidas antes de insertar
        if reservaciones_collection.find_one({"fecha_evento": self.fecha_evento}):
            return False, "La fecha escogida ya está registrada"

        #Asignamos un nuevo ID
        next_id = get_next_sequence_value("reservacion_id")
        if next_id is None:
            return False, "No se pudo generar un ID."

        """Convertimos la instancia a documento Mongo listo para ser insertado."""
        documento = {
            "id": next_id,
            "nombre_residente": self.nombre_residente,
            "telefono": self.telefono,  # string
            "fecha_evento": self.fecha_evento,
            "servicios_extra": self.servicios_extra,
            "total": self.calcular_total(),
            "estado": self.estado,
            "estado_pago": self.estado_pago,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        try:
            result = reservaciones_collection.insert_one(documento)
            return True, f"Reservacion registrada con _id: {result.inserted_id}"
        except Exception as e:
            return False, f"Error al insertar en DB: {e}"
        
    @staticmethod
    def obtener_por_id(reservacion_id):
        #Obtenemos una reservacion por su ID especifica.
        if reservaciones_collection is None:
            print("Error: DB no inicializada en obtener_por_id")
            return None
            
        reservacion = reservaciones_collection.find_one({"id": reservacion_id})
        if not reservacion:
            print(f"Reservacion no encontrada: {reservacion_id}")
            return False
        
        #Creamos una instancia de Reservacion con los datos obtenidos
        return True, Reservacion(
            nombre_residente=reservacion.get("nombre_residente"),
            telefono=reservacion.get("telefono"),
            fecha_evento=reservacion.get("fecha_evento"),
            servicios_extra=reservacion.get("servicios_extra"),
            estado=reservacion.get("estado"),
            estado_pago=reservacion.get("estado_pago"),
            created_at=reservacion.get("created_at"),
            updated_at=reservacion.get("updated_at")
        )
    

    @staticmethod
    def listar_por_fecha(fecha_inicio=None, fecha_fin=None):
        """Devuelve documentos entre dos fechas/fechas-hora.

        Parámetros aceptados: fecha_inicio, fecha_fin pueden ser:
        - None -> sin límite
        - datetime.datetime
        - datetime.date
        - string en formato ISO date o datetime (ej. '2025-11-15' o '2025-11-15T14:00:00')

        Normaliza fecha_inicio al inicio del día y fecha_fin al fin del día cuando se pasan fechas.
        Retorna (True, [docs]) o (False, mensaje).
        """
        if reservaciones_collection is None:
            return False, "DB no inicializada (listar_por_fecha)"

        def to_dt_edge(v, start=True):
            if v is None:
                return None
            # si ya es datetime
            if isinstance(v, datetime):
                return v
            # si es date (no datetime)
            if isinstance(v, date):
                return datetime.combine(v, datetime.min.time()) if start else datetime.combine(v, datetime.max.time())
            # si es string, intentar parsear
            if isinstance(v, str):
                try:
                    # intenta ISO completa
                    dt = datetime.fromisoformat(v)
                    # si venía solo fecha (sin hora), fromisoformat devuelve date? No, lanzará error; aquí lo manejamos
                    if isinstance(dt, datetime):
                        return dt
                except Exception:
                    # asumir formato 'YYYY-MM-DD'
                    try:
                        d = datetime.fromisoformat(v + 'T00:00:00')
                        return d if start else datetime.fromisoformat(v + 'T23:59:59.999999')
                    except Exception:
                        return None
            return None

        inicio_dt = to_dt_edge(fecha_inicio, start=True)
        fin_dt = to_dt_edge(fecha_fin, start=False)

        q = {}
        if inicio_dt or fin_dt:
            q["fecha_evento"] = {}
            if inicio_dt:
                q["fecha_evento"]["$gte"] = inicio_dt
            if fin_dt:
                q["fecha_evento"]["$lte"] = fin_dt

        try:
            docs = list(reservaciones_collection.find(q).sort([("fecha_evento", 1), ("created_at", 1)]))
            return True, docs
        except Exception as e:
            return False, f"Error al listar reservaciones: {e}"
        

    @staticmethod
    def listar_por_residente(nombre_residente):
        if reservaciones_collection is None:
            return False, "DB no inicializada (reservaciones)"
        try:
            docs = list(reservaciones_collection.find({"nombre_residente": nombre_residente}).sort("fecha_evento", 1))
            return True, docs
        except Exception as e:
            return False, f"Error al listar por residente: {e}"

    @staticmethod
    def obtener_por_id(resv_id):
        if reservaciones_collection is None:
            return None
        return reservaciones_collection.find_one({"id": resv_id})

    @staticmethod
    def cancelar(resv_id):
        if reservaciones_collection is None:
            return False, "DB no inicializada (reservaciones)"
        try:
            res = reservaciones_collection.find_one_and_update(
                {"id": resv_id},
                {"$set": {"estado": "cancelada", "updated_at": datetime.utcnow()}},
                return_document=True
            )
            if res:
                return True, res
            else:
                return False, "Reservación no encontrada"
        except Exception as e:
            return False, f"Error al cancelar: {e}"

    @staticmethod
    def agregar_servicio_extra(resv_id, servicio):
        """
        servicio = {"nombre": str, "costo": float}
        Retorna (True, updated_doc) o (False, mensaje)
        """
        if reservaciones_collection is None:
            return False, "DB no inicializada (reservaciones)"
        try:
            # push servicio y recalcular total manualmente (atomicidad no perfecta sin transacción)
            updated = reservaciones_collection.find_one_and_update(
                {"id": resv_id},
                {
                    "$push": {"servicios_extra": servicio},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                return_document=True
            )
            if not updated:
                return False, "Reservación no encontrada"
            # recalcular total en aplicación y actualizar campo total
            new_total = 0.0
            for s in updated.get("servicios_extra", []):
                try:
                    new_total += float(s.get("costo", 0))
                except Exception:
                    new_total += 0.0
            reservaciones_collection.update_one({"id": resv_id}, {"$set": {"total": new_total, "updated_at": datetime.utcnow()}})
            updated = reservaciones_collection.find_one({"id": resv_id})
            return True, updated
        except Exception as e:
            return False, f"Error al agregar servicio: {e}"