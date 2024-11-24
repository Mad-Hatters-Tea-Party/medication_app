from fastapi import FastAPI
from activity import CrudSideEffectsActivities

app = FastAPI()

# API activities which requests can be routed to
# CRUD requests for Side Effects
app.include_router(CrudSideEffectsActivities.router)