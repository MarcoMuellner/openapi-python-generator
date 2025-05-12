from datetime import datetime, date
from typing import List
from typing import Optional

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel


app = FastAPI()


class RootResponse(BaseModel):
    message: str


class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    birthdate: Optional[date] = None


class Team(BaseModel):
    id: int
    name: str
    description: str
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    users: Optional[List[User]] = None


@app.get("/", response_model=RootResponse, tags=["general"])
async def root():
    return {"message": "Hello World"}


@app.get("/users", response_model=List[User], tags=["general"])
async def get_users():
    return [
        User(
            id=1, username="user1", email="x@y.com", password="123456", is_active=True
        ),
        User(
            id=2, username="user2", email="x@y.com", password="123456", is_active=True
        ),
    ]


@app.get("/users/{user_id}", response_model=User, tags=["general"])
async def get_user(user_id: int):
    return User(
        id=user_id, username="user1", email="x@y.com", password="123456", is_active=True
    )


@app.post("/users", response_model=User, tags=["general"], status_code=201)
async def create_user(user: User):
    return user


@app.patch("/users/{user_id}", response_model=User, tags=["general"], status_code=200)
async def update_user(user_id: int, user: User):
    return user


@app.delete("/users/{user_id}", tags=["general"], status_code=204)
async def delete_user(user_id: int):
    return None


@app.get("/teams", response_model=List[Team], tags=["general"])
async def get_teams():
    return [
        Team(
            id=1,
            name="team1",
            description="team1",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Team(
            id=2,
            name="team2",
            description="team2",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]


@app.get("/teams/{team_id}", response_model=Team, tags=["general"])
async def get_team(team_id: int):
    return Team(
        id=team_id,
        name="team1",
        description="team1",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        users=[
            User(
                id=1,
                username="user1",
                email="x@y.com",
                password="123456",
                is_active=True,
            )
        ],
    )


@app.post("/teams", response_model=Team, tags=["general"], status_code=201)
async def create_team(team: Team):
    return team


@app.patch("/teams/{team_id}", response_model=Team, tags=["general"], status_code=200)
async def update_team(team_id: int, team: Team):
    return team


@app.delete("/teams/{team_id}", tags=["general"], status_code=204)
async def delete_team(team_id: int):
    return None


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="openapi-python-generator test api",
        version="1.0.0",
        description="API Schema for openapi-python-generator test api",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    openapi_schema["servers"] = [{"url": "http://localhost:8080"}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
