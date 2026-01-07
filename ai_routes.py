from flask import Blueprint, jsonify, request
from app.utils.ai_recommender import recommender
from app.utils.ai_assistant import assistant
from app.models.product import Product

bp = Blueprint('ai', __name__, url_prefix='/api')

@bp.route('/recommend/<int:product_id>')
def recommend(product_id):
    """Get AI-powered recommendations for a product"""
    limit = request.args.get('limit', 4, type=int)
    
    recommendations = recommender.recommend_by_similarity(product_id, limit=limit)
    
    return jsonify({
        'product_id': product_id,
        'recommendations': recommendations,
        'count': len(recommendations)
    })

@bp.route('/trending')
def trending():
    """Get trending/featured products"""
    limit = request.args.get('limit', 8, type=int)
    
    trending_products = recommender.recommend_trending(limit=limit)
    
    return jsonify({
        'trending': trending_products,
        'count': len(trending_products)
    })

@bp.route('/generate-description', methods=['POST'])
def generate_description():
    """Generate product description using AI"""
    data = request.get_json()
    
    name = data.get('name', '')
    category = data.get('category', '')
    tags = data.get('tags', [])
    
    if not name or not category:
        return jsonify({'error': 'Name and category are required'}), 400
    
    description = recommender.generate_product_description(name, category, tags)
    
    return jsonify({
        'description': description
    })

@bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear recommendation cache (admin only)"""
    product_id = request.args.get('product_id', type=int)
    
    recommender.clear_cache(product_id)
    
    return jsonify({
        'message': 'Cache cleared successfully'
    })

@bp.route('/chat', methods=['POST'])
def chat():
    """AI Assistant Chat"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get some products for context
    products = Product.query.limit(5).all()
    context = ", ".join([f"{p.name} ({p.price} LE)" for p in products])
    
    response = assistant.get_response(user_message, context)
    
    return jsonify({
        'response': response
    })
