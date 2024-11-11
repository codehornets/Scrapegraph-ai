from typing import Optional

from pydantic import BaseModel


class CompanySocialMediaLinks(BaseModel):
    linkedin: Optional[str]
    facebook: Optional[str]
    instagram: Optional[str]
    twitter: Optional[str]
    youtube: Optional[str]
