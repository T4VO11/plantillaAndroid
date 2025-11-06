# import pymongo
# import flet as ft


# uri = "mongodb+srv://gdltech:gdltech12345@cluster0.7lopmuz.mongodb.net/?appName=Cluster0"
# DATABASE_NAME = "condominios"
# COLLECTION_NAME = "usuarios"

# try: 
#     client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000) # Timeout de 5 seg
#     db = client[DATABASE_NAME]
#     collection = db[COLLECTION_NAME]
#     counters_collection = db["counters"]
#     client.admin.command('ping')
#     print("Conexión a MongoDB Atlas exitosa.")