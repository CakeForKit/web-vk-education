import random
import string
from urllib.parse import parse_qs

def create_dynamic(kb_data):
    return ''.join(random.choices(string.ascii_letters + ' ', k=kb_data * 1024))

def log_params(environ):
    # GET параметры
    query = environ.get('QUERY_STRING', '')
    if query:
        get_params = parse_qs(query)
        print(f"GET parameters: {get_params}")
    
    # POST параметры
    if environ.get('REQUEST_METHOD') == 'POST':
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
            if length > 0:
                post_data = environ['wsgi.input'].read(length)
                print(f"POST data (raw): {post_data}")
        except:
            pass

def dynamic_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    # log_params(environ)
    return [create_dynamic(30).encode('utf-8')]

def static_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    with open('./test_30kb.txt', 'rb') as f:
        data = f.read()
    # log_params(environ)
    return [data]

def main_app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path == '/dynamic' or path == '/dynamic/':
        print("dynamic")
        return dynamic_app(environ, start_response)
    elif path == '/static' or path == '/static/':
        print("static")
        return static_app(environ, start_response)
    else:
        status = '404 Not Found'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        return [b'404 - Page not found\n']

application = main_app
