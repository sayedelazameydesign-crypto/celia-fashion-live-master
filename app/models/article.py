from app import db
from datetime import datetime

class Article(db.Model):
    """Article/Blog post model"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)  # URL-friendly title
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))  # Short description
    
    # Featured image
    featured_image_url = db.Column(db.String(500))
    
    # Author info
    author_name = db.Column(db.String(100), default='Admin')
    
    # Categories and tags
    category = db.Column(db.String(100))  # fashion, trends, tips, news
    tags = db.Column(db.JSON)  # ['summer', 'style', 'guide']
    
    # SEO
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # Status
    published = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)  # Show on homepage
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Stats
    views = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert article to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'featured_image_url': self.featured_image_url,
            'author_name': self.author_name,
            'category': self.category,
            'tags': self.tags or [],
            'meta_description': self.meta_description,
            'published': self.published,
            'featured': self.featured,
            'views': self.views,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<Article {self.title}>'
