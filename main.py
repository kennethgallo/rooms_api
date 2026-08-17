from typing import Annotated, Literal

from fastapi import Cookie, FastAPI, Header, HTTPException, Query, Response, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints, field_validator

openapi_tags = [
    {
        "name": "rooms",
        "description": "Operations with **rooms** (a 4-wall _space_ that can be slept in)",
    }
]

app = FastAPI(
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
    contact={"name": "Gallo Bookings", "email": "contact@vgcagent.com"},
    openapi_tags=openapi_tags,
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

apartment = {
    "id": 1,
    "name": "Sunny 2-bedroom apartment",
    "price_per_night": 200,
    "bedrooms": 2,
    "bathrooms": 1.5,
}

house = {
    "id": 2,
    "name": "Cozy 3-bedroom house",
    "price_per_night": 350,
    "bedrooms": 3,
    "bathrooms": 2.5,
}

studio = {
    "id": 3,
    "name": "Modern studio near uptown",
    "price_per_night": 150,
    "bedrooms": 1,
    "bathrooms": 1,
}


class AppCookies(BaseModel):
    theme: Literal["light", "dark"] = "dark"
    language: Literal["en", "es", "ge"] = "en"


class AppHeaders(BaseModel):
    user_agent: str | None


class RoomQueryParams(BaseModel):
    max_price: int | None = Field(
        default=None, ge=10, le=10_000, examples=[100, 200, 10_000]
    )

    search: Annotated[str | None, StringConstraints(to_lower=True)] = Field(
        default=None,
        min_length=3,
        max_length=10,
        title="Search term",
        description="Provide a keyword search term",
        examples=["sunny", "bedroom", "house"],
    )

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("No funny business allowed")
        return search


@app.get("/", status_code=status.HTTP_200_OK)
def root(
    app_cookies: Annotated[AppCookies, Cookie()],
    app_headers: Annotated[AppHeaders, Header()],
):
    greetings = {
        "en": "Welcome to rent a room",
        "es": "Bienvenido to rent a room",
        "ge": "Willkomen to rent a room",
    }
    greeting = greetings.get(app_cookies.language)

    return {"message": greeting, "user_agent": app_headers.user_agent}


# Annotated -> comes from 'typing' module
# Annotated type attaches metadata to an existing type (class)

# str
# value: Annotated[str, ] <- params after initial type are the metadata, can be complex[]{}etc


@app.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
    tags=["rooms"],
    summary="List all available rooms",
    description="Returns all rooms. Supports filtering by price and search term",
    response_description="A list of rooms matching filter criteria",
)
def get_rooms(params: Annotated[RoomQueryParams, Query()]):
    results = [apartment, house, studio]

    if params.max_price:
        results = [
            room for room in results if room["price_per_night"] <= params.max_price
        ]

    if params.search:
        results = [room for room in results if params.search in room["name"].lower()]

    return results


@app.get(
    "/rooms/mansions", status_code=status.HTTP_200_OK, tags=["rooms"], deprecated=True
)
def get_mansions(params: Annotated[RoomQueryParams, Query()]):
    results = [house]

    if params.max_price:
        results = [
            room for room in results if room["price_per_night"] <= params.max_price
        ]

    if params.search:
        results = [room for room in results if params.search in room["name"].lower()]

    return results


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")


@app.get("/preferences", status_code=status.HTTP_200_OK, tags=["preferences"])
def set_preferences(response: Response):
    app_cookies = AppCookies()

    response.set_cookie(key="theme", value=app_cookies.theme)
    response.set_cookie(key="language", value=app_cookies.language)

    return {"message": "preferences updated"}
