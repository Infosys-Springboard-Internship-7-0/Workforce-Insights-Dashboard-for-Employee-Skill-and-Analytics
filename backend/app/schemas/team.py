from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    role: str
    contribution: str
    skills: str = ""
    linkedin: str = ""
    github: str = ""
