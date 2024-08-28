import base64
import json
import os

from flask import Flask, Response, render_template, request

from pygraving.score import score_from_json
from pygraving.state_machine import StateMachine

app = Flask(__name__, template_folder='.')

def make_preview(body):
    machine = StateMachine()
    score_image = machine(body)
    img_str = base64.b64encode(score_image).decode('utf-8')
    return img_str

# === Load the site examples ===
examples_folder = "site_examples"
files = sorted(os.listdir(examples_folder))
score_examples_lookup = {file.replace(".txt", ""): open(f"{examples_folder}/{file}").read() for file in files}

score_examples = []
for file in files:
    value = open(f"{examples_folder}/{file}").read()
    score_examples.append({
        "name": file.replace(".txt", ""),
        "value": value,
        "base64_img": make_preview(value)
    })
print(files)
# === === ===

@app.route('/')
def index():
    load = request.args.get("load")
    loaded = score_examples_lookup.get(load, "")
    return render_template('index.html', loaded=loaded)

@app.route('/help')
def doc():
    return render_template('doc.html')

@app.route('/examples')
def examples():
    return render_template('examples.html', examples=score_examples)

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
    return make_preview(body)

@app.post('/parse_json')
def parse_json():
    body = request.form.get("body")
    body = json.loads(body)
    score_image = score_from_json(body)
    # return a png image from the binary data
    return Response(score_image, mimetype="image/png")

if __name__ == '__main__':
    app.run(debug=True)