# 🔌 أمثلة استخدام API

## نظرة عامة

المتجر يوفر REST API للحصول على البيانات برمجياً.

---

## 🛒 المنتجات

### 1. الحصول على منتج بـ ID

```bash
GET /product/api/1
```

**Response:**
```json
{
  "id": 1,
  "name": "قميص كلاسيكي أبيض",
  "description": "قميص قطني أنيق...",
  "category": "shirt",
  "price": 149.99,
  "color": "white",
  "available_colors": ["white", "blue", "black"],
  "model_3d_url": "https://res.cloudinary.com/...",
  "thumbnail_url": "https://res.cloudinary.com/...",
  "ai_tags": ["formal", "cotton", "classic"],
  "stock": 50,
  "featured": true,
  "created_at": "2025-11-12T10:30:00"
}
```

### 2. الحصول على جميع الفئات

```bash
GET /product/api/categories
```

**Response:**
```json
["shirt", "pants", "jacket", "dress"]
```

---

## 🤖 التوصيات الذكية

### 1. الحصول على توصيات لمنتج

```bash
GET /api/recommend/1?limit=4
```

**Response:**
```json
{
  "product_id": 1,
  "recommendations": [
    {
      "id": 2,
      "name": "قميص أزرق",
      "price": 159.99,
      "category": "shirt",
      "thumbnail_url": "..."
    },
    {
      "id": 5,
      "name": "قميص رمادي",
      "price": 139.99,
      "category": "shirt",
      "thumbnail_url": "..."
    }
  ],
  "count": 2
}
```

### 2. الحصول على المنتجات المميزة/الرائجة

```bash
GET /api/trending?limit=8
```

**Response:**
```json
{
  "trending": [
    {
      "id": 1,
      "name": "قميص كلاسيكي",
      "price": 149.99,
      "featured": true,
      "thumbnail_url": "..."
    }
  ],
  "count": 1
}
```

### 3. توليد وصف منتج بالـ AI

```bash
POST /api/generate-description
Content-Type: application/json

{
  "name": "قميص صيفي",
  "category": "shirt",
  "tags": ["summer", "cotton", "casual"]
}
```

**Response:**
```json
{
  "description": "تعرف على قميص صيفي - قميص أنيق من فئة shirt. مثالي للارتداء اليومي والمناسبات الخاصة. يتميز بـ: summer, cotton, casual."
}
```

---

## 🧪 أمثلة بـ Python

### استخدام requests

```python
import requests

# 1. الحصول على منتج
response = requests.get('http://localhost:5000/product/api/1')
product = response.json()
print(f"المنتج: {product['name']}, السعر: {product['price']}")

# 2. الحصول على توصيات
response = requests.get('http://localhost:5000/api/recommend/1?limit=4')
data = response.json()
print(f"عدد التوصيات: {data['count']}")

for rec in data['recommendations']:
    print(f"- {rec['name']}: {rec['price']} ر.س")

# 3. توليد وصف
payload = {
    "name": "فستان أنيق",
    "category": "dress",
    "tags": ["elegant", "party", "silk"]
}
response = requests.post(
    'http://localhost:5000/api/generate-description',
    json=payload
)
result = response.json()
print(f"الوصف المولد: {result['description']}")
```

---

## 🌐 أمثلة بـ JavaScript

### استخدام Fetch API

```javascript
// 1. الحصول على منتج
async function getProduct(productId) {
    const response = await fetch(`/product/api/${productId}`);
    const product = await response.json();
    console.log(`المنتج: ${product.name}, السعر: ${product.price}`);
    return product;
}

// 2. الحصول على توصيات
async function getRecommendations(productId, limit = 4) {
    const response = await fetch(`/api/recommend/${productId}?limit=${limit}`);
    const data = await response.json();
    
    console.log(`عدد التوصيات: ${data.count}`);
    data.recommendations.forEach(rec => {
        console.log(`- ${rec.name}: ${rec.price} ر.س`);
    });
    
    return data.recommendations;
}

// 3. الحصول على المنتجات الرائجة
async function getTrending(limit = 8) {
    const response = await fetch(`/api/trending?limit=${limit}`);
    const data = await response.json();
    return data.trending;
}

// 4. عرض التوصيات في الصفحة
async function displayRecommendations(productId) {
    const recommendations = await getRecommendations(productId);
    
    const container = document.getElementById('recommendations');
    container.innerHTML = recommendations.map(product => `
        <div class="product-card">
            <img src="${product.thumbnail_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>${product.price} ر.س</p>
        </div>
    `).join('');
}

// استدعاء
displayRecommendations(1);
```

---

## 📱 أمثلة بـ cURL

### 1. الحصول على منتج

```bash
curl -X GET http://localhost:5000/product/api/1
```

### 2. الحصول على توصيات

```bash
curl -X GET "http://localhost:5000/api/recommend/1?limit=4"
```

### 3. توليد وصف

```bash
curl -X POST http://localhost:5000/api/generate-description \
  -H "Content-Type: application/json" \
  -d '{
    "name": "جاكيت شتوي",
    "category": "jacket",
    "tags": ["winter", "warm", "wool"]
  }'
```

### 4. مسح الكاش

```bash
curl -X POST "http://localhost:5000/api/clear-cache?product_id=1"
```

---

## 🔐 الأمان (للتطوير المستقبلي)

حالياً، API مفتوح للجميع. لإضافة أمان:

```python
# في app/routes/api_routes.py

from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-key':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/api/recommend/<int:product_id>')
@require_api_key
def recommend(product_id):
    # ...
```

**الاستخدام:**
```bash
curl -X GET http://localhost:5000/api/recommend/1 \
  -H "X-API-Key: your-secret-key"
```

---

## 📊 معدلات الاستخدام (Rate Limiting)

للحماية من الإساءة (يمكن إضافته لاحقاً):

```python
# تثبيت Flask-Limiter
pip install Flask-Limiter

# في app/__init__.py
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

# في routes
@bp.route('/api/recommend/<int:product_id>')
@limiter.limit("10 per minute")
def recommend(product_id):
    # ...
```

---

## 🧪 اختبار API

### باستخدام Python unittest

```python
import unittest
from app import create_app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_get_product(self):
        response = self.client.get('/product/api/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('name', data)
    
    def test_get_recommendations(self):
        response = self.client.get('/api/recommend/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('recommendations', data)

if __name__ == '__main__':
    unittest.main()
```

---

## 📚 توثيق إضافي

### Postman Collection

يمكنك استيراد هذه الطلبات في Postman:

```json
{
  "info": {
    "name": "E-commerce AI 3D API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Product",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/product/api/1"
      }
    },
    {
      "name": "Get Recommendations",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/api/recommend/1?limit=4"
      }
    },
    {
      "name": "Generate Description",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/generate-description",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"name\":\"قميص\",\"category\":\"shirt\",\"tags\":[\"cotton\"]}"
        }
      }
    }
  ]
}
```

---

## 🎯 حالات الاستخدام

### 1. تطبيق موبايل

```javascript
// في React Native / Flutter
async function fetchProducts() {
    const response = await fetch('https://your-site.onrender.com/api/trending');
    const data = await response.json();
    return data.trending;
}
```

### 2. Widget خارجي

```html
<!-- عرض منتجات موقعك في موقع آخر -->
<div id="products-widget"></div>
<script>
fetch('https://your-site.onrender.com/api/trending?limit=3')
    .then(res => res.json())
    .then(data => {
        const html = data.trending.map(p => `
            <div>
                <img src="${p.thumbnail_url}">
                <h4>${p.name}</h4>
                <p>${p.price} ر.س</p>
            </div>
        `).join('');
        document.getElementById('products-widget').innerHTML = html;
    });
</script>
```

### 3. Chatbot Integration

```python
# دمج مع Telegram Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler

def recommend_command(update, context):
    product_id = context.args[0]
    response = requests.get(f'http://your-site/api/recommend/{product_id}')
    data = response.json()
    
    message = "توصيات لك:\n"
    for rec in data['recommendations']:
        message += f"- {rec['name']}: {rec['price']} ر.س\n"
    
    update.message.reply_text(message)
```

---

**مستعد للانطلاق مع API! 🚀**
