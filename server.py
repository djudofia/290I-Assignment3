from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    # Check if the file is a JSON file
    if not file.filename.endswith(".json"):
        return {"Upload Error": "Invalid file type"}
    
    try:
        # Create graph from the JSON file
        global active_graph
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": str(e)}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    #TODO: implement this function
    raise NotImplementedError("/solve_shortest_path not yet implemented.")

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    