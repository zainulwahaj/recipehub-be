from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserType, Recipe, AIGenerateRequest, AIGenerateResponse, RecipeResponse
from app.services.auth import get_current_user
from app.services.recipe_ai import generate_recipe_with_ai
from app.routers.recipes import get_recipe_with_extras

router = APIRouter()

@router.post("/generate", response_model=AIGenerateResponse)
def generate_recipe(
    request: AIGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        recipe_data = generate_recipe_with_ai(
            ingredients=request.ingredients,
            diet=request.diet,
            cuisine=request.cuisine,
            max_time_minutes=request.max_time_minutes,
            difficulty=request.difficulty,
            servings=request.servings,
            user_id=current_user.id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    is_public = current_user.user_type == UserType.CHEF
    
    new_recipe = Recipe(
        user_id=current_user.id,
        title=recipe_data["title"],
        description=recipe_data["description"],
        ingredients=recipe_data["ingredients"],
        steps=recipe_data["steps"],
        time_minutes=recipe_data["time_minutes"],
        difficulty=recipe_data["difficulty"],
        tags=recipe_data.get("tags", []),
        source="ai",
        is_public=is_public
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    
    recipe_dict = get_recipe_with_extras(new_recipe, db, current_user)
    return AIGenerateResponse(recipe=RecipeResponse(**recipe_dict))
