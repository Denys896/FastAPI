from fastapi import APIRouter

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

@router.get("")
def list_users():
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]

@router.get("/{id}")
def get_user(id: int):
    return {"id": id, "name": f"User {id}"}