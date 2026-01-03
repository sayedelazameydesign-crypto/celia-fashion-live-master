from flask import Blueprint, jsonify, request
from app.utils.ai_recommender import recommender
from app.ai.assistant import chat_assistant

bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@bp.route('/recommend/<int:product_id>')
def recommend(product_id):
    """Get AI-powered recommendations for a product"""
    limit = request.args.get('limit', 8, type=int)
    
    recommendations = recommender.get_product_page_recommendations(product_id, limit=limit)
    
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
    """Handle incoming messages for the AI chat assistant"""
    data = request.get_json()
    message = data.get('message', '')
    session_data = data.get('session_data', {})

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    response = chat_assistant.get_response(message, session_data)

    return jsonify(response)

@bp.route('/product-seo', methods=['POST'])
def product_seo():
    """Generate SEO content for a product"""
    data = request.get_json()

    name = data.get('name')
    category = data.get('category')
    color = data.get('color')
    material = data.get('material')

    if not all([name, category]):
        return jsonify({'error': 'Name and category are required'}), 400

    seo_content = recommender.generate_product_seo(name, category, color, material)

    return jsonify(seo_content)
