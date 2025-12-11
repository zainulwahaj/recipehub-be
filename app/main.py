from fastapi import FastAPI
from mangum import Mangum
from app.routers import auth, recipes, ai

app = FastAPI(title="Recipe Maker API", version="1.0.0")

# Note: CORS is handled by Lambda Function URL, not FastAPI

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(ai.router, prefix="/api/ai/recipes", tags=["ai"])


@app.get("/")
def root():
    return {"message": "Recipe Maker API"}


# Lambda handler
handler = Mangum(app)



