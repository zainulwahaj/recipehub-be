# 📖 RecipeHub AI — Complete Project Documentation

> **Version:** 1.0.0  
> **Date:** December 11, 2025  
> **Author:** Development Team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [API Reference](#4-api-reference)
5. [Database Schema](#5-database-schema)
6. [Data Validation Schemas](#6-data-validation-schemas)
7. [Frontend Pages](#7-frontend-pages)
8. [Authentication System](#8-authentication-system)
9. [AI Recipe Generation System](#9-ai-recipe-generation-system)
10. [Role-Based Access Control](#10-role-based-access-control)
11. [Project Structure](#11-project-structure)

---

## 1. Project Overview

### What is RecipeHub AI?

**RecipeHub AI** is a modern, full-stack web application that combines traditional recipe management with artificial intelligence. It enables users to:

- **Generate Recipes with AI:** Input ingredients you have at home, and the AI creates a complete recipe with instructions.
- **Manage Personal Recipes:** Create, edit, and organize your own recipe collection.
- **Discover New Recipes:** Browse recipes published by professional chefs.
- **Rate & Favorite:** Save your favorite recipes and rate ones you've tried.

### Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Recipe Generation** | GPT-4o-mini powered recipe creation from ingredients |
| 👨‍🍳 **Role-Based System** | Different capabilities for Regular Users vs. Chefs |
| 🔐 **Secure Authentication** | JWT-based login with bcrypt password hashing |
| 📱 **Modern UI** | Responsive React frontend with Terracotta & Sage theme |
| ⭐ **Ratings & Favorites** | Community interaction features |
| 🔍 **Smart Filtering** | Search by name, diet, and cooking time |

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│                 │◄──────────────────►│                 │
│  React Frontend │                    │  FastAPI Server │
│   (Vite + SPA)  │                    │   (Uvicorn)     │
│                 │                    │                 │
└─────────────────┘                    └────────┬────────┘
                                                │
                              ┌─────────────────┼─────────────────┐
                              │                 │                 │
                              ▼                 ▼                 ▼
                    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
                    │   PostgreSQL    │ │   OpenAI    │ │   JWT Token     │
                    │    Database     │ │  GPT-4o-mini│ │   Validation    │
                    └─────────────────┘ └─────────────┘ └─────────────────┘
```

### Data Flow

1. **User Interaction:** User interacts with React frontend in browser
2. **API Request:** Frontend sends HTTP request to FastAPI backend
3. **Authentication:** Backend validates JWT token (if protected route)
4. **Business Logic:** Backend processes request (may call OpenAI for AI features)
5. **Database:** Data is read from or written to PostgreSQL
6. **Response:** JSON response sent back to frontend
7. **UI Update:** React updates the interface with new data

---

## 3. Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.115.0 | Web framework (async, type hints, auto-docs) |
| **Uvicorn** | 0.32.0 | ASGI server |
| **SQLAlchemy** | 2.0.36 | ORM (Object-Relational Mapping) |
| **PostgreSQL** | Latest | Production database |
| **Alembic** | 1.13.2 | Database migrations |
| **Pydantic** | 2.9.2 | Data validation and serialization |
| **python-jose** | 3.3.0 | JWT token handling |
| **passlib + bcrypt** | 1.7.4 / 4.0.1 | Password hashing |
| **OpenAI SDK** | 1.51.0 | AI recipe generation |

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI component library |
| **Vite** | 7.2.4 | Build tool and dev server |
| **React Router** | 7.9.6 | Client-side routing |
| **CSS3** | - | Styling (CSS Variables for theming) |

---

## 4. API Reference

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Create a new user account | ❌ No |
| `POST` | `/auth/login` | Login and receive access token | ❌ No |

#### POST `/auth/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "user_type": "REGULAR"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "user_type": "REGULAR"
}
```

#### POST `/auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "user_type": "REGULAR"
  }
}
```

---

### Recipe Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/recipes` | List recipes (with optional filters) | 🔶 Optional |
| `GET` | `/recipes/{id}` | Get a single recipe | 🔶 Optional |
| `POST` | `/recipes` | Create a new recipe | ✅ Yes |
| `PUT` | `/recipes/{id}` | Update a recipe | ✅ Yes (owner) |
| `DELETE` | `/recipes/{id}` | Delete a recipe | ✅ Yes (owner) |
| `POST` | `/recipes/{id}/favorite` | Add to favorites | ✅ Yes |
| `DELETE` | `/recipes/{id}/favorite` | Remove from favorites | ✅ Yes |
| `POST` | `/recipes/{id}/rate` | Rate a recipe (1-5) | ✅ Yes |

#### GET `/recipes`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search in title and description |
| `diet` | string | Filter by dietary tag |
| `max_time` | integer | Maximum cooking time in minutes |
| `mine` | boolean | If true, returns user's own recipes |
| `limit` | integer | Maximum number of results |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Chicken Stir Fry",
    "description": "A quick and healthy dinner option",
    "ingredients": ["chicken breast", "soy sauce", "vegetables"],
    "steps": ["Cut chicken...", "Heat oil...", "Stir fry..."],
    "time_minutes": 25,
    "difficulty": "Easy",
    "tags": ["Asian", "Quick"],
    "source": "manual",
    "is_public": true,
    "avg_rating": 4.5,
    "created_at": "2025-12-11T10:30:00Z",
    "updated_at": "2025-12-11T10:30:00Z",
    "author": {
      "id": 2,
      "name": "Chef Maria"
    },
    "is_owner": false,
    "is_favorite": true,
    "user_rating": 5
  }
]
```

---

### AI Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/ai/recipes/generate` | Generate recipe using AI | ✅ Yes |

#### POST `/ai/recipes/generate`

**Request Body:**
```json
{
  "ingredients": ["chicken", "rice", "lemon", "garlic"],
  "diet": "Halal",
  "cuisine": "Mediterranean",
  "max_time_minutes": 45,
  "difficulty": "Medium",
  "servings": 4
}
```

**Response (200 OK):**
```json
{
  "recipe": {
    "id": 15,
    "title": "Lemon Garlic Chicken with Rice",
    "description": "A flavorful Mediterranean-inspired dish...",
    "ingredients": [
      "500g chicken breast",
      "2 cups basmati rice",
      "2 lemons, juiced",
      "4 cloves garlic, minced"
    ],
    "steps": [
      "Marinate chicken in lemon juice and garlic for 30 minutes",
      "Cook rice according to package instructions",
      "..."
    ],
    "time_minutes": 45,
    "difficulty": "Medium",
    "tags": ["Mediterranean", "Halal", "Chicken"],
    "source": "ai",
    "is_public": false,
    "author": { "id": 1, "name": "John Doe" }
  }
}
```

---

## 5. Database Schema

### Entity Relationship Diagram

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│    users      │       │    recipes    │       │   favorites   │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ id (PK)       │──┐    │ id (PK)       │──┐    │ id (PK)       │
│ name          │  │    │ user_id (FK)  │◄─┘    │ user_id (FK)  │
│ email (UQ)    │  │    │ title         │  │    │ recipe_id(FK) │
│ password_hash │  │    │ description   │  │    │ created_at    │
│ user_type     │  │    │ ingredients   │  │    └───────────────┘
│ created_at    │  │    │ steps         │  │
└───────────────┘  │    │ time_minutes  │  │    ┌───────────────┐
                   │    │ difficulty    │  │    │    ratings    │
                   │    │ tags          │  │    ├───────────────┤
                   │    │ source        │  │    │ id (PK)       │
                   │    │ is_public     │  │    │ user_id (FK)  │
                   │    │ avg_rating    │  │    │ recipe_id(FK) │
                   │    │ created_at    │◄─┼────│ rating (1-5)  │
                   │    │ updated_at    │  │    │ created_at    │
                   │    └───────────────┘  │    └───────────────┘
                   │                       │
                   │    ┌───────────────┐  │
                   │    │  ai_requests  │  │
                   │    ├───────────────┤  │
                   └───►│ id (PK)       │  │
                        │ user_id (FK)  │◄─┘
                        │ model         │
                        │ prompt_tokens │
                        │ completion_tok│
                        │ created_at    │
                        └───────────────┘
```

### Table Definitions

#### `users` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `name` | VARCHAR | NOT NULL | Display name |
| `email` | VARCHAR | UNIQUE, NOT NULL | Login email |
| `password_hash` | VARCHAR | NOT NULL | Bcrypt hashed password |
| `user_type` | VARCHAR(20) | NOT NULL, DEFAULT 'REGULAR' | 'REGULAR' or 'CHEF' |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation time |

#### `recipes` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id | Recipe owner |
| `title` | VARCHAR | NOT NULL | Recipe name |
| `description` | VARCHAR | NOT NULL | Brief description |
| `ingredients` | JSON | NOT NULL | Array of ingredients |
| `steps` | JSON | NOT NULL | Array of instructions |
| `time_minutes` | INTEGER | NOT NULL | Cooking time |
| `difficulty` | VARCHAR | NOT NULL | Easy/Medium/Hard |
| `tags` | JSON | NULLABLE | Dietary/category tags |
| `source` | VARCHAR | NOT NULL | 'manual' or 'ai' |
| `is_public` | BOOLEAN | DEFAULT TRUE | Visibility |
| `avg_rating` | NUMERIC(3,2) | NULLABLE | Average rating |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation time |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update time |

#### `favorites` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id | User who favorited |
| `recipe_id` | INTEGER | FOREIGN KEY → recipes.id | Favorited recipe |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When favorited |

#### `ratings` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id | User who rated |
| `recipe_id` | INTEGER | FOREIGN KEY → recipes.id | Rated recipe |
| `rating` | INTEGER | NOT NULL | Rating value (1-5) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When rated |

#### `ai_requests` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id | Requesting user |
| `model` | VARCHAR | NOT NULL | AI model used |
| `prompt_tokens` | INTEGER | NULLABLE | Tokens in prompt |
| `completion_tokens` | INTEGER | NULLABLE | Tokens in response |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Request time |

---

## 6. Data Validation Schemas

### User Schemas (Pydantic)

```python
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_type: Optional[UserType] = UserType.REGULAR

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: UserType

class LoginResponse(BaseModel):
    accessToken: str
    user: UserResponse
```

### Recipe Schemas (Pydantic)

```python
class RecipeCreate(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    steps: List[str]
    time_minutes: int
    difficulty: str
    tags: Optional[List[str]] = None
    is_public: bool = True

class RecipeUpdate(BaseModel):
    # All fields Optional for partial updates
    title: Optional[str] = None
    description: Optional[str] = None
    # ... etc

class RecipeResponse(BaseModel):
    id: int
    title: str
    description: str
    ingredients: List[str]
    steps: List[str]
    time_minutes: int
    difficulty: str
    tags: Optional[List[str]]
    source: str
    is_public: bool
    avg_rating: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]
    author: AuthorInfo
    is_owner: Optional[bool] = None
    is_favorite: Optional[bool] = None
    user_rating: Optional[int] = None
```

### AI Schemas (Pydantic)

```python
class AIGenerateRequest(BaseModel):
    ingredients: List[str]
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    max_time_minutes: int = 30
    difficulty: str = "Easy"
    servings: int = 2

class AIGenerateResponse(BaseModel):
    recipe: RecipeResponse
```

---

## 7. Frontend Pages

### Page Overview

| Page | Route | Purpose |
|------|-------|---------|
| **HomePage** | `/` | Landing page with app introduction |
| **LoginPage** | `/login` | User authentication |
| **SignupPage** | `/signup` | New user registration |
| **DashboardPage** | `/dashboard` | User's personal dashboard |
| **BrowseRecipesPage** | `/browse` | Discover public recipes |
| **MyRecipesPage** | `/my-recipes` | Manage own recipes |
| **CreateRecipePage** | `/recipes/create` | Manual recipe creation |
| **EditRecipePage** | `/recipes/edit/:id` | Edit existing recipe |
| **RecipeDetailPage** | `/recipes/:id` | View full recipe |
| **AIGenerateRecipePage** | `/ai-generate` | AI recipe generation |

### Page Details

#### DashboardPage (`/dashboard`)
- **Purpose:** Central hub for authenticated users
- **Features:**
  - Recipe count statistics
  - Quick action buttons (Create Recipe, Generate AI Recipe)
  - Different stats for Chefs (includes Reviews)
  - Navigation to other sections

#### AIGenerateRecipePage (`/ai-generate`)
- **Purpose:** AI-powered recipe creation
- **Features:**
  - Ingredient input (comma-separated)
  - Dietary preference dropdown
  - Cuisine style dropdown
  - Difficulty selector
  - Servings number input
  - Max cooking time slider
- **Flow:** Submit → Loading state → Display generated recipe → Auto-saved

#### BrowseRecipesPage (`/browse`)
- **Purpose:** Public recipe discovery
- **Features:**
  - Search bar (searches title and description)
  - Diet filter (e.g., Vegetarian, Halal)
  - Max time filter
  - Recipe card grid with ratings
- **Note:** Only shows public recipes from Chef users

---

## 8. Authentication System

### Registration Flow

```
┌──────────┐    POST /auth/register    ┌──────────┐
│  Client  │ ─────────────────────────►│  Server  │
│          │   {name, email, password, │          │
│          │    user_type}             │          │
└──────────┘                           └────┬─────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │ Check if email │
                                   │    exists      │
                                   └───────┬────────┘
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                              ▼                         ▼
                        Email exists            Email available
                              │                         │
                              ▼                         ▼
                     Return 400 Error      ┌───────────────────┐
                                           │ Hash password     │
                                           │ with bcrypt       │
                                           └─────────┬─────────┘
                                                     │
                                                     ▼
                                           ┌───────────────────┐
                                           │ Create user in DB │
                                           └─────────┬─────────┘
                                                     │
                                                     ▼
                                            Return UserResponse
                                                (201 Created)
```

### Login Flow

```
┌──────────┐    POST /auth/login    ┌──────────┐
│  Client  │ ──────────────────────►│  Server  │
│          │   {email, password}    │          │
└──────────┘                        └────┬─────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  Query user by  │
                                │      email      │
                                └───────┬─────────┘
                                        │
                           ┌────────────┴────────────┐
                           │                         │
                           ▼                         ▼
                   User not found              User found
                           │                         │
                           ▼                         ▼
                  Return 401 Error      ┌─────────────────────┐
                                        │ Verify password     │
                                        │ (bcrypt.verify)     │
                                        └──────────┬──────────┘
                                                   │
                                      ┌────────────┴────────────┐
                                      │                         │
                                      ▼                         ▼
                              Password wrong            Password correct
                                      │                         │
                                      ▼                         ▼
                             Return 401 Error      ┌─────────────────────┐
                                                   │ Generate JWT Token  │
                                                   │ (sub=user_id,       │
                                                   │  exp=30min)         │
                                                   └──────────┬──────────┘
                                                              │
                                                              ▼
                                                   Return LoginResponse
                                                   {accessToken, user}
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1",
    "exp": 1702300000
  },
  "signature": "..."
}
```

---

## 9. AI Recipe Generation System

### Complete Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                             │
├─────────────────────────────────────────────────────────────────────┤
│  1. User fills form:                                                │
│     - Ingredients: "chicken, rice, lemon"                           │
│     - Diet: "Halal"                                                 │
│     - Cuisine: "Mediterranean"                                      │
│     - Difficulty: "Easy"                                            │
│     - Time: 30 min                                                  │
│     - Servings: 4                                                   │
│                                                                     │
│  2. Click "Generate Recipe"                                         │
│                                                                     │
│  3. Show loading spinner                                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    POST /api/ai/recipes/generate
                    Authorization: Bearer <token>
                    {
                      "ingredients": ["chicken", "rice", "lemon"],
                      "diet": "Halal",
                      "cuisine": "Mediterranean",
                      "max_time_minutes": 30,
                      "difficulty": "Easy",
                      "servings": 4
                    }
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI) - ai.py                        │
├─────────────────────────────────────────────────────────────────────┤
│  4. Validate JWT token → Get current_user                           │
│                                                                     │
│  5. Call generate_recipe_with_ai() service                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  SERVICE (recipe_ai.py)                             │
├─────────────────────────────────────────────────────────────────────┤
│  6. Build prompt:                                                   │
│     """                                                             │
│     Create a detailed recipe with the following requirements:       │
│     - Ingredients: chicken, rice, lemon                             │
│     - Servings: 4                                                   │
│     - Maximum time: 30 minutes                                      │
│     - Difficulty: Easy                                              │
│     - Dietary preference: Halal                                     │
│     - Cuisine style: Mediterranean                                  │
│                                                                     │
│     Please provide the recipe in JSON format...                     │
│     """                                                             │
│                                                                     │
│  7. Send to OpenAI API (gpt-4o-mini)                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        OPENAI API                                   │
├─────────────────────────────────────────────────────────────────────┤
│  8. AI generates JSON response:                                     │
│     {                                                               │
│       "title": "Mediterranean Lemon Chicken Rice",                  │
│       "description": "A fragrant one-pot dish...",                  │
│       "ingredients": ["500g chicken", "2 cups rice", ...],          │
│       "steps": ["Season chicken...", "Cook rice...", ...],          │
│       "time_minutes": 30,                                           │
│       "difficulty": "Easy",                                         │
│       "tags": ["Mediterranean", "Halal", "One-Pot"]                 │
│     }                                                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  BACKEND (recipe_ai.py + ai.py)                     │
├─────────────────────────────────────────────────────────────────────┤
│  9. Log AI request to ai_requests table                             │
│     (tokens used for billing/monitoring)                            │
│                                                                     │
│  10. Determine visibility:                                          │
│      is_public = (user.user_type == "CHEF")                         │
│                                                                     │
│  11. Create Recipe in database:                                     │
│      - source = "ai"                                                │
│      - is_public = based on user type                               │
│                                                                     │
│  12. Return AIGenerateResponse with full recipe                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                             │
├─────────────────────────────────────────────────────────────────────┤
│  13. Hide loading spinner                                           │
│                                                                     │
│  14. Display generated recipe with:                                 │
│      - Title, description                                           │
│      - Ingredients list                                             │
│      - Step-by-step instructions                                    │
│      - Tags, cooking time, difficulty                               │
│                                                                     │
│  15. Recipe is auto-saved and appears in "My Recipes"               │
└─────────────────────────────────────────────────────────────────────┘
```

### OpenAI Configuration

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system", 
            "content": "You are a professional chef. Create detailed, accurate recipes in JSON format."
        },
        {
            "role": "user", 
            "content": prompt
        }
    ],
    temperature=0.7,
    response_format={"type": "json_object"}
)
```

---

## 10. Role-Based Access Control

### User Types

| Type | Description |
|------|-------------|
| **REGULAR** | Standard users for personal recipe management |
| **CHEF** | Professional chefs who can publish recipes publicly |

### Permission Matrix

| Feature | REGULAR User | CHEF User |
|---------|:------------:|:---------:|
| Create personal recipes | ✅ | ✅ |
| Make recipes public | ❌ | ✅ |
| AI generate recipes | ✅ (private) | ✅ (public) |
| Edit own recipes | ✅ | ✅ |
| Delete own recipes | ✅ | ✅ |
| View public recipes | ✅ | ✅ |
| Recipes shown in Browse | ❌ | ✅ |
| Favorite recipes | ✅ | ✅ |
| Rate recipes | ✅ | ✅ |
| See Reviews stat | ❌ | ✅ |

### Access Control Implementation

#### Backend (Recipe Creation)
```python
# In recipes.py - create_recipe()
is_public = recipe_data.is_public
if current_user.user_type == UserType.REGULAR:
    is_public = False  # Force private for regular users
```

#### Backend (AI Generation)
```python
# In ai.py - generate_recipe()
is_public = current_user.user_type == UserType.CHEF
```

#### Backend (Public Listing)
```python
# In recipes.py - list_recipes()
# Only show public recipes from CHEFs
query = query.join(User).filter(
    and_(Recipe.is_public == True, User.user_type == UserType.CHEF)
)
```

#### Frontend (UI Visibility)
```jsx
// In RecipeForm.jsx - Hide public toggle for regular users
{user?.user_type === 'CHEF' && (
  <label>
    <input type="checkbox" checked={isPublic} onChange={...} />
    Make this recipe public
  </label>
)}
```

---

## 11. Project Structure

### Backend Structure

```
recipe-maker-backend/
├── .env                    # Environment variables (secrets)
├── alembic.ini             # Alembic configuration
├── requirements.txt        # Python dependencies
│
├── alembic/                # Database migrations
│   ├── env.py              # Migration environment
│   └── versions/           # Migration files
│       ├── 078f706f40a5_initial_tables.py
│       └── 216181ee4c1e_add_user_type.py
│
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI app entry point
    ├── database.py         # DB connection + settings
    ├── models.py           # SQLAlchemy models + Pydantic schemas
    │
    ├── routers/            # API route handlers
    │   ├── auth.py         # /api/auth/* endpoints
    │   ├── recipes.py      # /api/recipes/* endpoints
    │   └── ai.py           # /api/ai/recipes/* endpoints
    │
    └── services/           # Business logic
        ├── auth.py         # Password hashing, JWT, dependencies
        ├── openai.py       # OpenAI client singleton
        └── recipe_ai.py    # AI recipe generation logic
```

### Frontend Structure

```
recipe-maker-frontend/
├── .env                    # Environment variables (API URL)
├── index.html              # HTML entry point
├── package.json            # npm dependencies
├── vite.config.js          # Vite configuration
│
├── public/                 # Static assets
│
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Root component + routing
    ├── App.css             # Component styles
    ├── index.css           # Global styles + CSS variables
    │
    ├── api/
    │   └── client.js       # Axios/fetch wrapper for API calls
    │
    ├── context/
    │   └── AuthContext.jsx # Authentication state management
    │
    ├── hooks/
    │   └── useAuth.js      # Auth hook for components
    │
    ├── components/
    │   ├── Navbar.jsx      # Navigation bar
    │   ├── ProtectedRoute.jsx  # Route guard
    │   ├── RecipeCard.jsx  # Recipe preview card
    │   ├── RecipeForm.jsx  # Create/Edit form
    │   └── RecipeList.jsx  # Recipe grid
    │
    └── pages/
        ├── HomePage.jsx
        ├── LoginPage.jsx
        ├── SignupPage.jsx
        ├── DashboardPage.jsx
        ├── BrowseRecipesPage.jsx
        ├── MyRecipesPage.jsx
        ├── CreateRecipePage.jsx
        ├── EditRecipePage.jsx
        ├── RecipeDetailPage.jsx
        └── AIGenerateRecipePage.jsx
```

---

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/recipedb
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-your-openai-api-key
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

---

## Running the Application

### Backend
```bash
cd recipe-maker-backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Frontend
```bash
cd recipe-maker-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Points
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## Summary

RecipeHub AI is a full-stack application that demonstrates:

1. **Modern Backend Architecture** with FastAPI, featuring clean separation of concerns (routers, services, models)
2. **Secure Authentication** using JWT tokens and bcrypt password hashing
3. **AI Integration** with OpenAI's GPT-4o-mini for intelligent recipe generation
4. **Role-Based Access Control** distinguishing between regular users and chefs
5. **RESTful API Design** with proper HTTP methods and status codes
6. **React Frontend** with context-based state management and protected routes
7. **Relational Database** design with proper foreign key relationships

The application is designed to be maintainable, scalable, and easy to understand, following best practices for both Python and JavaScript development.
