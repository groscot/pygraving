import base64
import json
import os

from flask import Flask, Response, render_template, request

from pygraving.parsing.state_machine import StateMachine
from pygraving.score import score_from_json

app = Flask(__name__, template_folder='./site_pages')

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
# === === ===

# === Load the debug examples ===
debug_examples = []

if app.debug:
    debug_file = "debug_examples.txt"
    debug_scores = open(debug_file).read().split("\n-----\n")

    for example in debug_scores:
        debug_examples.append({
            "name": "",
            "value": example,
            "base64_img": make_preview(example)
        })
# === === ===

@app.context_processor
def inject_debug():
    return dict(debug=app.debug)

@app.route('/')
def index():
    load = request.args.get("load")
    loaded = score_examples_lookup.get(load, "")
    return render_template('index.html', page="/", loaded=loaded)

@app.route('/help')
def doc():
    return render_template('doc.html', page="/help")

@app.route('/examples')
def examples():
    return render_template('examples.html', page="/examples", examples=score_examples)

@app.route('/debug')
def debug():
    if not app.debug:
        return "Not Found", 404
    return render_template('examples.html', page="/debug", examples=debug_examples)


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