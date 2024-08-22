import base64
import json

from flask import Flask, Response, render_template, request

from pygraving.score import score_from_json
from pygraving.state_machine import StateMachine

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.post('/draw')
def draw():
    body = request.form.get("body")
    machine = StateMachine()
    score_image = machine(body)
    # return a png image from the binary data
    return Response(score_image, mimetype="image/png")

@app.post('/preview')
def preview():
    body = request.json.get("body")
    machine = StateMachine()
    score_image = machine(body)
    img_str = base64.b64encode(score_image).decode('utf-8')
    return img_str

@app.post('/parse_json')
def parse_json():
    body = request.form.get("body")
    body = json.loads(body)
    score_image = score_from_json(body)
    # return a png image from the binary data
    return Response(score_image, mimetype="image/png")

if __name__ == '__main__':
    app.run(debug=True)