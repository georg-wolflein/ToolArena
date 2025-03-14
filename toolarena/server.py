import asyncio
import json
import os
import shlex
from pathlib import Path
from uuid import uuid4

import yaml
from fastapi import FastAPI
from loguru import logger
from pydantic import create_model

from toolarena.types import RunToolResponse, argument_type_map

RUNTIME_DIR = Path(os.getenv("TOOLARENA_RUNTIME_DIR", "/toolarena_runtime"))
TOOLARENA_DIR = Path(os.getenv("TOOLARENA_DIR", "/toolarena"))
IMPLEMENTATION_PATH = RUNTIME_DIR / "implementation.py"
TASK_DEFINITION_PATH = RUNTIME_DIR / "task.yaml"
FUNCTION_RUNNER_PATH = TOOLARENA_DIR / "function_runner.py"

task_definition = yaml.safe_load(open(TASK_DEFINITION_PATH, "r"))


app = FastAPI()


@app.get("/info")
async def info():
    return task_definition


RunRequest = create_model(
    "RunRequest",
    **{
        k: (argument_type_map[v["type"]], ...)
        for k, v in task_definition["arguments"].items()
    },  # type: ignore
)


@app.get("/alive")
async def alive():
    return {"status": "ok"}


@app.post("/run")
async def run(args: RunRequest) -> RunToolResponse:  # type: ignore
    function_name = task_definition["name"]
    logger.info(f"Running {function_name} with args: {args}")
    id = uuid4()
    info_path = Path(f"/tmp/{id}_info.json")
    output_path = Path(f"/tmp/{id}_output.json")
    json.dump(
        {
            "path": str(IMPLEMENTATION_PATH.absolute()),
            "name": function_name,
            "args": args.model_dump(),  # type: ignore
            "output_path": str(output_path.absolute()),
        },
        open(info_path, "w"),
    )
    process = await asyncio.create_subprocess_shell(
        shlex.join(
            [
                "python",
                str(FUNCTION_RUNNER_PATH.absolute()),
                str(info_path.absolute()),
            ]
        ),
        stdin=asyncio.subprocess.DEVNULL,
        # stdout=asyncio.subprocess.PIPE,
        # stderr=asyncio.subprocess.STDOUT,
        text=False,
        cwd="/workspace",
        env=os.environ,
        start_new_session=True,  # this is to make sure an error is thrown if the command attempts to read from stdin
    )
    return_code = await process.wait()
    response = RunToolResponse(
        return_code=return_code, result=json.load(open(output_path, "r"))["result"]
    )
    for file in (info_path, output_path):
        file.unlink(missing_ok=True)

    return response
