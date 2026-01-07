from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from app.models.product import Product, RecommendationCache
from app import db

class AIRecommender:
    """AI-powered product recommendation system using scikit-learn"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def get_product_features(self, product):
        """Extract features from a product for comparison"""
        features = []
        
        # Add category
        if product.category:
            features.append(product.category)
        
        # Add color
        if product.color:
            features.append(product.color)
        
        # Add AI tags
        if product.ai_tags:
            features.extend(product.ai_tags)
        
        # Add description words (first 50 chars)
        if product.description:
            features.append(product.description[:50])
        
        return ' '.join(features)
    
    def recommend_by_rules(self, product, limit=4):
        """Phase 1: Rules-based recommendations"""
        recommendations = []
        
        # Rule 1: If product is a dress, recommend bags and shoes
        if 'dress' in product.category.lower() or 'فستان' in product.name:
            bags_shoes = Product.query.filter(
                (Product.category.ilike('%bag%')) | 
                (Product.category.ilike('%shoe%')) |
                (Product.category.ilike('%شنطة%')) |
                (Product.category.ilike('%جزمة%'))
            ).limit(limit).all()
            recommendations.extend(bags_shoes)
            
        # Rule 2: If color is black, recommend complementary colors
        if product.color and product.color.lower() in ['black', 'أسود']:
            complementary = Product.query.filter(
                Product.color.in_(['white', 'red', 'gold', 'أبيض', 'أحمر', 'ذهبي'])
            ).limit(limit).all()
            recommendations.extend(complementary)
            
        # Rule 3: If Soiree/Evening, recommend accessories
        if any(tag in (product.ai_tags or []) for tag in ['soiree', 'evening', 'سواريه']):
            accessories = Product.query.filter(
                Product.category.ilike('%accessory%') | Product.category.ilike('%إكسسوار%')
            ).limit(limit).all()
            recommendations.extend(accessories)
            
        return [p.to_dict() for p in recommendations[:limit]]

    def recommend_by_similarity(self, product_id, limit=4):
        """
        Recommend products using cosine similarity
        Based on category, color, tags, and description
        """
        # Get the target product
        target_product = Product.query.get(product_id)
        if not target_product:
            return []

        # Try rules-based first
        rules_recommendations = self.recommend_by_rules(target_product, limit)
        if len(rules_recommendations) >= limit:
            return rules_recommendations
            
        
        # Check cache first
        cache = RecommendationCache.query.filter_by(product_id=product_id).first()
        if cache and cache.recommended_ids:
            # Return cached recommendations
            products = Product.query.filter(Product.id.in_(cache.recommended_ids)).all()
            return [p.to_dict() for p in products[:limit]]
        
        # Get the target product
        target_product = Product.query.get(product_id)
        if not target_product:
            return []
        
        # Get all products except the target
        all_products = Product.query.filter(Product.id != product_id).all()
        
        if not all_products:
            return []
        
        try:
            # Create feature strings for all products
            product_list = [target_product] + all_products
            features = [self.get_product_features(p) for p in product_list]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(features)
            
            # Calculate cosine similarity
            cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Get indices of most similar products
            similar_indices = cosine_similarities.argsort()[-limit:][::-1]
            
            # Get recommended products
            recommended_products = [all_products[i] for i in similar_indices]
            recommended_ids = [p.id for p in recommended_products]
            
            # Cache the results
            if cache:
                cache.recommended_ids = recommended_ids
            else:
                cache = RecommendationCache(
                    product_id=product_id,
                    recommended_ids=recommended_ids
                )
                db.session.add(cache)
            
            db.session.commit()
            
            return [p.to_dict() for p in recommended_products]
            
        except Exception as e:
            print(f"Error in similarity recommendation: {e}")
            # Fallback to simple category-based recommendation
            return self.recommend_by_category(product_id, limit)
    
    def recommend_by_category(self, product_id, limit=4):
        """Simple fallback: recommend products from the same category"""
        product = Product.query.get(product_id)
        if not product:
            return []
        
        similar = Product.query.filter(
            Product.category == product.category,
            Product.id != product.id
        ).limit(limit).all()
        
        return [p.to_dict() for p in similar]
    
    def recommend_trending(self, limit=8):
        """Get trending/featured products"""
        trending = Product.query.filter_by(featured=True).limit(limit).all()
        
        # If not enough featured products, get latest ones
        if len(trending) < limit:
            latest = Product.query.order_by(Product.created_at.desc()).limit(limit).all()
            trending = list(set(trending + latest))[:limit]
        
        return [p.to_dict() for p in trending]
    
    def generate_product_description(self, name, category, tags=None):
        """
        Generate marketing description for a product using OpenAI
        Includes SEO optimization and Egyptian market tone
        """
        from app.utils.ai_assistant import assistant
        
        prompt = f"""
        اكتب وصف لمنتج ملابس بالمواصفات دي:
        الاسم: {name}
        الفئة: {category}
        المميزات: {', '.join(tags) if tags else 'جودة عالية، تصميم عصري'}
        
        المطلوب:
        1. وصف قصير (بيع) بلهجة مصرية ودودة.
        2. وصف طويل (SEO) باللغة العربية الفصحى البسيطة.
        3. ركز على الـ Benefits مش الـ Features بس.
        4. مناسب للسوق المصري.
        """
        
        try:
            response = assistant.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "أنت خبير SEO وكتابة محتوى تسويقي لبراندات الموضة في مصر."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except:
            return f"{name} - قطعة مميزة من {category}، جودة عالية وتصميم يجنن هيخليكي متألقة في كل وقت."
    
    def clear_cache(self, product_id=None):
        """Clear recommendation cache"""
        if product_id:
            RecommendationCache.query.filter_by(product_id=product_id).delete()
        else:
            RecommendationCache.query.delete()
        db.session.commit()

# Global instance
recommender = AIRecommender()
