from flask import Blueprint, render_template, request, jsonify
from app.models.product import Product
from app.utils.ai_recommender import recommender

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage with featured products"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get featured products
    featured_products = Product.query.filter_by(featured=True).limit(6).all()
    
    # Get all products with pagination
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    products = pagination.items
    
    return render_template('index.html', 
                         featured_products=featured_products,
                         products=products,
                         pagination=pagination)

@bp.route('/search')
def search():
    """Search products by name, category, or tags"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    # Build query
    search_query = Product.query
    
    if query:
        search_query = search_query.filter(
            (Product.name.ilike(f'%{query}%')) | 
            (Product.description.ilike(f'%{query}%'))
        )
    
    if category:
        search_query = search_query.filter_by(category=category)
    
    products = search_query.all()
    
    return render_template('search.html', 
                         products=products,
                         query=query,
                         category=category)

@bp.route('/cart')
def cart():
    """Shopping cart page"""
    return render_template('cart.html')

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
