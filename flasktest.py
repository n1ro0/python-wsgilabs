from flask import Flask, render_template, request, make_response, Response
from urllib.parse import parse_qs
import entities
import uuid


app = Flask(__name__)

@app.route('/new')
def new():
    page = render_template('new.html')
    resp = Response(page)
    resp.headers['Content-Type'] = 'text/html'
    resp.headers['Content-Length'] = str(len(page))
    resp.status = '200 OK'
    return resp

@app.route('/new/create', methods=['POST'])
def new_create():
    try:
        size = request.content_length
    except ValueError:
        size = 0
    data = request.input_stream.read(size).decode()
    qs = parse_qs(data)
    link = qs.get('hash')[0]
    if entities.Link.objects(link=link).count() == 0:
        duplicated = True
        while duplicated:
            shortcut = str(uuid.uuid4())[-8:]
            if entities.Link.objects(shortcut=shortcut).count() == 0:
                duplicated = False
        entities.Link(shortcut=shortcut, link=link).save()
    else:
        shortcut = entities.Link.objects(link=link).first().shortcut
    page = render_template('create.html', hash="localhost:5000/{}".format(shortcut))
    resp = Response(page)
    resp.headers['Content-Type'] = 'text/html'
    resp.headers['Content-Length'] = str(len(page))
    resp.status = '200 OK'
    return resp




@app.route('/')
def index():
    shortcut = parse_qs(request.query_string.decode()).get('hash', [''])[0]
    link = entities.Link.objects(shortcut=shortcut).first()
    resp = make_response()
    if link == None:
        resp.status = '404 Not Found'
    else:
        resp.status = '302 Found'
        resp.headers['Location'] = link.link
    return resp


@app.route('/<shortcut>')
def hash(shortcut):
    link = entities.Link.objects(shortcut=shortcut).first()
    resp = make_response()
    if link == None:
        resp.status = '404 Not Found'
    else:
        resp.status = '302 Found'
        resp.headers['Location'] = link.link
    return resp



if __name__ == '__main__':
    app.run()