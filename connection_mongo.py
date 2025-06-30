from pymongo import MongoClient

def get_mongo_connection():
    uri = "mongodb+srv://catequesis:Flask123@catequesisg9.yjesiot.mongodb.net/?retryWrites=true&w=majority&appName=CatequesisG9"
    client = MongoClient(uri)
    db = client["CatequesisG9"]
    return db
