import uvicorn
import argparse

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from rag_lib.logger.print_progress import PrintProgressLogger

logger = PrintProgressLogger("")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# app.mount("/static", StaticFiles(directory="client"), name="static")

def get_args():
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--client_port', type=int, default=8844)
    parser.add_argument('--server_port', type=int, default=8877)

    return parser.parse_args()

# @app.get("/config")
# def get_config(request: Request):
#     config = {
#         "client_port": request.app.state.client_port,
#         "server_port": request.app.state.server_port,
#     }
#     return config

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    server_port = request.app.state.server_port
    logger.info(f'Connecting server port: {server_port}')
    data = {"server_port": server_port}
    return templates.TemplateResponse("client_web_page.html", {
        "request": request,
        "data": data
    })

if __name__ == "__main__":

    args = get_args()

    app.state.client_port = args.client_port
    app.state.server_port = args.server_port

    uvicorn.run(
        app, #"client_server:app",
        host="0.0.0.0",
        port=args.client_port,
        ssl_certfile=None,
        ssl_keyfile=None,
    )
