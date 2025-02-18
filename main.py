import uvicorn
from fastapi import FastAPI
from api_v1 import router as api_router
from demo_auth import jwt_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Applied Informatics",
    description="API for control web-application",
    version="0.1.0",
    redoc_url=None,
    contact={
        "name": "Farrukh Yuldoshev",
        "email": "codingmaestro.uz@gmail.com",
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(jwt_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        # ssl_keyfile="key.pem",
        # ssl_certfile="cert.pem",
        reload=True,
    )
