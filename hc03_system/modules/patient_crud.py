from hc03_system.db import db
from bson import ObjectId

async def create_patient(patient: dict):
    result = await db.patients.insert_one(patient)
    return str(result.inserted_id)

async def get_patient(patient_id: str):
    return await db.patients.find_one({"_id": ObjectId(patient_id)})
