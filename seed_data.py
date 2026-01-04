from app import create_app, db
from app.models.product import Product

def seed_data():
    """Seeds the database with sample product data."""
    app = create_app('development')
    with app.app_context():
        # Check if data already exists
        if Product.query.count() > 0:
            print("Database already seeded.")
            return

        print("Seeding database with sample products...")

        products = [
            Product(id=1, name='Classic T-Shirt', category='shirt', price=150.0, color='black', material='cotton', sizes=['S', 'M', 'L'], stock=10, thumbnail_url='https://res.cloudinary.com/dixa78h2w/image/upload/v1735870597/EcommerceAI3D/thumbnails/black_shirt_thumb_d69gzj.webp'),
            Product(id=2, name='Summer Dress', category='dress', price=350.0, color='red', material='silk', sizes=['M', 'L'], stock=5, thumbnail_url='https://res.cloudinary.com/dixa78h2w/image/upload/v1735870601/EcommerceAI3D/thumbnails/red_dress_thumb_i5ez9j.webp'),
            Product(id=3, name='Leather Bag', category='bag', price=500.0, color='brown', stock=8, thumbnail_url='https://res.cloudinary.com/dixa78h2w/image/upload/v1735870591/EcommerceAI3D/thumbnails/brown_bag_thumb_kkgx4z.webp'),
            Product(id=4, name='High Heels', category='shoes', price=450.0, color='black', stock=12, thumbnail_url='https://res.cloudinary.com/dixa78h2w/image/upload/v1735870594/EcommerceAI3D/thumbnails/black_heels_thumb_yftf2f.webp'),
            Product(id=5, name='White Blouse', category='shirt', price=250.0, color='white', material='cotton', stock=15, thumbnail_url='https://res.cloudinary.com/dixa78h2w/image/upload/v1735870604/EcommerceAI3D/thumbnails/white_blouse_thumb_tkv5n7.webp'),
            Product(id=6, name='Blue Jeans', category='pants', price=400.0, color='blue', material='denim', stock=20, thumbnail_url='https://res.cloudinary.com/dixa78h2w/image/upload/v1735870599/EcommerceAI3D/thumbnails/blue_jeans_thumb_zjg9wc.webp'),
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
