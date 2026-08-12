"""Team member schemas."""

from pydantic import BaseModel, Field


class TeamMemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    role: str = Field(..., min_length=1, max_length=150)
    contribution: str = Field(..., min_length=1)
    photo_url: str | None = None
    linkedin_url: str | None = None
    display_order: int = 0


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    contribution: str | None = None
    photo_url: str | None = None
    linkedin_url: str | None = None
    display_order: int | None = None


class TeamMemberOut(TeamMemberBase):
    id: int
    model_config = {"from_attributes": True}
