from fastapi import FastAPI
from core.database import engine
from core.base import Base
from controllers import root

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(root)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True)