# Imports
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId  
from models import Todo
import creds

MONGO_URI = creds.uri

app = FastAPI()


# Establishing MongoDB connection
client = MongoClient(MONGO_URI)
db = client["todoapp"]
collection = db["todos"]


@app.get("/")
async def read_root():
    return {"message": "Hello, World"}

# Getting all todos.
@app.get("/todos")
async def get_todos():
    todos = []
    cursor = collection.find()
    for document in cursor:
        # Converting ObjectId to string
        document['_id'] = str(document['_id'])
        todos.append(document)
    return {"todos": todos}

# Creating a single todo.
@app.post("/todos")
async def create_todos(todo: Todo):
    collection.insert_one(todo.dict())
    return {"message": "Todo added successfully!"}

# Getting a single todo.
@app.get("/todos/{todo_id}")
async def get_todo_by_id(todo_id: int):
    # Find document by id field
    todo_document = collection.find_one({"id": todo_id})
    # Check if document exists
    if todo_document:
        todo_dict = dict(todo_document)
        todo_dict.pop("_id", None)
        return {"todo": todo_dict}
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

# Deleting todos. 
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    collection.delete_one({"id": todo_id})
    return {"message": "Todo has been deleted."}

# Update a todo.
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo_obj: Todo):
    todo_document = collection.find_one({"id": todo_id})
    if todo_document:
        result = collection.update_one({"id": todo_id}, {"$set": {"item": todo_obj.item}})
        if result.modified_count == 1:
            # Excluding the _id field from the response content
            del todo_document['_id']
            return {"message": "Todo updated successfully!"}
        else:
            return {"detail": "Todo item not updated"}
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
