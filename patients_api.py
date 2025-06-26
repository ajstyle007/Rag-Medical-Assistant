from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
from rag_model import ask_question
from mongo_db import load_data, patients_collection

app = FastAPI()

class Patient(BaseModel):

    id : Annotated[str, Field(..., description="Id of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="weight of the patient in kgs")]

    @computed_field()
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2), 2)

        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
        

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', "others"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


@app.get("/")
def hello():
    return {"message" : "Hello World!"}


@app.get("/view")
def view():
    data = load_data()

    return data


@app.get("/health", tags=["System"])
def health_check():
    try:
        data = load_data()  # optional: just to verify file/db access
        return {"status": "ok", "message": "API is healthy", "patients_count": len(data)}
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error", 
            "message": "Something went wrong", 
            "details": str(e)
        })
    

@app.get("/patient/{patient_id}")
def view_patient(patient_id : str = Path(..., description="ID of the patient in the DB", example="P001")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    
    raise HTTPException(status_code=404, detail="patient not found")


@app.get("/sort")
def sort_patients(sort_by : str = Query(..., description="Sort on the basis on Height, Weight or BMI"),
                order: str = Query("desc", description="Sort in asc or desc order")):
    
    valid_fields = ["height", "weight", "bmi"]

    sort_by = sort_by.lower()
    order = order.lower()

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"invalid field select from {valid_fields}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="invalid order select between asc and desc")
    
    data = load_data()

    sort_order = True if order == "desc" else False

    sorted_data = sorted(data.values(), key= lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


@app.post("/create")
def create_patient(patient: Patient):
    if patients_collection.find_one({"id": patient.id}):
        raise HTTPException(status_code=400, detail="Patient already exists")

    patient_dict = patient.model_dump(exclude=["bmi", "verdict"])
    patient_dict["bmi"] = patient.bmi
    patient_dict["verdict"] = patient.verdict

    patients_collection.insert_one(patient_dict)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})


@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    existing_patient = patients_collection.find_one({"id": patient_id})

    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Merge existing data with the update
    updated_fields = patient_update.model_dump(exclude_unset=True)
    existing_patient.update(updated_fields)

    # Ensure 'id' is included for model validation
    existing_patient["id"] = patient_id

    try:
        # Create a new Patient object (auto-computes BMI and verdict)
        patient_obj = Patient(**existing_patient)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid data: {str(e)}")

    # Convert to dict and exclude 'id' before saving
    updated_data = patient_obj.model_dump(exclude={"id"})

    patients_collection.update_one({"id": patient_id}, {"$set": updated_data})

    return JSONResponse(status_code=200, content={"message": "Patient Details Updated"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    result = patients_collection.delete_one({"id": patient_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return JSONResponse(status_code=200, content={"message": "Patient Deleted"})


class Query(BaseModel):
    question : str

@app.post("/ask")
def ask_ques(q: Query):
    try:
        answer = ask_question(q.question)
        return {"query": q.question, "answer": answer}
    except Exception as e:
        return {"error": str(e)}
