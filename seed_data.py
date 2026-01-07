from app import db, create_app
from app.models.product import Product

app = create_app()
with app.app_context():
    # Clear existing products
    Product.query.delete()
    
    products = [
        Product(
            name="فستان سهرة أسود ملكي",
            description="فستان سواريه أنيق جداً، خامة ليكرا مستوردة، مناسب لكل المناسبات السعيدة.",
            category="Dresses",
            price=1200.0,
            color="Black",
            ai_tags=["soiree", "evening", "elegant"],
            featured=True,
            stock=10
        ),
        Product(
            name="طقم كاجوال صيفي",
            description="طقم مريح جداً للجامعة أو الخروجات اليومية، قطن 100%.",
            category="Casual",
            price=850.0,
            color="Blue",
            ai_tags=["casual", "summer", "cotton"],
            featured=True,
            stock=15
        ),
        Product(
            name="شنطة يد جلد طبيعي",
            description="شنطة شيك جداً تكمل طقمك، جلد طبيعي 100% صناعة مصرية.",
            category="Bags",
            price=450.0,
            color="Red",
            ai_tags=["accessory", "leather"],
            featured=False,
            stock=5
        ),
        Product(
            name="حذاء كعب عالي ذهبي",
            description="حذاء سواريه كعب عالي، مريح جداً في اللبس وشيك جداً.",
            category="Shoes",
            price=600.0,
            color="Gold",
            ai_tags=["soiree", "shoes"],
            featured=False,
            stock=8
        )
    ]
    
    for p in products:
        db.session.add(p)
    
    db.session.commit()
    print("✅ Seed data added successfully!")
