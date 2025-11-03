import uvicorn
from backend import app
from config import HOST, PORT

if __name__ == "__main__":
    config = uvicorn.Config(app=app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    server.run()
