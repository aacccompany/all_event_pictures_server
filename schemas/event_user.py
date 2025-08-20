from pydantic import BaseModel
from schemas.auth import UserResponse

class EventUserJoin(BaseModel):
    event_id: int
    user_id: int


class EventUserResponse(EventUserJoin):
    id: int
    user: UserResponse
