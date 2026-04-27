let cart = [];

const itemNameInput = document.getElementById('itemName');
const itemPriceInput = document.getElementById('itemPrice');
const itemQtyInput = document.getElementById('itemQty');
const cartItemsContainer = document.getElementById('cartItems');
const cartTotalElement = document.getElementById('cartTotal');

// Quantity Controls
document.getElementById('btnMinus').addEventListener('click', () => {
    let current = parseInt(itemQtyInput.value) || 1;
    if (current > 1) itemQtyInput.value = current - 1;
});

document.getElementById('btnPlus').addEventListener('click', () => {
    let current = parseInt(itemQtyInput.value) || 0;
    itemQtyInput.value = current + 1;
});

// Add to Cart
document.getElementById('btnAdd').addEventListener('click', () => {
    const name = itemNameInput.value.trim();
    const price = parseFloat(itemPriceInput.value);
    const quantity = parseInt(itemQtyInput.value);

    if (!name || isNaN(price) || isNaN(quantity) || price < 0 || quantity < 1) {
        alert("Please enter valid item details.");
        return;
    }

    cart.push({ name, price, quantity });
    updateCartUI();
    
    // Reset inputs
    itemNameInput.value = '';
    itemPriceInput.value = '';
    itemQtyInput.value = '1';
    itemNameInput.focus();
});

// Remove Item
function removeItem(index) {
    cart.splice(index, 1);
    updateCartUI();
}

// Update UI
function updateCartUI() {
    cartItemsContainer.innerHTML = '';
    let total = 0;

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const itemDiv = document.createElement('div');
        itemDiv.className = 'cart-item';
        itemDiv.innerHTML = `
            <div class="item-info">
                <span class="item-name">${item.name}</span>
                <span class="item-sub">${item.quantity} x $${item.price.toFixed(2)}</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span class="item-total">$${itemTotal.toFixed(2)}</span>
                <button class="remove-btn" onclick="removeItem(${index})">✖</button>
            </div>
        `;
        cartItemsContainer.appendChild(itemDiv);
    });

    cartTotalElement.textContent = `$${total.toFixed(2)}`;
    
    // Scroll to bottom
    cartItemsContainer.scrollTop = cartItemsContainer.scrollHeight;
}

// Clear Cart
document.getElementById('btnClear').addEventListener('click', () => {
    if(confirm("Clear the entire cart?")) {
        cart = [];
        updateCartUI();
    }
});

// Checkout
document.getElementById('btnCheckout').addEventListener('click', async () => {
    if (cart.length === 0) {
        alert("Cart is empty!");
        return;
    }

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    const payload = {
        items: cart,
        total: total
    };

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            alert(`Success! Receipts printed (Check Docker Console). Sale ID: #${data.sale_id}`);
            cart = [];
            updateCartUI();
        } else {
            alert("Error during checkout.");
        }
    } catch (error) {
        console.error("Checkout error:", error);
        alert("Network error. Please try again.");
    }
});
