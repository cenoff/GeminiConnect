import uvicorn
from backend import app
from config import HOST, PORT
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    config = uvicorn.Config(app=app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    server.run()
