#from http://werkzeug.pocoo.org/
from werkzeug.wrappers import Request, Response

@Request.application
def application(request):
    return Response('Example Application.  Please visit /console for the debugger')

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 8081, application, use_debugger=True)
