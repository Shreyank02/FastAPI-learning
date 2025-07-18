from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()


def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data, f)


@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get("/about")
def about():
    return {'message':'A fully functional api to manage your patient records'}

@app.get("/view")
def view():
    data = load_data()
    return data

#path parameters
@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description='id of the patient in the db', example='P002')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')

#query parameter
@app.get('/sort')
def sorting(sort_by: str = Query(..., description='Sort by basis of height, weight or bmi'),
            order: str = Query('asc',description='sort in ascending of descinding order')):
    
    valid_fields = ['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail='invalid field in select from {valid_fields}')
    
    if order not in ['asc','dsc']:
        raise HTTPException(status_code=400, detail='invalid field in select from asc or dsc')
    
    data = load_data()

    sort_order = True if order=='dsc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


#pydantic class for post
class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient',example=['P001'])]
    name: Annotated[str, Field(...,description='name of patient')]
    city: Annotated[str, Field(...,description='city of patient')]
    age: Annotated[int, Field(...,description='age of the patient')]
    gender: Annotated[Literal['male','female','other'], Field(...,description='gender of the patient')]
    height: Annotated[float, Field(...,description='height of the patient in meters')]
    weight: Annotated[float, Field(...,description='weight of the patient in meters')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight/self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        
@app.post("/create")
def create_patient(patient : Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail='patient already exists')

    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})


#pydantic class for put
class Patient_update(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    gender: Annotated[Optional[Literal['male','female','other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None)]
    weight: Annotated[Optional[float], Field(default=None)]

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: Patient_update):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail='patient not found')
    
    existing_info = data[patient_id]
    
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items():
        existing_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_info)
    #-> pydantic object -> dict
    existing_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'Patient deleted'})

