from typing import List

from fastapi import HTTPException, APIRouter

from main import app
from models.data_access_schemas import SideEffectCreate, SideEffectRead, SideEffectUpdate, SideEffectDelete
from operation.data_access_operations import DataAccessOperations

# API router
router = APIRouter()
data_access_operations = DataAccessOperations()


# Create Side Effect
# Returns flag indicating creation status. NOTE: Can return a POPO with side effect data as well.
@app.post("/side_effects/", response_model=bool)
async def create_side_effect(data_to_insert: SideEffectCreate):
    result = data_access_operations.insert_side_effect(incoming_side_effect=data_to_insert)

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to insert side effect for user: {data_to_insert.user_id}"
        )

    return True


# Read Side Effect for a user
# Returns all side effect data for a user id.
@app.get("/side_effects/{user_id}", response_model=List[SideEffectRead])
async def read_side_effect_for_user(user_id: str):
    if not user_id or not user_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Incoming user id is malformed"
        )

    result = data_access_operations.read_side_effects_for_user(user_id=user_id)
    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to retrieve side effect for user: {user_id}"
        )

    return result.result_data


# Read Side Effect for a Medication
# Returns all side effect data for a medication id.
@app.get("/side_effects/{medication_id}", response_model=List[SideEffectRead])
async def read_side_effect_for_medication(medication_id: str):
    if not medication_id or not medication_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Incoming medication id is malformed"
        )

    result = data_access_operations.read_side_effects_for_medication(medication_id=medication_id)
    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to retrieve side effect for medication id: {medication_id}"
        )

    return result.result_data


# Delete Side Effect
# Returns id of side effect deleted
# NOTE: How will downstream know the side effect id ? Isnt that internal ? Should we rather add delete_side_effect_for_user
# and delete_side_effect_for_medication ??
@app.delete("/side_effects/{side_effect_id}", response_model=SideEffectDelete)
async def delete_side_effect(side_effect_id: int):
    result = data_access_operations.delete_side_effect(side_effect_id=side_effect_id)

    if result.success:
        return SideEffectDelete(side_effect_id=side_effect_id)
    else:
        return SideEffectDelete(side_effect_id=None)


# Update Side Effect
# NOTE: How will downstream know the side effect id ? Isnt that internal ?
# Should we rather add update_side_effect_for_medication_and_user ?
@app.put("/side_effects/{side_effect_id}", response_model=SideEffectRead)
async def side_effects_update(side_effect_id: int, update_data: SideEffectUpdate):
    return None
