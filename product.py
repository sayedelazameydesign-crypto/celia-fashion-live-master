from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Product(db.Model):
    """Product model for storing clothing items"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)  # shirt, pants, jacket, etc.
    price = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(50))  # main color
    available_colors = db.Column(db.JSON)  # list of available colors
    
    # 3D Model paths (stored in Cloudinary)
    model_3d_url = db.Column(db.String(500))  # .glb file URL
    thumbnail_url = db.Column(db.String(500))  # preview image
    texture_urls = db.Column(db.JSON)  # different textures/colors
    
    # AI Tags for recommendations
    ai_tags = db.Column(db.JSON)  # ['casual', 'summer', 'cotton']
    
    # Metadata
    stock = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'color': self.color,
            'available_colors': self.available_colors or [],
            'model_3d_url': self.model_3d_url,
            'thumbnail_url': self.thumbnail_url,
            'texture_urls': self.texture_urls or {},
            'ai_tags': self.ai_tags or [],
            'stock': self.stock,
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.name}>'

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Order(db.Model):
    """Order model for purchases"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    products = db.Column(db.JSON)  # [{'product_id': 1, 'quantity': 2, 'color': 'red'}]
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.id}>'

class RecommendationCache(db.Model):
    """Cache for AI recommendations"""
    __tablename__ = 'recommendation_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    recommended_ids = db.Column(db.JSON)  # [1, 5, 8, 12]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RecommendationCache for Product {self.product_id}>'
