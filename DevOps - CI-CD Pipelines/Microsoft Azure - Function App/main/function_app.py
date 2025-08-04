import logging
import azure.functions as func
# from FlaskApp import app
from flask import Flask, redirect

app = Flask(__name__)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the WSGI handler.
    """

    logging.info('Python HTTP trigger function processed a request.')
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)


@app.route('/')
def index():
    logging.info('Flask app about to do a redirect.')
    return redirect('https://www.gigacourses.com/', code=301)


