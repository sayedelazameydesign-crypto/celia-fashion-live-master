from flask import Blueprint, render_template, request
from app.models.article import Article

bp = Blueprint('blog', __name__, url_prefix='/blog')

@bp.route('/')
def index():
    """Blog homepage with all articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    # Get published articles only
    pagination = Article.query.filter_by(published=True).order_by(
        Article.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    articles = pagination.items
    
    # Get featured articles
    featured = Article.query.filter_by(published=True, featured=True).limit(3).all()
    
    return render_template('blog/index.html', 
                         articles=articles,
                         featured=featured,
                         pagination=pagination)

@bp.route('/<slug>')
def article_detail(slug):
    """Single article page"""
    article = Article.query.filter_by(slug=slug, published=True).first_or_404()
    
    # Increment views
    article.views += 1
    from app import db
    db.session.commit()
    
    # Get related articles (same category)
    related = Article.query.filter(
        Article.category == article.category,
        Article.id != article.id,
        Article.published == True
    ).limit(3).all()
    
    return render_template('blog/article.html', 
                         article=article,
                         related=related)

@bp.route('/category/<category_name>')
def category(category_name):
    """Articles by category"""
    articles = Article.query.filter_by(
        category=category_name,
        published=True
    ).order_by(Article.published_at.desc()).all()
    
    return render_template('blog/category.html',
                         articles=articles,
                         category=category_name)

@bp.route('/search')
def search():
    """Search articles"""
    query = request.args.get('q', '')
    
    articles = Article.query.filter(
        Article.published == True,
        (Article.title.ilike(f'%{query}%')) | 
        (Article.content.ilike(f'%{query}%'))
    ).all()
    
    return render_template('blog/search.html',
                         articles=articles,
                         query=query)
