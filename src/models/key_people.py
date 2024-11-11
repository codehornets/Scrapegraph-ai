from typing import Optional

from pydantic import BaseModel


class KeyPeople(BaseModel):
    name: Optional[str]
    position: Optional[str]
    linkedin_profile: Optional[str]
