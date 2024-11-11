from typing import Optional

from pydantic import BaseModel


class ProductsAndServices(BaseModel):
    name: Optional[str]
    description: Optional[str]
    url: Optional[str]
