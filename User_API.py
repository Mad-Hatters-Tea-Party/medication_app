from fastapi import FastAPI, Path, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()


class User(BaseModel): 
    user_id: int = None 
    first_name: str 
    last_name: str 
    email: str 
    password: str 
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime]

users_db = [] 

#Creates the users with user id (if you type 0, it will set it to one and so on)
#as requred and created_at and updated_at ones that are updated
@app.post("/users/", response_model=User) 
def create_user(user: User): 
    user.user_id = len(users_db) + 1 
    user.created_at = datetime.now() 
    user.updated_at = datetime.now() 
    users_db.append(user) 
    return user 

#Searches for a user using the user_id
@app.get("/users/{user_id}", response_model=User) 
def read_user(user_id: int): 
    for user in users_db: 
        if user.user_id == user_id: 
            return user 
        raise HTTPException(status_code=404, detail="User not found") 

#Updates the user using user_id as input to change. updates user.updated_at to current time  
@app.put("/users/{user_id}", response_model=User) 
def update_user(user_id: int, user: User): 
    for idx, existing_user in enumerate(users_db): 
        if existing_user.user_id == user_id: 
            user.user_id = user_id 
            user.created_at = existing_user.created_at 
            user.updated_at = datetime.now() 
            users_db[idx] = user 
            return user 
    raise HTTPException(status_code=404, detail="User not found") 

#Removes user from the database using user_id
@app.delete("/users/{user_id}", response_model=User) 
def delete_user(user_id: int): 
    for idx, user in enumerate(users_db): 
        if user.user_id == user_id: del users_db[idx] 
        return user 
    raise HTTPException(status_code=404, detail="User not found")

