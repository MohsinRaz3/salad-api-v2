from main import app

def handler(event, context):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    response = asgi_handler(event, context)
    return response
