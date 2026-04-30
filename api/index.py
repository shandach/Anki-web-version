import sys
sys.path.insert(0, 'backend')

from app.main import app
from mangum import Mangum

# Mangum адаптер для ASGI → AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")
