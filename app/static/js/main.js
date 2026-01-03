// Shopping Cart Management
class ShoppingCart {
    constructor() {
        this.items = this.loadCart();
        this.updateCartUI();
    }
    
    loadCart() {
        const saved = localStorage.getItem('cart');
        return saved ? JSON.parse(saved) : [];
    }
    
    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
        this.updateCartUI();
    }
    
    addItem(product) {
        const existing = this.items.find(item => item.id === product.id);
        if (existing) {
            existing.quantity += 1;
        } else {
            this.items.push({...product, quantity: 1});
        }
        this.saveCart();
        this.showNotification('تم إضافة المنتج إلى السلة');
    }
    
    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveCart();
    }
    
    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            item.quantity = quantity;
            if (quantity <= 0) {
                this.removeItem(productId);
            }
        }
        this.saveCart();
    }
    
    getTotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }
    
    updateCartUI() {
        const countElement = document.getElementById('cart-count');
        if (countElement) {
            const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
            countElement.textContent = totalItems;
        }
    }
    
    showNotification(message) {
        // Simple notification (can be enhanced with toast library)
        const notification = document.createElement('div');
        notification.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        gsap.from(notification, {
            y: -50,
            opacity: 0,
            duration: 0.3
        });
        
        setTimeout(() => {
            gsap.to(notification, {
                y: -50,
                opacity: 0,
                duration: 0.3,
                onComplete: () => notification.remove()
            });
        }, 2000);
    }
}

// Initialize cart
const cart = new ShoppingCart();

// Add to cart button handler
function addToCart(productId, productName, productPrice) {
    cart.addItem({
        id: productId,
        name: productName,
        price: productPrice
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Page load animations
window.addEventListener('load', () => {
    gsap.from('.card-hover', {
        y: 50,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: 'power2.out'
    });
});

// Search functionality
function handleSearch(event) {
    event.preventDefault();
    const query = document.getElementById('search-input').value;
    if (query) {
        window.location.href = `/search?q=${encodeURIComponent(query)}`;
    }
}

// Load recommendations
async function loadRecommendations(productId) {
    try {
        const response = await fetch(`/api/recommend/${productId}`);
        const data = await response.json();
        
        const container = document.getElementById('recommendations');
        if (container && data.recommendations) {
            container.innerHTML = data.recommendations.map(product => `
                <div class="card-hover bg-white rounded-lg shadow-lg overflow-hidden">
                    <a href="/product/${product.id}">
                        <img src="${product.thumbnail_url || '/static/images/placeholder.png'}" 
                             alt="${product.name}" 
                             class="w-full h-48 object-cover">
                        <div class="p-4">
                            <h3 class="font-bold text-gray-800">${product.name}</h3>
                            <p class="text-purple-600 font-bold mt-2">${product.price} ر.س</p>
                        </div>
                    </a>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

// Mobile menu toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

console.log('✅ Main JavaScript loaded');
