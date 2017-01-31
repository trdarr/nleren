import base64
import json
import urllib.parse

import flask
import psycopg2
import requests
import yaml
from flask import Flask
from psycopg2 import ProgrammingError
from psycopg2.extras import RealDictCursor

from .users import UserService

with open('secrets.yaml', 'r') as secrets_file:
  secrets = yaml.load(secrets_file)

app = Flask(__name__)
app.secret_key = secrets['secret_key']

@app.before_request
def connect():
  flask.g.connection = psycopg2.connect(
      host='postgres',
      user='postgres',
      cursor_factory=RealDictCursor)
  flask.g.users = UserService(flask.g.connection)

@app.before_request
def load_session():
  if 'session_id' in flask.session:
    session_id = flask.session['session_id']
    flask.g.current_user = flask.g.users.find_by_session_id(session_id)
  else:
    flask.g.current_user = None

@app.after_request
def close_connection(response):
  flask.g.connection.close()
  return response

@app.route('/')
def index():
  return flask.render_template('index.html.j2',
      current_user=flask.g.current_user)

@app.route('/sign-in')
def sign_in():
  if 'code' not in flask.request.args:
    # Redirect to Google to get an authorization code.
    # https://developers.google.com/identity/protocols/OAuth2WebServer#redirecting
    uri = 'https://accounts.google.com/o/oauth2/v2/auth'
    qs = urllib.parse.urlencode({
        'client_id': secrets['google']['client_id'],
        'redirect_uri': flask.url_for('sign_in', _external=True),
        'response_type': 'code',
        'scope': 'email profile'})

    return flask.redirect(f'{uri}?{qs}')

  if 'error' in flask.request.args:
    # Something terrible has happened.
    flask.flash(flask.request.args['error'], category='error')
    return flask.redirect(flask.url_for('index'))

  else:
    # Exchange the authorization code for access and refresh tokens.
    # https://developers.google.com/identity/protocols/OAuth2WebServer#handlingresponse
    uri = 'https://www.googleapis.com/oauth2/v4/token'
    app.logger.info('Handling response from Google.')
    response = requests.post(uri, data={
        'client_id': secrets['google']['client_id'],
        'client_secret': secrets['google']['client_secret'],
        'code': flask.request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': flask.url_for('sign_in', _external=True)})

    # We're really only interested in the id_token, which is a JWT.
    # The JWT consists of three components delimited by a period.
    # The second is the “payload”, a Base64-encoded JSON object.
    # Adding ‘===’ before decoding prevents padding errors.
    payload = response.json()['id_token'].split('.')[1]
    token = json.loads(base64.b64decode(payload + '==='))

    # Create (or update) the user and create a session for the user.
    user_id = flask.g.users.create(token['sub'], token['name'], token['email'])
    flask.session['session_id'] = flask.g.users.create_session(user_id)

    # Redirect to the index.
    return flask.redirect(flask.url_for('index'))

@app.route('/sign-out')
def sign_out():
  flask.session.clear()
  return flask.redirect(flask.url_for('index'))
