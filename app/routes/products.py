from flask import Blueprint, render_template, jsonify, request
from app.models.product import Product
from app.utils.ai_recommender import recommender

bp = Blueprint('products', __name__, url_prefix='/product')

@bp.route('/<int:product_id>')
def product_detail(product_id):
    """Product detail page with 3D viewer"""
    product = Product.query.get_or_404(product_id)
    
    # Get recommendations
    recommendations = recommender.recommend_by_similarity(product_id, limit=4)
    
    return render_template('product.html', 
                         product=product,
                         recommendations=recommendations)

@bp.route('/api/<int:product_id>')
def product_api(product_id):
    """API endpoint to get product data as JSON"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@bp.route('/category/<category_name>')
def category(category_name):
    """Get products by category"""
    products = Product.query.filter_by(category=category_name).all()
    return render_template('category.html', 
                         products=products,
                         category=category_name)

@bp.route('/api/categories')
def get_categories():
    """Get all available categories"""
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([cat[0] for cat in categories])
