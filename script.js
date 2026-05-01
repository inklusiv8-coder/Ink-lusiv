// ================== Supabase Configuration ==================
const SUPABASE_URL = 'https://tkjwwtwtjatcbdxvwwzu.supabase.co';
// Use a valid Supabase anon/public key only if you want browser-side fallback.
// Otherwise the backend route /api/products will be used on localhost or a server host.
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRmand3dHd0amF0Y2JkeHZ3d3p1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MDY4MDAsImV4cCI6MjA5Mjk4MjgwMH0.YHq7dXiiJNJrbm1m2FRtKzgqnQeT-OFci6I7dC2mwbs';
const SUPABASE_FALLBACK_ENABLED = false;

const supabaseClient = SUPABASE_FALLBACK_ENABLED && window.supabase
    ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
    : null;

// ================== Hero Advert Carousel ==================
const carouselImages = [
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS0XRWj0Xp3r4FF2VvQDLR3YGB0gyM5KqF-8Q&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ3kczDLPkgSnYsoYyw3xBRLo4kVO_vY40ZzQ&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTw4ZeVCF54bTMABmlD5rUlXwwYviLo5dWEHQ&s',
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQovQT17An2mhnBe34nyZfTS8E0ePIR3ZuFnQ&s'
];

let currentCarouselIndex = 0;

function initCarousel() {
    const dotsContainer = document.getElementById('carouselDots');
    
    // Create dots
    carouselImages.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.className = 'carousel-dot' + (index === 0 ? ' active' : '');
        dot.onclick = () => goToSlide(index);
        dotsContainer.appendChild(dot);
    });

    // Set initial background
    setHeroBackground(carouselImages[0]);
    
    // Auto rotate carousel
    setInterval(() => {
        currentCarouselIndex = (currentCarouselIndex + 1) % carouselImages.length;
        updateCarousel();
    }, 5000); // Change image every 5 seconds
}

function setHeroBackground(imageUrl) {
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.backgroundImage = `linear-gradient(135deg, rgba(245,241,232,0.35) 0%, rgba(232,220,200,0.25) 50%, rgba(212,165,116,0.2) 100%), url('${imageUrl}')`;
        hero.style.backgroundSize = 'cover';
        hero.style.backgroundPosition = 'center';
        hero.style.backgroundRepeat = 'no-repeat';
    }
}

function updateCarousel() {
    setHeroBackground(carouselImages[currentCarouselIndex]);
    const dots = document.querySelectorAll('.carousel-dot');
    dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentCarouselIndex);
    });
}

function goToSlide(index) {
    currentCarouselIndex = index;
    updateCarousel();
}

// Change hero image with button navigation
function changeHeroImage(direction) {
    currentCarouselIndex = (currentCarouselIndex + direction + carouselImages.length) % carouselImages.length;
    updateCarousel();
}

// Check and update AI chat indicator
function updateChatIndicator() {
    const whatsappChats = JSON.parse(localStorage.getItem('whatsappChats') || '[]');
    const chatModalTitle = document.getElementById('chatModalTitle');
    const chatIndicator = document.getElementById('chatIndicator');
    const whatsappBtn = document.getElementById('whatsappBtn');
    
    if (whatsappChats && whatsappChats.length > 0) {
        if (chatModalTitle) chatModalTitle.textContent = 'Chat with Main Customer Service';
        if (chatIndicator) {
            chatIndicator.style.display = 'block';
            chatIndicator.style.backgroundColor = '#4CAF50';
        }
        if (whatsappBtn) whatsappBtn.title = 'Chat with Main Customer Service';
    } else {
        if (chatModalTitle) chatModalTitle.textContent = 'AI Assistant';
        if (chatIndicator) chatIndicator.style.display = 'none';
        if (whatsappBtn) whatsappBtn.title = 'Chat with AI Assistant';
    }
}

// ================== Product Data ==================
let products = [];

async function fetchProductsFromSupabase(filter = 'all') {
    if (!supabaseClient) {
        throw new Error('Supabase client not available');
    }

    const validCategories = { 'leather': 'products_leather', 'metal': 'products_metal', 'silicone': 'products_silicone' };

    try {
        let allProducts = [];

        if (filter === 'all') {
            // Fetch from all three tables
            for (const [category, tableName] of Object.entries(validCategories)) {
                const { data, error } = await supabaseClient
                    .from(tableName)
                    .select('*');

                if (error) {
                    console.error(`Error fetching ${category} products:`, error);
                    continue;
                }

                // Normalize the data to match expected format
                const normalizedProducts = (data || []).map(product => ({
                    ...product,
                    category: category,
                    id: product.id || product.product_id,
                    name: product.name || product.product_name,
                    price: product.price || product.product_price,
                    originalPrice: product.original_price || product.price,
                    rating: product.rating || 4.5,
                    reviews: product.reviews || 0,
                    description: product.description || '',
                    image: product.image || product.image_url,
                    specs: product.specs || {}
                }));

                allProducts.push(...normalizedProducts);
            }
        } else if (validCategories[filter]) {
            // Fetch from specific category table
            const tableName = validCategories[filter];
            const { data, error } = await supabaseClient
                .from(tableName)
                .select('*');

            if (error) {
                throw error;
            }

            // Normalize the data
            allProducts = (data || []).map(product => ({
                ...product,
                category: filter,
                id: product.id || product.product_id,
                name: product.name || product.product_name,
                price: product.price || product.product_price,
                originalPrice: product.original_price || product.price,
                rating: product.rating || 4.5,
                reviews: product.reviews || 0,
                description: product.description || '',
                image: product.image || product.image_url,
                specs: product.specs || {}
            }));
        }

        return allProducts;
    } catch (error) {
        console.error('Supabase fetch error:', error);
        throw error;
    }
}

async function fetchProducts(filter = 'all') {
    let data = null;
    const useApi = !window.location.hostname.includes('github.io') && !window.location.protocol.startsWith('file');

    if (useApi) {
        try {
            const response = await fetch(`/api/products?category=${encodeURIComponent(filter)}`);
            if (response.ok) {
                data = await response.json();
            } else {
                console.warn('Backend API returned non-ok status:', response.status);
            }
        } catch (error) {
            console.warn('Backend API unavailable, falling back to Supabase/local JSON:', error);
        }
    }

    // If API failed or is unavailable, optionally try Supabase directly as a fallback
    if (!data && SUPABASE_FALLBACK_ENABLED && supabaseClient) {
        try {
            data = await fetchProductsFromSupabase(filter);
        } catch (supabaseError) {
            console.error('Supabase fetch error:', supabaseError);
        }
    } else if (!data && !useApi && !SUPABASE_FALLBACK_ENABLED) {
        console.info('Skipping direct Supabase fallback; using local JSON fallback instead.');
    }

    // Final fallback to local JSON
    if (!data) {
        try {
            const scriptEl = document.querySelector('script[src*="script.js"]');
            const scriptBase = scriptEl
                ? scriptEl.src.replace(/\/[^\/]*$/, '/')
                : `${window.location.origin}${window.location.pathname.replace(/\/[^\/]*$/, '/')}`;
            const pageBase = `${window.location.origin}${window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname.replace(/\/[^\/]*$/, '/')}`;
            const pathSegments = window.location.pathname.split('/').filter(Boolean);
            const repoBase = pathSegments.length > 0
                ? `${window.location.origin}/${pathSegments[0]}/`
                : `${window.location.origin}/`;

            const fallbackPaths = Array.from(new Set([
                new URL('data/products.json', scriptBase).href,
                new URL('./data/products.json', pageBase).href,
                new URL('/data/products.json', window.location.origin).href,
                new URL('data/products.json', repoBase).href,
                new URL('../data/products.json', pageBase).href,
            ]));

            let fallbackResponse = null;
            for (let i = 0; i < fallbackPaths.length && !data; i++) {
                const path = fallbackPaths[i];
                try {
                    fallbackResponse = await fetch(path);
                    if (fallbackResponse.ok) {
                        data = await fallbackResponse.json();
                    } else {
                        console.warn('Local product JSON fetch failed:', fallbackResponse.status, fallbackResponse.statusText, 'path:', path);
                    }
                } catch (err) {
                    console.warn('Error fetching local product JSON path:', path, err);
                }
            }

            if (!data) {
                data = [];
            }
        } catch (fallbackError) {
            console.error(fallbackError);
            showNotification('Unable to load products data.', 'error');
            products = [];
            currentFilter = filter;
            currentPage = 1;
            displayProducts();
            return;
        }
    }

    if (!data) {
        data = [];
    }

    products = Array.isArray(data)
        ? data
        : Array.isArray(data.products)
            ? data.products
            : [];

    if (filter !== 'all') {
        products = products.filter(product => String(product.category || '').toLowerCase() === filter.toLowerCase());
    }

    currentFilter = filter;
    currentPage = 1;
    displayProducts();
}

// ================== Cart Management ==================
let currentFilter = 'all';
let currentPage = 1;
const productsPerPage = 4;
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function addToCart(product, quantity = 1) {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            ...product,
            quantity: quantity
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showNotification('Added to cart!');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCart();
}

function updateCartCount() {
    const cartCount = document.querySelector('.cart-count');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
}

function displayCart() {
    const cartItemsContainer = document.getElementById('cartItems');
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        document.getElementById('subtotal').textContent = '$0.00';
        document.getElementById('total').textContent = '$5.00';
        return;
    }
    
    cartItemsContainer.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)} x ${item.quantity}</div>
            </div>
            <button class="cart-item-remove" onclick="removeFromCart(${item.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
    
    updateCartTotals();
}

function updateCartTotals() {
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = cart.length > 0 ? 1000 : 0;
    const total = subtotal + shipping;
    
    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('shipping').textContent = `$${shipping.toFixed(2)}`;
    document.getElementById('total').textContent = `$${total.toFixed(2)}`;
}

// ================== Checkout Functions ==================
function showCheckout() {
    if (cart.length === 0) {
        showNotification('Your cart is empty!', 'error');
        return;
    }
    
    // Hide cart modal and show checkout section
    document.getElementById('cartModal').style.display = 'none';
    document.getElementById('checkout').style.display = 'block';
    
    // Scroll to checkout section
    document.getElementById('checkout').scrollIntoView({ behavior: 'smooth' });
    
    // Populate checkout with cart items
    displayCheckoutItems();
    updateCheckoutTotals();
    
    // Pre-fill form with user data if logged in
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (currentUser) {
        document.getElementById('firstName').value = currentUser.fullName.split(' ')[0] || '';
        document.getElementById('lastName').value = currentUser.fullName.split(' ').slice(1).join(' ') || '';
        document.getElementById('email').value = currentUser.email || '';
        document.getElementById('phone').value = currentUser.phoneNumber || '';
        document.getElementById('address').value = currentUser.address || '';
        document.getElementById('city').value = currentUser.city || '';
        document.getElementById('zipCode').value = currentUser.zipCode || '';
    }
}

function showCheckoutFromNav() {
    document.getElementById('checkout').style.display = 'block';
    document.getElementById('checkout').scrollIntoView({ behavior: 'smooth' });
    
    if (cart.length === 0) {
        showNotification('Your cart is empty! Add some items to proceed with checkout.', 'error');
        // Still show the checkout section but with empty cart message
        displayCheckoutItems();
        updateCheckoutTotals();
        return;
    }
    
    // Populate checkout with cart items
    displayCheckoutItems();
    updateCheckoutTotals();
    
    // Pre-fill form with user data if logged in
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (currentUser) {
        document.getElementById('firstName').value = currentUser.fullName.split(' ')[0] || '';
        document.getElementById('lastName').value = currentUser.fullName.split(' ').slice(1).join(' ') || '';
        document.getElementById('email').value = currentUser.email || '';
        document.getElementById('phone').value = currentUser.phoneNumber || '';
        document.getElementById('address').value = currentUser.address || '';
        document.getElementById('city').value = currentUser.city || '';
        document.getElementById('zipCode').value = currentUser.zipCode || '';
    }
}

function backToCart() {
    document.getElementById('checkout').style.display = 'none';
    document.getElementById('cartModal').style.display = 'block';
}

function displayCheckoutItems() {
    const checkoutItemsContainer = document.getElementById('checkoutItems');
    
    if (cart.length === 0) {
        checkoutItemsContainer.innerHTML = '<p class="empty-checkout">Your cart is empty. <a href="#products" onclick="document.getElementById(\'products\').scrollIntoView({behavior: \'smooth\'})">Browse our products</a> to add items.</p>';
        return;
    }
    
    checkoutItemsContainer.innerHTML = cart.map(item => `
        <div class="checkout-item">
            <div class="checkout-item-details">
                <div class="checkout-item-name">${item.name} x ${item.quantity}</div>
                <div class="checkout-item-price">$${item.price.toFixed(2)} each</div>
            </div>
            <div class="checkout-item-total">$${(item.price * item.quantity).toFixed(2)}</div>
        </div>
    `).join('');
}

function updateCheckoutTotals() {
    const placeOrderBtn = document.getElementById('placeOrderBtn');
    
    if (cart.length === 0) {
        document.getElementById('checkoutSubtotal').textContent = '$0.00';
        document.getElementById('checkoutShipping').textContent = '$0.00';
        document.getElementById('checkoutTax').textContent = '$0.00';
        document.getElementById('checkoutTotal').textContent = '$0.00';
        placeOrderBtn.disabled = true;
        placeOrderBtn.textContent = 'Cart is Empty';
        placeOrderBtn.style.opacity = '0.5';
        return;
    }
    
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = subtotal > 50 ? 0 : 5;
    const tax = subtotal * 0.08; // 8% tax
    const total = subtotal + shipping + tax;
    
    document.getElementById('checkoutSubtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('checkoutShipping').textContent = shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`;
    document.getElementById('checkoutTax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('checkoutTotal').textContent = `$${total.toFixed(2)}`;
    
    placeOrderBtn.disabled = false;
    placeOrderBtn.textContent = 'Place Order';
    placeOrderBtn.style.opacity = '1';
}

function toggleCardDetails() {
    const paymentMethod = document.getElementById('paymentMethod').value;
    const cardDetails = document.getElementById('cardDetails');
    
    if (paymentMethod === 'card') {
        cardDetails.style.display = 'block';
    } else {
        cardDetails.style.display = 'none';
    }
}

async function placeOrder() {
    if (cart.length === 0) {
        showNotification('Your cart is empty! Add some items before placing an order.', 'error');
        return;
    }
    
    const form = document.getElementById('checkoutForm');
    
    // Basic form validation
    if (!form.checkValidity()) {
        showNotification('Please fill in all required fields!', 'error');
        return;
    }
    
    const paymentMethod = document.getElementById('paymentMethod').value;
    if (!paymentMethod) {
        showNotification('Please select a payment method!', 'error');
        return;
    }
    
    if (paymentMethod === 'card') {
        const cardNumber = document.getElementById('cardNumber').value;
        const expiryDate = document.getElementById('expiryDate').value;
        const cvv = document.getElementById('cvv').value;
        const cardName = document.getElementById('cardName').value;
        
        if (!cardNumber || !expiryDate || !cvv || !cardName) {
            showNotification('Please fill in all card details!', 'error');
            return;
        }
    }

    const orderPayload = {
        cart,
        billing: {
            firstName: document.getElementById('firstName').value.trim(),
            lastName: document.getElementById('lastName').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            address: document.getElementById('address').value.trim(),
            city: document.getElementById('city').value.trim(),
            zipCode: document.getElementById('zipCode').value.trim()
        },
        paymentMethod
    };

    showNotification('Submitting your order to the backend...');

    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderPayload)
        });

        const data = await response.json();
        if (!response.ok) {
            showNotification(data.error || 'Could not submit order.', 'error');
            return;
        }

        localStorage.setItem('cart', JSON.stringify([]));
        updateCartCount();

        if (paymentMethod === 'bank') {
            const orderId = data.order.id;
            window.location.href = `bank-transfer.html?orderId=${encodeURIComponent(orderId)}`;
            return;
        }

        showNotification('Order placed successfully! Thank you for shopping with us.');
        window.location.href = 'index.html';
    } catch (error) {
        console.error(error);
        showNotification('Unable to place your order right now.', 'error');
    }
}

// ================== Product Display ==================
function displayProducts(filter = currentFilter) {
    const productsGrid = document.getElementById('productsGrid');
    const viewMoreBtn = document.getElementById('viewMoreBtn');
    currentFilter = filter;
    
    const filteredProducts = filter === 'all' 
        ? products 
        : products.filter(p => p.category === filter);
    
    const maxItems = currentPage * productsPerPage;
    const visibleProducts = filteredProducts.slice(0, maxItems);
    const hasMore = filteredProducts.length > visibleProducts.length;

    productsGrid.innerHTML = visibleProducts.map(product => `
        <div class="product-card" onclick="openProductModal(${product.id})">
            <div class="product-image">
                <img src="${product.image}" alt="${product.name}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div class="product-body">
                <div class="product-category">${product.category.toUpperCase()}</div>
                <h3 class="product-name">${product.name}</h3>
                <div class="product-rating">
                    <span class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</span>
                    <span style="color: #999; font-size: 0.9rem;">(${product.reviews})</span>
                </div>
                <div class="product-price">
                    <div>
                        <span class="price">$${product.price.toFixed(2)}</span>
                        ${product.originalPrice > product.price ? `
                            <div>
                                <span class="original-price">$${product.originalPrice.toFixed(2)}</span>
                                <span class="discount">-${Math.round((1 - product.price/product.originalPrice) * 100)}%</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <button class="btn btn-primary" onclick="event.stopPropagation(); addToCart(${JSON.stringify(product).replace(/"/g, '&quot;')})">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');

    if (viewMoreBtn) {
        viewMoreBtn.style.display = hasMore ? 'inline-block' : 'none';
        viewMoreBtn.textContent = hasMore ? 'View More' : 'No More Items';
    }
}

function loadMoreProducts() {
    currentPage += 1;
    displayProducts(currentFilter);
}

// ================== Product Modal ==================
let currentProductId = null;

function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    currentProductId = productId;
    
    const modal = document.getElementById('productModal');
    
    // Update product image
    const modalProductImage = document.getElementById('modalProductImage');
    modalProductImage.innerHTML = `<img src="${product.image}" alt="${product.name}" style="width: 100%; height: 100%; object-fit: cover;">`;
    
    document.getElementById('modalProductName').textContent = product.name;
    document.getElementById('modalProductPrice').textContent = `$${product.price.toFixed(2)}`;
    document.getElementById('modalProductDescription').textContent = product.description;
    document.getElementById('modalProductRating').innerHTML = '★'.repeat(Math.floor(product.rating)) + '☆'.repeat(5 - Math.floor(product.rating));
    document.getElementById('modalProductReviews').textContent = `${product.reviews} reviews`;
    
    const specsHtml = Object.entries(product.specs).map(([key, value]) => `
        <div class="spec-item">
            <span>${key}:</span>
            <span style="font-weight: bold;">${value}</span>
        </div>
    `).join('');
    document.getElementById('modalProductSpecs').innerHTML = specsHtml;
    
    document.getElementById('quantityInput').value = 1;
    
    modal.style.display = 'block';
}

// ================== Modal Controls ==================
function setupModalControls() {
    const productModal = document.getElementById('productModal');
    const cartModal = document.getElementById('cartModal');
    const cartBtn = document.getElementById('cartBtn');
    
    cartBtn.onclick = function(e) {
        e.preventDefault();
        displayCart();
        cartModal.style.display = 'block';
    }
    
    // Quantity controls
    document.getElementById('decreaseQty').onclick = function() {
        const input = document.getElementById('quantityInput');
        if (input.value > 1) {
            input.value = parseInt(input.value) - 1;
        }
    }
    
    document.getElementById('increaseQty').onclick = function() {
        const input = document.getElementById('quantityInput');
        input.value = parseInt(input.value) + 1;
    }
    
    // Add to cart from modal
    document.getElementById('addToCartBtn').onclick = function() {
        const quantity = parseInt(document.getElementById('quantityInput').value);
        const product = products.find(p => p.id === currentProductId);
        addToCart(product, quantity);
        productModal.style.display = 'none';
    }
    
    // Checkout button in cart modal
    const checkoutBtn = document.getElementById('checkoutButton');
    if (checkoutBtn) {
        checkoutBtn.onclick = function(e) {
            e.stopPropagation();
            showCheckout();
        };
    }
}

// ================== Checkout Controls ==================
function setupCheckoutControls() {
    const paymentMethod = document.getElementById('paymentMethod');
    const placeOrderBtn = document.getElementById('placeOrderBtn');
    const backToCartBtn = document.getElementById('backToCartBtn');

    if (paymentMethod) {
        paymentMethod.onchange = toggleCardDetails;
    }

    if (placeOrderBtn) {
        placeOrderBtn.onclick = placeOrder;
    }

    if (backToCartBtn) {
        backToCartBtn.onclick = backToCart;
    }
}

// ================== WhatsApp Chat ==================
function setupWhatsappChat() {
    const whatsappBtn = document.getElementById('whatsappBtn');
    const chatWidget = document.getElementById('chatWidget');
    const chatClose = document.querySelector('.chat-close');
    const whatsappForm = document.getElementById('whatsappChatForm');
    const whatsappName = document.getElementById('whatsappName');
    const whatsappMessage = document.getElementById('whatsappMessage');

    if (!whatsappBtn || !chatWidget || !whatsappForm || !whatsappName || !whatsappMessage) {
        console.warn('WhatsApp chat elements not found:', {whatsappBtn, chatWidget, whatsappForm, whatsappName, whatsappMessage});
        return;
    }

    let currentThreadId = null;
    let pollInterval = null;

    whatsappBtn.addEventListener('click', function(e) {
        const href = whatsappBtn.getAttribute('href');
        if (href && href !== '#') {
            return;
        }
        e.preventDefault();
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
        if (currentUser) {
            whatsappName.value = currentUser.fullName;
            currentThreadId = currentUser.email;
        } else {
            whatsappName.value = localStorage.getItem('whatsappName') || 'Guest';
            currentThreadId = localStorage.getItem('whatsappName') || 'Guest';
        }
        chatWidget.classList.add('open');
        renderWhatsappMessages();
        startMessagePolling();
        updateChatIndicator();
    });

    if (chatClose) {
        chatClose.addEventListener('click', function() {
            chatWidget.classList.remove('open');
            stopMessagePolling();
        });
    }

    whatsappForm.onsubmit = async function(e) {
        e.preventDefault();
        const name = whatsappName.value.trim() || 'Guest';
        const message = whatsappMessage.value.trim();

        if (!message) {
            showNotification('Please type a message before sending.', 'error');
            return;
        }

        const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
        const payload = {
            customerName: name,
            customerEmail: currentUser ? currentUser.email : '',
            customerPhone: currentUser ? (currentUser.phoneNumber || '') : '',
            whatsappNumber: '9138154963',
            message: message
        };

        try {
            const response = await fetch('/api/customer-care', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const error = await response.json();
                showNotification(error.error || 'Failed to send message', 'error');
                return;
            }

            whatsappMessage.value = '';
            renderWhatsappMessages();
            showNotification('Message sent!');
        } catch (error) {
            console.error('Error sending message:', error);
            showNotification('Failed to send message', 'error');
        }
    };

    function startMessagePolling() {
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(() => {
            renderWhatsappMessages();
        }, 3000);
    }

    function stopMessagePolling() {
        if (pollInterval) clearInterval(pollInterval);
    }
}

function simulateAgentReply(name) {
    const chats = JSON.parse(localStorage.getItem('whatsappChats') || '[]');
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    const email = currentUser ? currentUser.email : '';
    const phone = currentUser ? (currentUser.phoneNumber || currentUser.phone || '') : '';
    const chat = chats.find(c => (email && c.customerEmail === email) || (phone && c.customerPhone === phone) || (c.customerName === name));
    if (!chat) return;

    chat.messages = chat.messages || [];
    chat.messages.push({
        sender: 'agent',
        text: 'Thanks for your message! A support agent will reply here soon.',
        timestamp: new Date().toISOString()
    });

    localStorage.setItem('whatsappChats', JSON.stringify(chats));
    renderWhatsappMessages();
}

async function saveWhatsappChat(name, message) {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    const customerEmail = currentUser ? currentUser.email : '';
    const customerPhone = currentUser ? (currentUser.phoneNumber || currentUser.phone || '') : '';
    const payload = {
        customerName: name,
        customerEmail,
        customerPhone,
        whatsappNumber: '9138154963',
        message
    };

    console.log('saveWhatsappChat payload:', payload);

    try {
        const response = await fetch('/api/customer-care', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        console.log('saveWhatsappChat response status:', response.status);

        const data = await response.json();
        console.log('saveWhatsappChat response data:', data);

        if (!response.ok) {
            console.error('AI message send failed:', data.error);
            showNotification(data.error || 'Unable to send AI message.', 'error');
            return false;
        }

        const chats = JSON.parse(localStorage.getItem('whatsappChats') || '[]');
        let chat = chats.find(c => c.customerEmail && customerEmail && c.customerEmail === customerEmail);

        if (!chat) {
            chat = chats.find(c => c.customerName === name);
        }

        if (!chat) {
            chat = {
                customerName: name,
                customerEmail: customerEmail,
                customerPhone: customerPhone,
                whatsappNumber: '9138154963',
                messages: []
            };
            chats.push(chat);
        }

        chat.messages = chat.messages || [];
        chat.messages.push({
            sender: 'customer',
            text: message,
            timestamp: data.createdAt || new Date().toISOString()
        });

        localStorage.setItem('whatsappChats', JSON.stringify(chats));
        console.log('AI message saved successfully');
        updateChatIndicator();
        return true;
    } catch (error) {
        console.error('WhatsApp chat save error:', error);
        showNotification('Unable to send WhatsApp message.', 'error');
        return false;
    }
}

async function renderWhatsappMessages() {
    const messagesContainer = document.getElementById('whatsappChatMessages');
    if (!messagesContainer) return;

    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    const email = currentUser ? currentUser.email : localStorage.getItem('whatsappName') || 'Guest';

    try {
        const response = await fetch('/api/customer-care');
        if (!response.ok) {
            console.error('Failed to fetch messages');
            return;
        }

        const data = await response.json();
        const threads = data.threads || [];
        const thread = threads.find(t => t.customerEmail === email);

        if (!thread || !thread.messages || thread.messages.length === 0) {
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
            messagesContainer.innerHTML = `
                <div class="message agent-message">
                    <div class="message-bubble">
                        <p>Hi there! Type a message below to start chatting.</p>
                        <span class="message-time">${time}</span>
                    </div>
                </div>
            `;
            return;
        }

        messagesContainer.innerHTML = thread.messages.map(msg => `
            <div class="message ${msg.sender === 'customer' ? 'user-message' : 'agent-message'}">
                <div class="message-bubble">
                    <p>${msg.text}</p>
                </div>
                <span class="message-time">${new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</span>
            </div>
        `).join('');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Error rendering messages:', error);
    }
}

// ================== Filter Controls ==================
function setupFilterControls() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.onclick = function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filter = this.getAttribute('data-filter');
            currentPage = 1;
            fetchProducts(filter);
        }
    });
}

// ================== Mobile Menu ==================
function setupMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.querySelector('.nav-menu');
    
    menuToggle.onclick = function() {
        navMenu.classList.toggle('active');
    }
    
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.onclick = function() {
            navMenu.classList.remove('active');
        }
    });
}

// ================== Contact Form ==================
function setupContactForm() {
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;

    contactForm.onsubmit = async function(e) {
        e.preventDefault();

        const name = document.getElementById('contactName').value.trim();
        const email = document.getElementById('contactEmail').value.trim();
        const message = document.getElementById('contactMessage').value.trim();

        if (!name || !email || !message) {
            showNotification('Please enter your name, email, and message.', 'error');
            return;
        }

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, message })
            });

            const data = await response.json();
            if (!response.ok) {
                showNotification(data.error || 'Unable to send message.', 'error');
                return;
            }

            showNotification('Message sent successfully! A confirmation email was also sent to you.');
            contactForm.reset();
        } catch (error) {
            console.error(error);
            showNotification('Unable to send message. Please try again later.', 'error');
        }
    }
}

// ================== Authentication ==================
function setupAuthModals() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    // Open login modal
    loginBtn.onclick = function(e) {
        e.preventDefault();
        loginModal.style.display = 'block';
    }
    
    // Open register modal
    registerBtn.onclick = function(e) {
        e.preventDefault();
        registerModal.style.display = 'block';
    }
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        if (event.target === loginModal) {
            loginModal.style.display = 'none';
        }
        if (event.target === registerModal) {
            registerModal.style.display = 'none';
        }
        if (event.target === productModal) {
            productModal.style.display = 'none';
        }
        if (event.target === cartModal) {
            cartModal.style.display = 'none';
        }
    }
    
    // Close buttons
    const closeButtons = document.querySelectorAll('.modal .close');
    closeButtons.forEach(btn => {
        btn.onclick = function() {
            this.closest('.modal').style.display = 'none';
        }
    });
    
    // Login form submission
    loginForm.onsubmit = async function(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        if (await loginUser(email, password)) {
            showNotification('Login successful!');
            loginModal.style.display = 'none';
            loginForm.reset();
            updateAuthUI();
        }
    }
    
    // Register form submission
    registerForm.onsubmit = async function(e) {
        e.preventDefault();
        const userData = {
            fullName: document.getElementById('fullName').value,
            email: document.getElementById('registerEmail').value,
            phoneNumber: document.getElementById('phoneNumber').value,
            address: document.getElementById('address').value,
            city: document.getElementById('city').value,
            zipCode: document.getElementById('zipCode').value,
            password: document.getElementById('registerPassword').value,
            confirmPassword: document.getElementById('confirmPassword').value
        };
        
        const registeredUser = await registerUser(userData);
        if (registeredUser) {
            showNotification('Registration successful! You are now logged in.');
            registerModal.style.display = 'none';
            registerForm.reset();
            localStorage.setItem('currentUser', JSON.stringify(registeredUser));
            updateAuthUI();
        }
    }
}

function switchToRegister() {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('registerModal').style.display = 'block';
}

function switchToLogin() {
    document.getElementById('registerModal').style.display = 'none';
    document.getElementById('loginModal').style.display = 'block';
}

async function registerUser(userData) {
    if (userData.password !== userData.confirmPassword) {
        showNotification('Passwords do not match!', 'error');
        return false;
    }

    if (userData.password.length < 6) {
        showNotification('Password must be at least 6 characters!', 'error');
        return false;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        if (!response.ok) {
            showNotification(data.error || 'Registration failed.', 'error');
            return false;
        }

        return data.user;
    } catch (error) {
        console.error(error);
        showNotification('Unable to register at this time.', 'error');
        return false;
    }
}

async function loginUser(email, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok) {
            showNotification(data.error || 'Login failed.', 'error');
            return false;
        }

        localStorage.setItem('currentUser', JSON.stringify(data.user));
        return true;
    } catch (error) {
        console.error(error);
        showNotification('Unable to log in at this time.', 'error');
        return false;
    }
}

function logoutUser() {
    localStorage.removeItem('currentUser');
    updateAuthUI();
    showNotification('Logged out successfully!');
}

function updateAuthUI() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    
    if (currentUser) {
        const firstName = currentUser.fullName.split(' ')[0];
        loginBtn.innerHTML = `<i class="fas fa-user"></i><span>${firstName}</span>`;
        loginBtn.title = 'Click to show logout option';
        loginBtn.dataset.showingLogout = 'false';
        loginBtn.onclick = function(e) {
            e.preventDefault();
            if (loginBtn.dataset.showingLogout === 'true') {
                logoutUser();
            } else {
                loginBtn.dataset.showingLogout = 'true';
                loginBtn.innerHTML = `<i class="fas fa-sign-out-alt"></i><span>Logout</span>`;
                loginBtn.title = 'Click again to logout';
            }
        };
        registerBtn.style.display = 'none';
    } else {
        loginBtn.innerHTML = `<i class="fas fa-sign-in-alt"></i><span>Login</span>`;
        loginBtn.onclick = function(e) {
            e.preventDefault();
            document.getElementById('loginModal').style.display = 'block';
        };
        registerBtn.style.display = 'inline-block';
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background-color: ${type === 'error' ? '#f44336' : '#4caf50'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        z-index: 3000;
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ================== Initialization ==================
document.addEventListener('DOMContentLoaded', async function() {
    initCarousel();
    await fetchProducts();
    setupFilterControls();
    const viewMoreBtn = document.getElementById('viewMoreBtn');
    if (viewMoreBtn) {
        viewMoreBtn.onclick = loadMoreProducts;
    }
    setupModalControls();
    setupCheckoutControls();
    setupWhatsappChat();
    updateChatIndicator();
    setupMobileMenu();
    setupContactForm();
    setupAuthModals();
    updateCartCount();
    updateAuthUI();
    
    // Add slide animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
    `;
    document.head.appendChild(style);
});