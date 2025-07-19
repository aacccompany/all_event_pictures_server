from fastapi import FastAPI
from core.database import Base, engine
from controllers import root

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(root)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", port=8081, reload=True)