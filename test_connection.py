from connection_mongo import get_mongo_connection

try:
    db = get_mongo_connection()
    print("Conexión exitosa. Colecciones disponibles:", db.list_collection_names())
except Exception as e:
    print("Error al conectar a MongoDB:", str(e))
