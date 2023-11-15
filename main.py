import config
import sys
import signal
from db import db
from app import create_app
from gevent.pywsgi import WSGIServer

http_server = None


def graceful_shutdown(self, *args):
    print("Received Termination Signal, Preparing graceful shutdown process..")
    if http_server:
        http_server.close()
        print("Server closed.")
    db.close()
    print("Graceful shutdown finished!")
    sys.exit(0)


if __name__ == "__main__":
    # assign handler function
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    # connect Database
    db.connect(
        host=config.POSTGRES_HOST,
        dbname=config.POSTGRES_DBNAME,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASS,
        port=config.POSTGRES_PORT,
    )

    # create http server
    app = create_app()
    http_server = WSGIServer(("0.0.0.0", config.PORT), app)
    print(f"Server start on port {config.PORT} ({config.NODE_ENV})")
    http_server.serve_forever()
