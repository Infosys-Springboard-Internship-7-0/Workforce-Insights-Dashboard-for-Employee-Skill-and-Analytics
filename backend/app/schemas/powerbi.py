from pydantic import BaseModel


class PowerBIUpdate(BaseModel):
    name: str
    description: str = ""
    embed_url: str
    is_active: bool = True
