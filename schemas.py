from pydantic import BaseModel, Field
from typing import Optional, List

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field("apparel", description="Product category")
    image: Optional[str] = Field(None, description="Primary image URL")
    images: Optional[List[str]] = Field(default_factory=list, description="Gallery image URLs")
    color: Optional[str] = Field(None, description="Primary color / variant")
    sizes: Optional[List[str]] = Field(default_factory=list, description="Available sizes")
    tag: Optional[str] = Field(None, description="Badge like New or Bestseller")
