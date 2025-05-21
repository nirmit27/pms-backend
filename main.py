"""Root of the service."""

from fastapi import FastAPI, Path, HTTPException, Query

from utils import load_data, valid_fields

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Patient Management System 🏥"}


@app.get("/about")
def about():
    return {"message": "This is a microservice for managing patient records."}


@app.get("/view")
def view():
    data: dict[str, dict[str, str | int | float]] = load_data()
    return data


@app.get("/patient/id/{patient_id}")
def view_patient_by_id(
    patient_id: str = Path(
        ..., description="Patient ID in the database.", example="P001"
    )
):
    data: dict[str, dict[str, str | int | float]] = load_data()

    if patient_id in data:
        return data[patient_id]

    raise HTTPException(
        status_code=404, detail=f"Patient with ID : '{patient_id}' not found."
    )


@app.get("/patient/")
def view_patients_by_name(
    patient_name: str = Query(
        ..., description="Patient name in the database.", example="John Doe"
    )
):
    data: dict[str, dict[str, str | int | float]] = load_data()
    results: list[dict[str, str | int | float]] = []

    for k in data.keys():
        if patient_name in data[k].values():
            results.append(data[k])

    if len(results) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Patient(s) with name : '{patient_name}' not found.",
        )

    return results


@app.get("/sort")
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Sort records on the basis of height, weight or bmi.",
    ),
    order: str = Query("asc", description="Sort in ascending or descending order."),
):
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, detail=f"Invalid sorting field. Select from {valid_fields}."
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail="Invalid sorting order. Select either 'asc' or 'desc'."
        )

    data: dict[str, dict[str, str | int | float]] = load_data()
    sort_order = True if order == "desc" else False

    sorted_data = sorted(
        data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order
    )

    return sorted_data
