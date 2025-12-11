from typing import List, Optional
from app.services.openai import get_openai_client
from app.models import AIRequest
from sqlalchemy.orm import Session


def generate_recipe_with_ai(
    ingredients: List[str],
    diet: Optional[str],
    cuisine: Optional[str],
    max_time_minutes: int,
    difficulty: str,
    servings: int,
    user_id: int,
    db: Session
) -> dict:
    client = get_openai_client()
    
    ingredients_str = ", ".join(ingredients)
    
    prompt = f"""Create a detailed recipe with the following requirements:
- Ingredients: {ingredients_str}
- Servings: {servings}
- Maximum time: {max_time_minutes} minutes
- Difficulty: {difficulty}"""
    
    if diet:
        prompt += f"\n- Dietary preference: {diet}"
    if cuisine:
        prompt += f"\n- Cuisine style: {cuisine}"
    
    prompt += """

Please provide the recipe in the following JSON format:
{
  "title": "Recipe title",
  "description": "Brief description of the recipe",
  "ingredients": ["ingredient1", "ingredient2", ...],
  "steps": ["step1", "step2", ...],
  "time_minutes": number,
  "difficulty": "Easy" or "Medium" or "Hard",
  "tags": ["tag1", "tag2", ...]
}

Make sure the recipe uses the provided ingredients and follows all the constraints."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional chef. Create detailed, accurate recipes in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        import json
        recipe_data = json.loads(response.choices[0].message.content)
        
        ai_request = AIRequest(
            user_id=user_id,
            model="gpt-4o-mini",
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )
        db.add(ai_request)
        db.commit()
        
        return recipe_data
    except Exception as e:
        raise ValueError(f"Failed to generate recipe: {str(e)}")


