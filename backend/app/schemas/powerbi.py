"""Power BI embed link schemas."""

from pydantic import BaseModel, Field


class PowerBILinkBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    embed_url: str = Field(..., min_length=1, max_length=2000)
    is_active: bool = True
    display_order: int = 0


class PowerBILinkCreate(PowerBILinkBase):
    pass


class PowerBILinkUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    embed_url: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class PowerBILinkOut(PowerBILinkBase):
    id: int
    model_config = {"from_attributes": True}
