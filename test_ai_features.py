# test_ai_features.py
import os
import unittest
from app import create_app, db
from app.models.product import Product
from app.utils.ai_recommender import recommender
from app.ai.assistant import chat_assistant

class AIFeaturesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and a test database."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create dummy data
        self._create_dummy_data()

    def tearDown(self):
        """Tear down the test database and the app context."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_dummy_data(self):
        """Create dummy products for testing."""
        products = [
            Product(id=1, name='Classic T-Shirt', category='shirt', price=150.0, color='black', material='cotton', sizes=['S', 'M', 'L']),
            Product(id=2, name='Summer Dress', category='dress', price=350.0, color='red', material='silk', sizes=['M', 'L']),
            Product(id=3, name='Leather Bag', category='bag', price=500.0, color='brown'),
            Product(id=4, name='High Heels', category='shoes', price=450.0, color='black'),
            Product(id=5, name='White Blouse', category='shirt', price=250.0, color='white', material='cotton'),
            Product(id=6, name='Blue Jeans', category='pants', price=400.0, color='blue', material='denim'),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()

    def test_01_chat_assistant_greeting(self):
        """Test the chat assistant's greeting response."""
        response = chat_assistant.get_response("أهلاً")
        self.assertIn("أهلاً بيكي", response['reply'])

    def test_02_chat_assistant_static_questions(self):
        """Test the chat assistant's responses to static questions."""
        test_cases = {
            "ما هو سعر الفستان؟": "أسعارنا تنافسية",
            "ما هي المقاسات المتوفرة؟": "عندنا كل المقاسات",
            "ما هي خامات البلوزة؟": "بنستخدم أجود الخامات",
            "متى يتم التوصيل؟": "التوصيل متاح لكل محافظات مصر",
            "هل يمكن الاسترجاع؟": "تقدري تسترجعي أو تستبدلي"
        }
        for message, expected in test_cases.items():
            response = chat_assistant.get_response(message)
            self.assertIn(expected, response['reply'])

    def test_03_rule_based_recommendations_for_dress(self):
        """Test the rule-based recommendations for a dress."""
        # Product ID 2 is a dress
        recommendations = recommender.recommend_by_rules(2, limit=4)

        categories = [rec['category'] for rec in recommendations]
        self.assertIn('bag', categories)
        self.assertIn('shoes', categories)

        colors = [rec['color'] for rec in recommendations]
        self.assertIn('black', colors, "Complementary color 'black' for 'red' dress should be recommended")

    def test_04_product_seo_generation(self):
        """Test the product SEO content generation."""
        seo_content = recommender.generate_product_seo("فستان سهرة", "dress", "أحمر", "حرير")

        self.assertIn("فستان سهرة", seo_content['meta_title'])
        self.assertTrue(len(seo_content['meta_title']) <= 60)
        self.assertIn("تسوقي الآن", seo_content['meta_description'])
        self.assertTrue(len(seo_content['meta_description']) <= 160)
        self.assertIn("جددي ستايلك", seo_content['description_ar'])
        self.assertIn("Elevate your style", seo_content['description_en'])
        self.assertIn("صورة فستان سهرة", seo_content['alt_text'])

    def test_05_api_endpoints(self):
        """Test the API endpoints for chat, recommendations, and SEO."""

        # Test /api/ai/chat
        chat_response = self.client.post('/api/ai/chat', json={'message': 'hello'})
        self.assertEqual(chat_response.status_code, 200)
        self.assertIn('reply', chat_response.json)

        # Test /api/ai/recommend/<id>
        rec_response = self.client.get('/api/ai/recommend/2')
        self.assertEqual(rec_response.status_code, 200)
        self.assertIn('recommendations', rec_response.json)

        # Test /api/ai/product-seo
        seo_response = self.client.post('/api/ai/product-seo', json={
            'name': 'Elegant Blouse',
            'category': 'shirt',
            'color': 'white',
            'material': 'silk'
        })
        self.assertEqual(seo_response.status_code, 200)
        self.assertIn('meta_title', seo_response.json)

if __name__ == '__main__':
    # You need to configure the testing database URI in your config
    # For example, in config.py:
    # class TestingConfig(Config):
    #     TESTING = True
    #     SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'

    unittest.main()
