import base64
import json
import os

import markdown
from flask import (Flask, Response, render_template, request,
                   send_from_directory)
from markupsafe import Markup

from pygraving.parsing.state_machine import StateMachine
from pygraving.score import score_from_json

app = Flask(__name__, template_folder='./site_pages')

# "development"-like params
MAKE_SITE_EXAMPLES = False
MAKE_DEBUG_EXAMPLES = False
BUILD_DOC_EXAMPLES = False

# # "development"-like params
# MAKE_SITE_EXAMPLES = False
# MAKE_DEBUG_EXAMPLES = True
# BUILD_DOC_EXAMPLES = False

# # "production"-like params
# MAKE_SITE_EXAMPLES = True
# MAKE_DEBUG_EXAMPLES = app.debug
# BUILD_DOC_EXAMPLES = True

def make_preview(body):
    machine = StateMachine()
    score_image = machine(body)
    img_str = base64.b64encode(score_image).decode('utf-8')
    return img_str

score_examples = []
score_examples_lookup = {}
if MAKE_SITE_EXAMPLES:
    examples_folder = "site_examples"
    files = sorted(os.listdir(examples_folder))
    score_examples_lookup = {file.replace(".txt", ""): open(f"{examples_folder}/{file}").read() for file in files}

    for file in files:
        value = open(f"{examples_folder}/{file}").read()
        score_examples.append({
            "name": file.replace(".txt", ""),
            "value": value,
            "base64_img": make_preview(value)
        })

debug_examples = []
if MAKE_DEBUG_EXAMPLES:
    debug_file = "debug_examples.txt"
    debug_scores = open(debug_file).read().split("\n-----\n")

    for example in debug_scores:
        debug_examples.append({
            "name": "",
            "value": example,
            "base64_img": make_preview(example)
        })

if BUILD_DOC_EXAMPLES:
    doc_file = "doc_examples.txt"
    with open(doc_file, 'r') as file:
        doc_content = file.read()
        
    examples = doc_content.split("* ")
    examples.pop(0)

    for example in examples:
        # split example with "\n\n" only once
        image_file, body = example.split("\n\n", 1)
        base64_img = make_preview(body)
        
        with open(f'site_pages/static/{image_file}', 'wb') as img_file:
            img_file.write(base64.b64decode(base64_img))


@app.context_processor
def inject_debug():
    return dict(debug=app.debug)

@app.route('/')
def index():
    load = request.args.get("load")
    loaded = score_examples_lookup.get(load, "")
    return render_template('index.html', page="/", loaded=loaded)

# static files
@app.route('/static/<path>')
def send_static(path):
    print(path)
    return send_from_directory('site_pages/static', path)

@app.route('/help/<string:lang>')
def doc(lang):
    with open(f'site_pages/help_{lang}.md', 'r') as file:
        content = file.read()
    doc_content = Markup(markdown.markdown(content))
    return render_template('doc.html', page="/help", doc_content=doc_content)

@app.route('/help')
def doc_home():
    # read lang in request
    user_locale = request.accept_languages.best_match(['fr', 'en'])
    return doc(user_locale)

@app.route('/examples')
def examples():
    return render_template('examples.html', page="/examples", examples=score_examples)

@app.route('/me')
def me():
    return render_template('me.html', page="/me")

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