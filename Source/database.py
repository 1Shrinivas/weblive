from pymongo import MongoClient

Mongo_client = MongoClient('mongodb+srv://puneetgani:puneetgani@quentdb.04y5a6m.mongodb.net/test')
database = Mongo_client['Chest']
Chest_Data_collection = database["chest_data"]
