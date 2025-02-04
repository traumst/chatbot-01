import uvicorn
from fastapi import FastAPI
from src.router import home, query, history
from src.database import engine
from src import models

app = FastAPI(title="LLM Query API", version="1.0")

# Create database tables (for demo; in production use Alembic migrations)
models.Base.metadata.create_all(bind=engine)

app.include_router(home.router)
app.include_router(query.router)
app.include_router(history.router)

# Run the server (only if this script is run directly)
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=7654, reload=True)
