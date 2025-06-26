# mongodb+srv://rag_aj:<db_password>@cluster0.txsdxgr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

from pymongo import MongoClient
import json, os
from urllib.parse import quote_plus

# username = quote_plus("rag_aj")              # escape username
# password = quote_plus("Ajay@1234")           # escape password

mongo_user = os.getenv("MONGO_USERNAME")
mongo_pass = os.getenv("MONGO_PASSWORD")
mongo_uri_template = os.getenv("MONGO_URI_TEMPLATE")

# Encode username and password safely
encoded_user = quote_plus(mongo_user)
encoded_pass = quote_plus(mongo_pass)

# Replace in URI template
mongo_uri = mongo_uri_template.format(username=encoded_user, password=encoded_pass)

# Paste your connection URI here
# MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.txsdxgr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a client
client = MongoClient(mongo_uri)

# Choose your database name
db = client["rag_medical_bot"]

# Choose your collection name
patients_collection = db["patients"]

# Load data from JSON file
# with open("indian_patients.json", "r") as f:
#     data = json.load(f)

# Insert each patient
# for patient_id, patient_info in data.items():
#     patient_info["id"] = patient_id  # add id field inside the object
#     patients_collection.insert_one(patient_info)

# print("✅ All patients inserted successfully!")


# def load_data():
#     data = {}
#     for doc in patients_collection.find():
#         patient_id = doc.get("id")
#         if patient_id:
#             # Remove MongoDB’s internal _id field
#             doc.pop("_id", None)
#             data[patient_id] = doc
#     return data



def load_data():
    data = {}
    for doc in patients_collection.find():
        patient_id = doc.get("id")
        if patient_id:
            # Remove MongoDB’s internal _id field
            doc.pop("_id", None)
            data[patient_id] = {
            "id": doc.get("id"),
            "name": doc.get("name"),
            "city": doc.get("city"),
            "age": doc.get("age"),
            "gender": doc.get("gender"),
            "height": doc.get("height"),
            "weight": doc.get("weight"),
            "bmi": doc.get("bmi"),
            "verdict": doc.get("verdict")
        }
    return data
