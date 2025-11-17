import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    category: str
    image: Optional[str] = None
    images: Optional[List[str]] = None
    color: Optional[str] = None
    sizes: Optional[List[str]] = None
    tag: Optional[str] = None


# Utility to convert Mongo document to API shape
def serialize_product(doc) -> ProductOut:
    return ProductOut(
        id=str(doc.get("_id")),
        title=doc.get("title", ""),
        description=doc.get("description"),
        price=float(doc.get("price", 0)),
        category=doc.get("category", "apparel"),
        image=doc.get("image"),
        images=doc.get("images"),
        color=doc.get("color"),
        sizes=doc.get("sizes"),
        tag=doc.get("tag"),
    )


@app.on_event("startup")
def seed_products():
    try:
        if db is None:
            return
        count = db["product"].count_documents({})
        if count == 0:
            seed = [
                {
                    "title": "Iridescent Tee",
                    "description": "Boxy unisex tee with subtle pearlescent finish.",
                    "price": 48.0,
                    "category": "tops",
                    "image": "https://images.unsplash.com/photo-1666374792290-665a1d115a40?ixid=M3w3OTkxMTl8MHwxfHNlYXJjaHwxfHxJcmlkZXNjZW50JTIwVGVlfGVufDB8MHx8fDE3NjMzOTE5OTB8MA&ixlib=rb-4.1.0&w=1600&auto=format&fit=crop&q=80",
                    "images": [],
                    "color": "Pearl",
                    "sizes": ["XS", "S", "M", "L", "XL"],
                    "tag": "New",
                },
                {
                    "title": "Glass Bottle Hoodie",
                    "description": "Oversized hoodie inspired by glass-bottle sheen.",
                    "price": 92.0,
                    "category": "hoodies",
                    "image": "https://images.unsplash.com/photo-1516826957135-700dedea698c?q=80&w=1400&auto=format&fit=crop",
                    "images": [],
                    "color": "Lavender",
                    "sizes": ["XS", "S", "M", "L", "XL"],
                    "tag": "Bestseller",
                },
                {
                    "title": "Studio Sweatpants",
                    "description": "Relaxed fit with elastic cuffs and deep pockets.",
                    "price": 78.0,
                    "category": "bottoms",
                    "image": "https://images.unsplash.com/photo-1693250707470-687a2cf908b0?ixid=M3w3OTkxMTl8MHwxfHNlYXJjaHwxfHxTdHVkaW8lMjBTd2VhdHBhbnRzfGVufDB8MHx8fDE3NjMzOTE5OTB8MA&ixlib=rb-4.1.0&w=1600&auto=format&fit=crop&q=80",
                    "images": [],
                    "color": "Onyx",
                    "sizes": ["XS", "S", "M", "L", "XL"],
                },
                {
                    "title": "Minimal Tank",
                    "description": "Breathable ribbed tank, clean neckline.",
                    "price": 36.0,
                    "category": "tops",
                    "image": "https://images.unsplash.com/photo-1755335853548-52622a24b11c?ixid=M3w3OTkxMTl8MHwxfHNlYXJjaHwxfHxNaW5pbWFsJTIwVGFua3xlbnwwfDB8fHwxNzYzMzkxOTkwfDA&ixlib=rb-4.1.0&w=1600&auto=format&fit=crop&q=80",
                    "images": [],
                    "color": "Cloud",
                    "sizes": ["XS", "S", "M", "L", "XL"],
                },
            ]
            for s in seed:
                create_document("product", s)
    except Exception:
        # Silently ignore seeding errors to not block startup
        pass


@app.get("/")
def read_root():
    return {"message": "Bella Vogue API is running"}


@app.get("/api/products", response_model=List[ProductOut])
def list_products():
    docs = get_documents("product")
    return [serialize_product(d) for d in docs]


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: str):
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")

    doc = db["product"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_product(doc)


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
