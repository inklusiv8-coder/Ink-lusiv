const cart = JSON.parse(localStorage.getItem('cart') || '[]');

function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem('currentUser') || 'null');
    } catch (error) {
        return null;
    }
}

function populateCheckoutFromCurrentUser() {
    const currentUser = getCurrentUser();
    if (!currentUser) return;

    const fullName = (currentUser.fullName || '').trim();
    const nameParts = fullName.split(' ').filter(Boolean);
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';

    const firstNameField = document.getElementById('firstName');
    const lastNameField = document.getElementById('lastName');
    const emailField = document.getElementById('email');
    const phoneField = document.getElementById('phone');
    const addressField = document.getElementById('address');
    const cityField = document.getElementById('city');
    const zipCodeField = document.getElementById('zipCode');

    if (firstNameField) firstNameField.value = firstName;
    if (lastNameField) lastNameField.value = lastName;
    if (emailField) emailField.value = currentUser.email || '';
    if (phoneField) phoneField.value = currentUser.phoneNumber || currentUser.phone || '';
    if (addressField) addressField.value = currentUser.address || '';
    if (cityField) cityField.value = currentUser.city || '';
    if (zipCodeField) zipCodeField.value = currentUser.zipCode || '';
}

function initCheckoutPage() {
    displayCheckoutItems();
    updateCheckoutTotals();
    setupPaymentToggle();
    setupButtons();
    setupFormValidation();
    populateCheckoutFromCurrentUser();
    updateBillingInfoDisplay();

    // Mobile-specific enhancements
    if (window.innerWidth <= 768) {
        setupMobileEnhancements();
    }
}

function setupFormValidation() {
    const form = document.getElementById('checkoutForm');
    const inputs = form.querySelectorAll('input, select');

    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });

        input.addEventListener('input', function() {
            // Clear validation state on input
            this.classList.remove('invalid', 'valid');
        });
    });

    // Format card number input
    const cardNumberField = document.getElementById('cardNumber');
    if (cardNumberField) {
        cardNumberField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.replace(/(.{4})/g, '$1 ').trim();
            e.target.value = formattedValue;
        });
    }

    // Format expiry date input
    const expiryField = document.getElementById('expiryDate');
    if (expiryField) {
        expiryField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;

    // Remove previous validation classes
    field.classList.remove('invalid', 'valid');

    // Basic validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
    }

    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = emailRegex.test(value);
    }

    // Phone validation (basic)
    if (field.id === 'phone' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        isValid = phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''));
    }

    // Add validation class
    field.classList.add(isValid ? 'valid' : 'invalid');

    return isValid;
}

function setupMobileEnhancements() {
    // Prevent zoom on input focus for iOS
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.setAttribute('inputmode', this.type === 'email' ? 'email' : 'text');
        });
    });

    // Add viewport meta tag if not present
    if (!document.querySelector('meta[name="viewport"]')) {
        const viewport = document.createElement('meta');
        viewport.name = 'viewport';
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        document.head.appendChild(viewport);
    }

    // Improve button touch targets
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.style.minHeight = '48px';
        btn.style.display = 'flex';
        btn.style.alignItems = 'center';
        btn.style.justifyContent = 'center';
    });
}

function displayCheckoutItems() {
    const checkoutItemsContainer = document.getElementById('checkoutItems');

    if (cart.length === 0) {
        checkoutItemsContainer.innerHTML = '<p class="empty-checkout">Your cart is empty. <a href="index.html#products">Browse our products</a> to add items.</p>';
        return;
    }

    checkoutItemsContainer.innerHTML = cart.map(item => `
        <div class="checkout-item">
            <div class="checkout-item-details">
                <div class="checkout-item-name">${item.name} x ${item.quantity}</div>
                <div class="checkout-item-price">$${(item.price || 0).toFixed(2)} each</div>
            </div>
            <div class="checkout-item-total">$${((item.price || 0) * item.quantity).toFixed(2)}</div>
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

    const subtotal = cart.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0);
    const shipping = cart.length > 0 ? 1000 : 0;
    const tax = subtotal * 0.08;
    const total = subtotal + shipping + tax;

    document.getElementById('checkoutSubtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('checkoutShipping').textContent = `$${shipping.toFixed(2)}`;
    document.getElementById('checkoutTax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('checkoutTotal').textContent = `$${total.toFixed(2)}`;
    placeOrderBtn.disabled = false;
    placeOrderBtn.textContent = 'Place Order';
    placeOrderBtn.style.opacity = '1';
}

function setupPaymentToggle() {
    const paymentMethod = document.getElementById('paymentMethod');
    const cardDetails = document.getElementById('cardDetails');

    if (!paymentMethod || !cardDetails) return;

    paymentMethod.onchange = function() {
        const isCard = paymentMethod.value === 'card';
        cardDetails.style.display = isCard ? 'block' : 'none';

        // Auto-focus first card field on mobile when card is selected
        if (isCard && window.innerWidth <= 768) {
            setTimeout(() => {
                const cardNumberField = document.getElementById('cardNumber');
                if (cardNumberField) cardNumberField.focus();
            }, 300);
        }
    };
}

function setupButtons() {
    const placeOrderBtn = document.getElementById('placeOrderBtn');
    const backToCartBtn = document.getElementById('backToCartBtn');

    if (placeOrderBtn) {
        placeOrderBtn.onclick = placeOrder;
    }

    if (backToCartBtn) {
        backToCartBtn.onclick = function() {
            window.location.href = 'index.html';
        };
    }

    // Update billing info display when form fields change
    const billingFields = ['firstName', 'lastName', 'email', 'address'];
    billingFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', updateBillingInfoDisplay);
        }
    });
}

function updateBillingInfoDisplay() {
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const address = document.getElementById('address').value.trim();

    const fullName = `${firstName} ${lastName}`.trim();
    document.getElementById('billingName').textContent = fullName || '-';
    document.getElementById('billingEmail').textContent = email || '-';
    document.getElementById('billingAddress').textContent = address || '-';
}

async function placeOrder() {
    if (cart.length === 0) {
        showNotification('Your cart is empty! Add items before placing an order.', 'error');
        return;
    }

    const form = document.getElementById('checkoutForm');
    if (!form.checkValidity()) {
        showNotification('Please fill in all required fields!', 'error');
        // Highlight invalid fields
        const invalidFields = form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            invalidFields[0].focus();
        }
        return;
    }

    const paymentMethod = document.getElementById('paymentMethod').value;
    if (!paymentMethod) {
        showNotification('Please select a payment method!', 'error');
        document.getElementById('paymentMethod').focus();
        return;
    }

    if (paymentMethod === 'card') {
        const cardNumber = document.getElementById('cardNumber').value.trim();
        const expiryDate = document.getElementById('expiryDate').value.trim();
        const cvv = document.getElementById('cvv').value.trim();
        const cardName = document.getElementById('cardName').value.trim();
        if (!cardNumber || !expiryDate || !cvv || !cardName) {
            showNotification('Please fill in all card details!', 'error');
            return;
        }
    }

    // Show loading state
    const placeOrderBtn = document.getElementById('placeOrderBtn');
    const originalText = placeOrderBtn.textContent;
    placeOrderBtn.disabled = true;
    placeOrderBtn.classList.add('loading');
    placeOrderBtn.textContent = 'Processing...';

    const billing = {
        fullName: `${document.getElementById('firstName').value.trim()} ${document.getElementById('lastName').value.trim()}`.trim(),
        email: document.getElementById('email').value.trim(),
        phoneNumber: document.getElementById('phone').value.trim(),
        address: document.getElementById('address').value.trim(),
        city: document.getElementById('city').value.trim(),
        zipCode: document.getElementById('zipCode').value.trim()
    };

    const orderPayload = {
        cart,
        billing,
        paymentMethod
    };

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
            throw new Error(data.error || 'Could not submit order.');
        }

        localStorage.setItem('cart', JSON.stringify([]));
        const orderId = data.order.id;

        if (paymentMethod === 'bank') {
            // For bank transfer, create a bank transfer record instead
            const bankPayload = {
                cart,
                billing
            };

            try {
                const bankResponse = await fetch('/api/bank-transfers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(bankPayload)
                });

                const bankData = await bankResponse.json();
                if (!bankResponse.ok) {
                    throw new Error(bankData.error || 'Could not submit bank transfer.');
                }

                showNotification('Bank transfer order submitted. Awaiting admin confirmation. You will be notified once confirmed.');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
                return;
            } catch (error) {
                console.error(error);
                throw new Error('Unable to submit bank transfer.');
            }
        }

        showNotification('Order placed successfully! Thank you for shopping with us.');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1200);
    } catch (error) {
        console.error(error);
        showNotification(error.message || 'Unable to place your order right now.', 'error');
    } finally {
        // Reset button state
        placeOrderBtn.disabled = false;
        placeOrderBtn.classList.remove('loading');
        placeOrderBtn.textContent = originalText;
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    const isMobile = window.innerWidth <= 768;

    notification.style.cssText = `
        position: fixed;
        ${isMobile ? 'bottom: 20px; left: 20px; right: 20px;' : 'top: 20px; right: 20px;'}
        background-color: ${type === 'error' ? '#f44336' : '#4caf50'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        font-size: ${isMobile ? '14px' : '16px'};
        max-width: ${isMobile ? 'calc(100vw - 40px)' : '400px'};
        word-wrap: break-word;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    // Add fade out animation
    setTimeout(() => {
        notification.style.transition = 'opacity 0.5s ease-out';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 2500);
}

document.addEventListener('DOMContentLoaded', initCheckoutPage);