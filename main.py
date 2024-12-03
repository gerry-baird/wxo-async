import json
from typing import Annotated
import time
from fastapi import FastAPI, Header, APIRouter, BackgroundTasks
from pydantic import BaseModel
from starlette import status
import httpx

app = FastAPI()

callback_router = APIRouter()
class Async_Request(BaseModel):
    name: str
    age: int

class Async_Response(BaseModel):
    name: str
    age: int

class Output_Wrapper(BaseModel):
    output: Async_Response

class Async_Ack(BaseModel):
    description: str

@app.get("/")
def alive ():
    return {"message": "Alive"}

@callback_router.post("{$callbackurl}", status_code=status.HTTP_202_ACCEPTED)
def make_callback() -> Output_Wrapper:
    pass

@app.post("/v1/generate", callbacks=callback_router.routes, status_code=status.HTTP_202_ACCEPTED)
async def generate(req: Async_Request,background_tasks: BackgroundTasks,
                   callbackurl: Annotated[str , Header()] = None) -> Async_Ack:
    print("*** /v1/generate called with body:")
    print(req.model_dump_json())
    ack = Async_Ack(description = "Async Ack")
    print("*** Received callback URL " + callbackurl)

    # do complex processing that requires async response
    req.age = req.age + 1

    background_tasks.add_task(send_response, callbackurl=callbackurl, req=req)

    return ack

@app.post("/foo")
async def foo(payload: Output_Wrapper):
    print("Foo Received " + payload.model_dump_json())

def send_response(callbackurl: str, req: Async_Request):
    print("*** Sending response to " + callbackurl)
    print("*** Taking a quick nap")
    time.sleep(10)

    payload = Async_Response(name = req.name, age = req.age)

    wrapper = Output_Wrapper(output=payload)
    print("*** Awake - now sending response ")
    jsonStr = json.dumps(wrapper.dict())
    print(jsonStr)



    headers = {'Content-Type': 'application/json'}

    response = httpx.post(callbackurl, data=jsonStr, headers=headers)
    print(response.json())