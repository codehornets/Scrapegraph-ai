from pydantic import BaseModel


class Email(BaseModel):
    subject: str
    content: str
    trigger: str
    timing: str
