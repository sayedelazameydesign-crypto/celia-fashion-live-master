from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.models.product import Product
from app.models.article import Article
from app import db
from app.utils.ai_recommender import recommender
import cloudinary.uploader
from datetime import datetime
import re

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
def dashboard():
    """Admin dashboard"""
    total_products = Product.query.count()
    featured_count = Product.query.filter_by(featured=True).count()
    total_articles = Article.query.count()
    published_articles = Article.query.filter_by(published=True).count()
    categories = db.session.query(Product.category).distinct().all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         featured_count=featured_count,
                         total_articles=total_articles,
                         published_articles=published_articles,
                         categories=[cat[0] for cat in categories])

@bp.route('/products')
def list_products():
    """List all products"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)

@bp.route('/product/new', methods=['GET', 'POST'])
def new_product():
    """Create new product"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = float(request.form.get('price', 0))
        color = request.form.get('color')
        stock = int(request.form.get('stock', 0))
        featured = request.form.get('featured') == 'on'
        
        # Handle file uploads (if Cloudinary is configured)
        model_3d_url = request.form.get('model_3d_url')
        thumbnail_url = request.form.get('thumbnail_url')
        
        # Create product
        product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            color=color,
            stock=stock,
            featured=featured,
            model_3d_url=model_3d_url,
            thumbnail_url=thumbnail_url
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Clear cache
        recommender.clear_cache()
        
        return redirect(url_for('admin.list_products'))
    
    return render_template('admin/product_form.html')

@bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit existing product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        product.price = float(request.form.get('price', 0))
        product.color = request.form.get('color')
        product.stock = int(request.form.get('stock', 0))
        product.featured = request.form.get('featured') == 'on'
        
        # Update URLs if provided
        if request.form.get('model_3d_url'):
            product.model_3d_url = request.form.get('model_3d_url')
        if request.form.get('thumbnail_url'):
            product.thumbnail_url = request.form.get('thumbnail_url')
        
        db.session.commit()
        
        # Clear cache for this product
        recommender.clear_cache(product_id)
        
        return redirect(url_for('admin.list_products'))
    
    return render_template('admin/product_form.html', product=product)

@bp.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    # Clear cache
    recommender.clear_cache(product_id)
    
    return redirect(url_for('admin.list_products'))

@bp.route('/seed-sample-data', methods=['POST'])
def seed_sample_data():
    """Seed database with sample products"""
    sample_products = [
        {
            'name': 'قميص كلاسيكي أبيض',
            'description': 'قميص قطني أبيض أنيق مثالي للمناسبات الرسمية',
            'category': 'shirt',
            'price': 149.99,
            'color': 'white',
            'stock': 50,
            'featured': True,
            'ai_tags': ['formal', 'cotton', 'classic']
        },
        {
            'name': 'بنطلون جينز أزرق',
            'description': 'بنطلون جينز عصري بقصة مريحة',
            'category': 'pants',
            'price': 199.99,
            'color': 'blue',
            'stock': 40,
            'featured': True,
            'ai_tags': ['casual', 'denim', 'comfortable']
        },
        {
            'name': 'جاكيت شتوي أسود',
            'description': 'جاكيت شتوي دافئ وأنيق',
            'category': 'jacket',
            'price': 399.99,
            'color': 'black',
            'stock': 30,
            'featured': False,
            'ai_tags': ['winter', 'warm', 'elegant']
        }
    ]
    
    for item in sample_products:
        product = Product(**item)
        db.session.add(product)
    
    db.session.commit()
    
    return jsonify({'message': f'{len(sample_products)} sample products added'})


# ==================== ARTICLES MANAGEMENT ====================

def create_slug(title):
    """Create URL-friendly slug from title"""
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

@bp.route('/articles')
def list_articles():
    """List all articles"""
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=articles)

@bp.route('/article/new', methods=['GET', 'POST'])
def new_article():
    """Create new article"""
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')
        author_name = request.form.get('author_name', 'Admin')
        featured_image_url = request.form.get('featured_image_url')
        
        # SEO fields
        meta_description = request.form.get('meta_description')
        meta_keywords = request.form.get('meta_keywords')
        
        # Status
        published = request.form.get('published') == 'on'
        featured = request.form.get('featured') == 'on'
        
        # Tags (comma-separated)
        tags_str = request.form.get('tags', '')
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Create slug
        slug = create_slug(title)
        
        # Check if slug exists
        existing = Article.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{Article.query.count() + 1}"
        
        # Create article
        article = Article(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            category=category,
            author_name=author_name,
            featured_image_url=featured_image_url,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            published=published,
            featured=featured,
            tags=tags,
            published_at=datetime.utcnow() if published else None
        )
        
        db.session.add(article)
        db.session.commit()
        
        return redirect(url_for('admin.list_articles'))
    
    return render_template('admin/article_form.html')

@bp.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    """Edit existing article"""
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        # Update fields
        old_published = article.published
        
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.excerpt = request.form.get('excerpt')
        article.category = request.form.get('category')
        article.author_name = request.form.get('author_name', 'Admin')
        article.meta_description = request.form.get('meta_description')
        article.meta_keywords = request.form.get('meta_keywords')
        article.published = request.form.get('published') == 'on'
        article.featured = request.form.get('featured') == 'on'
        
        # Update featured image if provided
        if request.form.get('featured_image_url'):
            article.featured_image_url = request.form.get('featured_image_url')
        
        # Update tags
        tags_str = request.form.get('tags', '')
        article.tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Update slug if title changed
        new_slug = create_slug(article.title)
        if new_slug != article.slug:
            # Check if new slug exists
            existing = Article.query.filter_by(slug=new_slug).first()
            if not existing or existing.id == article.id:
                article.slug = new_slug
        
        # Set published_at if just published
        if article.published and not old_published:
            article.published_at = datetime.utcnow()
        
        db.session.commit()
        
        return redirect(url_for('admin.list_articles'))
    
    return render_template('admin/article_form.html', article=article)

@bp.route('/article/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    """Delete an article"""
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    
    return redirect(url_for('admin.list_articles'))

@bp.route('/article/toggle-publish/<int:article_id>', methods=['POST'])
def toggle_publish_article(article_id):
    """Quick toggle article publish status"""
    article = Article.query.get_or_404(article_id)
    article.published = not article.published
    
    if article.published and not article.published_at:
        article.published_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'published': article.published
    })

@bp.route('/seed-sample-articles', methods=['POST'])
def seed_sample_articles():
    """Seed database with sample articles"""
    sample_articles = [
        {
            'title': 'دليل أزياء الصيف 2025',
            'slug': 'summer-fashion-guide-2025',
            'content': '''
                <h2>أحدث صيحات الموضة لصيف 2025</h2>
                <p>اكتشف معنا أجمل وأحدث صيحات الموضة لهذا الصيف. من الألوان الزاهية إلى القصات العصرية.</p>
                <h3>الألوان الرائجة</h3>
                <p>الألوان الباستيل والنيون هي النجمة هذا الموسم.</p>
                <h3>الأقمشة المفضلة</h3>
                <p>القطن والكتان للراحة في الأيام الحارة.</p>
            ''',
            'excerpt': 'اكتشف أحدث صيحات الموضة لصيف 2025 من الألوان إلى القصات العصرية',
            'category': 'fashion',
            'author_name': 'فريق التحرير',
            'tags': ['صيف', 'موضة', '2025', 'أزياء'],
            'published': True,
            'featured': True,
            'meta_description': 'دليلك الشامل لأزياء الصيف 2025 - أحدث الصيحات والألوان',
            'published_at': datetime.utcnow()
        },
        {
            'title': 'كيف تختار الجاكيت المثالي',
            'slug': 'how-to-choose-perfect-jacket',
            'content': '''
                <h2>خطوات اختيار الجاكيت المناسب</h2>
                <p>الجاكيت قطعة أساسية في خزانة كل شخص. إليك كيفية اختيار الأفضل لك.</p>
                <h3>المقاس المناسب</h3>
                <p>تأكد من أن الجاكيت مريح عند الأكتاف ولا يضيق عند الحركة.</p>
                <h3>اللون والأسلوب</h3>
                <p>اختر ألوان محايدة للاستخدام اليومي، وألوان جريئة للمناسبات.</p>
            ''',
            'excerpt': 'نصائح عملية لاختيار الجاكيت المثالي الذي يناسب أسلوبك',
            'category': 'tips',
            'author_name': 'خبير الأزياء',
            'tags': ['جاكيت', 'نصائح', 'أسلوب'],
            'published': True,
            'featured': False,
            'meta_description': 'دليل شامل لاختيار الجاكيت المثالي - نصائح وإرشادات',
            'published_at': datetime.utcnow()
        },
        {
            'title': 'تاريخ الموضة العربية',
            'slug': 'history-of-arabic-fashion',
            'content': '''
                <h2>رحلة عبر تاريخ الأزياء العربية</h2>
                <p>من العباءة التقليدية إلى التصاميم العصرية، تعرف على تطور الموضة العربية.</p>
                <h3>الأزياء التقليدية</h3>
                <p>العباءة والجلابية والكوفية - قطع تراثية خالدة.</p>
                <h3>المصممون العرب المعاصرون</h3>
                <p>كيف أثر المصممون العرب على الموضة العالمية.</p>
            ''',
            'excerpt': 'رحلة تاريخية عبر الأزياء العربية من التقليدي إلى العصري',
            'category': 'culture',
            'author_name': 'مؤرخ الموضة',
            'tags': ['تاريخ', 'عربي', 'تراث', 'ثقافة'],
            'published': True,
            'featured': False,
            'meta_description': 'تاريخ الموضة العربية من الماضي إلى الحاضر',
            'published_at': datetime.utcnow()
        }
    ]
    
    for item in sample_articles:
        article = Article(**item)
        db.session.add(article)
    
    db.session.commit()
    
    return jsonify({'message': f'{len(sample_articles)} sample articles added'})
