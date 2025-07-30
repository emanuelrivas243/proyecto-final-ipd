import ray
from fastapi import FastAPI
from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB
from pydantic import BaseModel
import numpy as np  # Importamos numpy
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

ray.init()

app = FastAPI()

class request_body(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# Cargar dataset
iris = load_iris()
X = iris['data']  # type: ignore
Y = iris['target']  # type: ignore
target_names = iris['target_names']  # type: ignore

# Entrenar modelo
clf = GaussianNB()
clf.fit(X, Y)

@app.post("/predict")
def predict(data: request_body):
    test_data = np.array([[ 
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]])
    
    class_idx = clf.predict(test_data)[0]
    return {"class": target_names[class_idx]}



app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")