from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from decimal import Decimal
from app.database import get_db
from app.models import User, UserType, Recipe, Favorite, Rating, RecipeCreate, RecipeUpdate, RecipeResponse, AuthorInfo, RatingCreate, RatingResponse
from app.services.auth import get_current_user, get_current_user_optional

router = APIRouter()

def get_recipe_with_extras(recipe: Recipe, db: Session, current_user: Optional[User] = None) -> dict:
    result = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "steps": recipe.steps,
        "time_minutes": recipe.time_minutes,
        "difficulty": recipe.difficulty,
        "tags": recipe.tags,
        "source": recipe.source,
        "is_public": recipe.is_public,
        "avg_rating": recipe.avg_rating,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
        "author": AuthorInfo(id=recipe.user.id, name=recipe.user.name),
        "is_owner": False,
        "is_favorite": False,
        "user_rating": None
    }
    
    if current_user:
        result["is_owner"] = recipe.user_id == current_user.id
        
        favorite = db.query(Favorite).filter(
            and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe.id)
        ).first()
        rating = db.query(Rating).filter(
            and_(Rating.user_id == current_user.id, Rating.recipe_id == recipe.id)
        ).first()
        
        result["is_favorite"] = favorite is not None
        result["user_rating"] = rating.rating if rating else None
    
    return result

@router.get("", response_model=List[RecipeResponse])
def list_recipes(
    search: Optional[str] = Query(None),
    diet: Optional[str] = Query(None),
    max_time: Optional[int] = Query(None),
    mine: Optional[bool] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Recipe)
    
    if mine:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        query = query.filter(Recipe.user_id == current_user.id)
    else:
        query = query.join(User).filter(
            and_(Recipe.is_public == True, User.user_type == UserType.CHEF)
        )
    
    if search:
        query = query.filter(
            or_(
                Recipe.title.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%")
            )
        )
    
    if diet:
        query = query.filter(Recipe.tags.contains([diet]))
    
    if max_time:
        query = query.filter(Recipe.time_minutes <= max_time)
    
    if limit:
        query = query.limit(limit)
    
    recipes = query.all()
    
    results = []
    for recipe in recipes:
        recipe_dict = get_recipe_with_extras(recipe, db, current_user)
        results.append(RecipeResponse(**recipe_dict))
    
    return results

@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    if current_user:
        if recipe.user_id != current_user.id:
            if not recipe.is_public or recipe.user.user_type != UserType.CHEF:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recipe not accessible"
                )
    else:
        if not recipe.is_public or recipe.user.user_type != UserType.CHEF:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recipe not accessible"
            )
    
    recipe_dict = get_recipe_with_extras(recipe, db, current_user)
    return RecipeResponse(**recipe_dict)

@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_public = recipe_data.is_public
    if current_user.user_type == UserType.REGULAR:
        is_public = False
    
    new_recipe = Recipe(
        user_id=current_user.id,
        title=recipe_data.title,
        description=recipe_data.description,
        ingredients=recipe_data.ingredients,
        steps=recipe_data.steps,
        time_minutes=recipe_data.time_minutes,
        difficulty=recipe_data.difficulty,
        tags=recipe_data.tags or [],
        source="manual",
        is_public=is_public
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    
    recipe_dict = get_recipe_with_extras(new_recipe, db, current_user)
    return RecipeResponse(**recipe_dict)

@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this recipe"
        )
    
    update_data = recipe_data.model_dump(exclude_unset=True)
    
    if "is_public" in update_data and current_user.user_type == UserType.REGULAR:
        update_data["is_public"] = False
    
    for field, value in update_data.items():
        setattr(recipe, field, value)
    
    db.commit()
    db.refresh(recipe)
    
    recipe_dict = get_recipe_with_extras(recipe, db, current_user)
    return RecipeResponse(**recipe_dict)

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this recipe"
        )
    
    db.delete(recipe)
    db.commit()
    return None

@router.post("/{recipe_id}/favorite", status_code=status.HTTP_201_CREATED)
def add_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    existing_favorite = db.query(Favorite).filter(
        and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id)
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe already favorited"
        )
    
    favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.add(favorite)
    db.commit()
    return {"message": "Recipe favorited"}

@router.delete("/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorite = db.query(Favorite).filter(
        and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id)
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    db.delete(favorite)
    db.commit()
    return None

@router.post("/{recipe_id}/rate", response_model=RatingResponse)
def rate_recipe(
    recipe_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    existing_rating = db.query(Rating).filter(
        and_(Rating.user_id == current_user.id, Rating.recipe_id == recipe_id)
    ).first()
    
    if existing_rating:
        existing_rating.rating = rating_data.rating
    else:
        new_rating = Rating(
            user_id=current_user.id,
            recipe_id=recipe_id,
            rating=rating_data.rating
        )
        db.add(new_rating)
    
    db.commit()
    
    avg_rating_result = db.query(func.avg(Rating.rating)).filter(
        Rating.recipe_id == recipe_id
    ).scalar()
    
    recipe.avg_rating = Decimal(str(avg_rating_result)) if avg_rating_result else None
    db.commit()
    
    user_rating = rating_data.rating
    if existing_rating:
        user_rating = existing_rating.rating
    
    return RatingResponse(
        user_rating=user_rating,
        avg_rating=recipe.avg_rating
    )
