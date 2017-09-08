from flask import Flask, request, jsonify, make_response
from polyglot.text import Text
from polyglot.detect import Detector
app = Flask(__name__)

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """See: http://flask.pocoo.org/snippets/56/"""
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type'])
def analyze():
    if request.method == 'GET':
        return '''
        <h1>Usage</h1>
        <code>curl -XPOST http://localhost:5000 -H "Content-Type: text/plain; charset=UTF-8" --data-ascii "Australia posted a World Cup record total of 417-6 as they beat Afghanistan by 275 runs."</code>
        <form action="." method="POST"><textarea palceholder="enter sample here" name="text"></textarea><button>Test!</button></form>'''
    
    if request.method == 'OPTIONS':
        resp = make_response('')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Request-Method'] = 'POST GET'
        return resp
    
    if request.method == 'POST':
        text = Text((request.get_json() and request.get_json().get('text')) or request.form['text'] or request.data)
        result = []
        cur = 0
        for entity in text.entities:
            result.append({'text': ' '.join(text.words[cur:entity.start])})
            result.append({'entity': entity.tag, 'text': ' '.join(text.words[entity.start:entity.end])})
            cur = entity.end
        result.append({'text': ' '.join(text.words[cur:])})
        return jsonify({'result': result})

if __name__ == "__main__":
    app.run()