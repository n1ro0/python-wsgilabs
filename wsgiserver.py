from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from html import escape, unescape
import entities
import uuid


new_html = """
<html>
<head><title> Welcome to redirection test page </title> </head>
<body>
    <form method="post" action='/new/create'>
        Input Link:<br>
        <input type="text" name="hash"><br>
        <input type=submit value=submit>
    </form>
</body>
</html>
"""


def create_html(link):
    return """
            <html>
            <head><title> Welcome to redirection test page </title> </head>
            <body>
            Your link:<br>
            {}
            </body>
            </html>
            """.format(escape(link))


def new(environ, start_response):
    response_body = new_html.encode()
    status = '200 OK'
    response_headers = [
                        ('Content-Type','text/html'),
                        ('Content-Length', str(len(response_body)))
                       ]
    start_response(status, response_headers)
    return [response_body]


def new_create(environ, start_response):
    try:
        size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        size = 0
    data = environ['wsgi.input'].read(size).decode()
    qs = parse_qs(data)
    link = qs.get('hash')[0]
    str(uuid.uuid4())[-8:]
    if entities.Link.objects(link=link).count() == 0:
        duplicated = True
        while duplicated:
            shortcut = str(uuid.uuid4())[-8:]
            if entities.Link.objects(shortcut=shortcut).count() == 0:
                duplicated = False
        entities.Link(shortcut=shortcut, link=link).save()
    else:
        shortcut = entities.Link.objects(link=link).first().shortcut
    response_body = create_html(escape("localhost:8080/{}".format(shortcut))).encode()
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)
    return [response_body]


def main(environ, start_response):
    qs = parse_qs(environ['QUERY_STRING'])
    hash = qs.get('hash')[0]
    exists = entities.Link.objects(shortcut=hash).count() != 0
    if exists:
        link = entities.Link.objects(shortcut=hash).first().link
        start_response('302 Found', [('Location', link)])
    else:
        start_response('404 Not Found', [])
    return []



def short_link(shortcut, start_response):
    """
    exists = entities.Link.objects(shortcut=shortcut).count() != 0
    if exists:
        link = entities.Link.objects(shortcut=shortcut).first().link
        start_response('302 Found', [('Location', link)])
    else:
        start_response('404 Not Found', [])
    """
    link = entities.Link.objects(shortcut=shortcut).first()
    if link == None:
        start_response('404 Not Found', [])
    else:
        start_response('302 Found', [('Location', link.link)])
    return []


def app(environ, start_response):
    path = environ['PATH_INFO'].split('/')
    length = len(path)
    print(length)
    if length == 2 and path[1] == "":
        return main(environ, start_response)
    elif length == 2 and path[1] == "new":
        return new(environ, start_response)
    elif length == 2:
        return short_link(path[1], start_response)
    elif length == 3 and path[2] == "create":
        return new_create(environ, start_response)

if __name__ == "__main__":
    http_serv = make_server("localhost", 8080, app)
    http_serv.serve_forever()
