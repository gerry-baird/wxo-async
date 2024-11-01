from typing import Annotated

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

@callback_router.post("{$callbackurl}")
def make_callback() -> Output_Wrapper:
    pass

@app.post("/v1/generate", callbacks=callback_router.routes, status_code=status.HTTP_202_ACCEPTED)
async def generate(req: Async_Request,background_tasks: BackgroundTasks,
                   callbackurl: Annotated[str | None, Header()] = None) -> Async_Ack:

    ack = Async_Ack(description = "Async Ack")
    print("*** Callback URL " + callbackurl)

    background_tasks.add_task(send_response, callbackurl=callbackurl)

    return ack

@app.post("/foo")
async def foo(payload: Output_Wrapper):
    print("Foo Received " + payload.model_dump_json())

def send_response(callbackurl: str):
    print("*** Sending response to " + callbackurl)
    resp = Async_Response(name = "Fred", age = 18)
    wrapper = Output_Wrapper(output=resp)

    httpx.post(callbackurl, data=wrapper.model_dump_json())