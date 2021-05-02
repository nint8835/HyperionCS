from typing import Dict

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world() -> Dict[str, int]:
    return {"a": 1}
