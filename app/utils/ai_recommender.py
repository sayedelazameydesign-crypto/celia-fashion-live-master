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
    
    def recommend_by_similarity(self, product_id, limit=4):
        """
        Recommend products using cosine similarity
        Based on category, color, tags, and description
        """
        
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
        Generate marketing description for a product
        Simple template-based approach (can be upgraded to GPT later)
        """
        templates = {
            'shirt': f"تعرف على {name} - قميص أنيق من فئة {category}. مثالي للارتداء اليومي والمناسبات الخاصة.",
            'pants': f"بنطلون {name} الرائع - تصميم عصري ومريح من فئة {category}. جودة عالية وأناقة لا مثيل لها.",
            'jacket': f"جاكيت {name} المميز - دفء وأناقة في تصميم واحد. من مجموعة {category} الفاخرة.",
            'dress': f"فستان {name} الساحر - أناقة وجمال يلفتان الأنظار. تصميم {category} فريد من نوعه.",
            'default': f"{name} - منتج مميز من فئة {category}. جودة عالية وتصميم عصري."
        }
        
        description = templates.get(category.lower(), templates['default'])
        
        if tags:
            description += f" يتميز بـ: {', '.join(tags)}."
        
        return description
    
    def clear_cache(self, product_id=None):
        """Clear recommendation cache"""
        if product_id:
            RecommendationCache.query.filter_by(product_id=product_id).delete()
        else:
            RecommendationCache.query.delete()
        db.session.commit()

# Global instance
recommender = AIRecommender()
