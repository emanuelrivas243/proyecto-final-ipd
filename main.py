import ray
from fastapi import FastAPI
from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB
from pydantic import BaseModel
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

ray.init()

app = FastAPI()

class request_body(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# Actor de Ray que contiene el modelo y hace predicciones
@ray.remote
class IrisModelActor:
    def __init__(self):
        iris = load_iris()
        self.X = iris['data'] # type: ignore
        self.Y = iris['target'] # type: ignore
        self.target_names = iris['target_names'] # type: ignore
        self.model = GaussianNB()
        self.model.fit(self.X, self.Y)

    def predict(self, data):
        test_data = np.array([data])
        class_idx = self.model.predict(test_data)[0]
        return self.target_names[class_idx]

# Crear instancia del actor
iris_model_actor = IrisModelActor.remote()

@app.post("/predict")
async def predict(data: request_body):
    input_data = [
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]
    prediction = await iris_model_actor.predict.remote(input_data) # type: ignore
    return {"class": prediction}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
