from fastapi import FastAPI, File, UploadFile, HTTPException
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
@app.post("/upload_graph_json")
@app.post("/upload")
async def create_upload_file(file: UploadFile = File(...)):
    """Upload a JSON graph file and set it as the active graph.

    Returns a JSON response with either Upload Success or Upload Error.
    """
    # basic filename validation
    if not file.filename or not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail={"Upload Error": "Invalid file type"})

    # optional: check content type (some clients may omit correct header)
    if file.content_type and "json" not in file.content_type:
        # allow but warn — we'll still attempt to parse; respond with 400 if parsing fails
        pass

    try:
        global active_graph
        # delegate parsing to utils.create_graph_from_json which expects UploadFile
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        # return a 400 with error details
        raise HTTPException(status_code=400, detail={"Upload Error": str(e)})


@app.get("/solve_shortest_path/starting_node_id={starting_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(starting_node_id: str, end_node_id: str):
    global active_graph
    
    # Check if a graph has been uploaded
    if active_graph is None:
        return {"Error": "No graph uploaded. Please upload a graph first."}
    
    # Check if start and end nodes exist in the graph
    if starting_node_id not in active_graph.nodes:
        return {"Error": f"Start node '{starting_node_id}' not found in graph."}
    if end_node_id not in active_graph.nodes:
        return {"Error": f"End node '{end_node_id}' not found in graph."}
    
    # Get the start node
    start_node = active_graph.nodes[starting_node_id]
    
    # Run Dijkstra's algorithm
    dijkstra(active_graph, start_node)
    
    # Get the end node to retrieve the shortest distance
    end_node = active_graph.nodes[end_node_id]
    shortest_distance = end_node.dist
    
    # Reconstruct the path from start to end using prev pointers
    path = []
    current = end_node
    while current is not None:
        path.append(current.id)
        current = current.prev
    
    path.reverse()  # Reverse to get path from start to end
    
    # Check if a path exists
    if len(path) == 0 or path[0] != starting_node_id:
        return {"Error": f"No path found from '{starting_node_id}' to '{end_node_id}'."}
    
    return {
        "starting_node_id": starting_node_id,
        "end_node_id": end_node_id,
        "shortest_path": path,
        "shortest_distance": float(shortest_distance)
    }

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    