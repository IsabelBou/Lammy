from threading import Thread

from flask import Flask

app = Flask("")


@app.route("/")
def _keep_alive():
    return 'I am alive dude'


def _run_flask():
    app.run('0.0.0.0', port=8080)


def run_keep_alive():
    server = Thread(target=_run_flask)
    server.start()
    return server
