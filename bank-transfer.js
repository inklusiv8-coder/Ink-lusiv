let bankOrder = null;

async function initBankTransferPage() {
    const backBtn = document.getElementById('bankBackBtn');
    const orderId = new URLSearchParams(window.location.search).get('orderId');

    if (orderId) {
        try {
            const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}`);
            const data = await response.json();
            if (response.ok && data.order) {
                bankOrder = data.order;
            }
        } catch (error) {
            console.error(error);
        }
    }

    if (!bankOrder) {
        const savedOrder = JSON.parse(localStorage.getItem('bankOrder') || 'null');
        if (savedOrder && Array.isArray(savedOrder.cart) && savedOrder.cart.length > 0) {
            bankOrder = savedOrder;
        }
    }

    if (!bankOrder || !Array.isArray(bankOrder.cart) || bankOrder.cart.length === 0) {
        document.getElementById('bankOrderItems').innerHTML = '<p class="empty-checkout">No pending bank transfer order found. Please place an order first.</p>';
        document.getElementById('paymentStatus').textContent = 'No Order';
        document.getElementById('paymentInstruction').textContent = 'Go back to the shop and choose bank transfer at checkout.';
        return;
    }

    displayBankOrder();
    updateBankTotals();
    updateBankStatus();
    updateBillingInfoDisplay();

    backBtn.onclick = function() {
        window.location.href = 'index.html';
    };
}

function displayBankOrder() {
    const container = document.getElementById('bankOrderItems');
    container.innerHTML = bankOrder.cart.map(item => `
        <div class="checkout-item">
            <div class="checkout-item-details">
                <div class="checkout-item-name">${item.name} x ${item.quantity}</div>
                <div class="checkout-item-price">$${item.price.toFixed(2)} each</div>
            </div>
            <div class="checkout-item-total">$${(item.price * item.quantity).toFixed(2)}</div>
        </div>
    `).join('');
}

function updateBankTotals() {
    const subtotal = bankOrder.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const shipping = typeof bankOrder.shipping === 'number' ? bankOrder.shipping : 1000;
    const tax = subtotal * 0.08;
    const total = subtotal + shipping + tax;

    document.getElementById('bankSubtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('bankShipping').textContent = `$${shipping.toFixed(2)}`;
    document.getElementById('bankTax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('bankTotal').textContent = `$${total.toFixed(2)}`;
}

function updateBillingInfoDisplay() {
    const billing = bankOrder.billing || {};
    const firstName = billing.firstName || '';
    const lastName = billing.lastName || '';
    const fullName = `${firstName} ${lastName}`.trim();

    document.getElementById('bankBillingName').textContent = fullName || '-';
    document.getElementById('bankBillingEmail').textContent = billing.email || '-';
    document.getElementById('bankBillingAddress').textContent = billing.address || '-';
}

function updateBankStatus() {
    const statusLabel = document.getElementById('paymentStatus');
    const instruction = document.getElementById('paymentInstruction');

    if (bankOrder.status === 'confirmed') {
        statusLabel.textContent = 'Confirmed';
        instruction.textContent = 'Your payment has been accepted. Thank you!';
    } else {
        statusLabel.textContent = 'Pending';
        instruction.textContent = 'Waiting for your payment within 30min';
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.style.cssText = `position: fixed; top: 20px; right: 20px; background-color: ${type === 'error' ? '#f44336' : '#4caf50'}; color: white; padding: 15px 20px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 9999;`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

document.addEventListener('DOMContentLoaded', initBankTransferPage);