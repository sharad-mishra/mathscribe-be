import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your router
from apps.calculator.route import router as calculator_router

app = FastAPI()

# Configure CORS
origins = [
    "https://mathscribe-fe.vercel.app",  # Replace with your Vercel frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return {"message": "Server is running"}

# Include your router
app.include_router(calculator_router, prefix="/calculate", tags=["calculate"])

if __name__ == "__main__":
    SERVER_URL = os.getenv("SERVER_URL", "0.0.0.0")
    PORT = os.getenv("PORT", 8000)
    ENV = os.getenv("ENV", "production")
    uvicorn.run("main:app", host=SERVER_URL, port=int(PORT), reload=(ENV == "dev"))