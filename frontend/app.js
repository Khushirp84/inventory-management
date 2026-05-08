const API = "http://127.0.0.1:8000";

// Show/hide sections
function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById(name).style.display = 'block';
    if (name === 'products') loadProducts();
    if (name === 'orders') loadOrders();
    if (name === 'lowstock') loadLowStock();
}

// Toast notification
function showToast(msg, error = false) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.background = error ? '#e74c3c' : '#27ae60';
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 3000);
}

// ✅ LOAD ALL PRODUCTS
async function loadProducts() {
    const res = await fetch(`${API}/products/`);
    const products = await res.json();
    const body = document.getElementById('products-body');
    body.innerHTML = '';
    products.forEach(p => {
        body.innerHTML += `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>${p.category || '-'}</td>
                <td class="${p.quantity <= 5 ? 'low-stock' : ''}">${p.quantity}</td>
                <td>₹${p.price}</td>
                <td>
                    <button class="btn-delete" onclick="deleteProduct(${p.id})">🗑 Delete</button>
                </td>
            </tr>`;
    });
}

// ✅ CREATE PRODUCT
async function createProduct() {
    const data = {
        name: document.getElementById('p-name').value,
        description: document.getElementById('p-desc').value,
        quantity: parseInt(document.getElementById('p-qty').value),
        price: parseFloat(document.getElementById('p-price').value),
        category: document.getElementById('p-cat').value
    };
    if (!data.name || !data.quantity || !data.price) {
        showToast('Please fill all required fields!', true);
        return;
    }
    const res = await fetch(`${API}/products/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (res.ok) {
        showToast('Product added successfully! ✅');
        loadProducts();
    } else {
        showToast('Error adding product!', true);
    }
}

// ✅ DELETE PRODUCT
async function deleteProduct(id) {
    if (!confirm('Delete this product?')) return;
    const res = await fetch(`${API}/products/${id}`, { method: 'DELETE' });
    if (res.ok) {
        showToast('Product deleted! ✅');
        loadProducts();
    }
}

// ✅ LOAD ALL ORDERS
async function loadOrders() {
    const res = await fetch(`${API}/orders/`);
    const orders = await res.json();
    const body = document.getElementById('orders-body');
    body.innerHTML = '';
    orders.forEach(o => {
        body.innerHTML += `
            <tr>
                <td>${o.id}</td>
                <td>${o.product_id}</td>
                <td>${o.quantity}</td>
                <td>${o.status}</td>
                <td>
                    <button onclick="updateStatus(${o.id}, 'completed')">✅</button>
                    <button onclick="updateStatus(${o.id}, 'cancelled')" class="btn-delete">❌</button>
                </td>
            </tr>`;
    });
}

// ✅ CREATE ORDER
async function createOrder() {
    const data = {
        product_id: parseInt(document.getElementById('o-pid').value),
        quantity: parseInt(document.getElementById('o-qty').value)
    };
    if (!data.product_id || !data.quantity) {
        showToast('Please fill all fields!', true);
        return;
    }
    const res = await fetch(`${API}/orders/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (res.ok) {
        showToast('Order placed successfully! ✅');
        loadOrders();
    } else {
        const err = await res.json();
        showToast(err.detail, true);
    }
}

// ✅ UPDATE ORDER STATUS
async function updateStatus(id, status) {
    const res = await fetch(`${API}/orders/${id}/status?status=${status}`, {
        method: 'PUT'
    });
    if (res.ok) {
        showToast(`Order ${status}! ✅`);
        loadOrders();
    }
}

// ✅ LOAD LOW STOCK
async function loadLowStock() {
    const res = await fetch(`${API}/products/alerts/low-stock`);
    const products = await res.json();
    const body = document.getElementById('lowstock-body');
    body.innerHTML = '';
    if (products.length === 0) {
        body.innerHTML = '<tr><td colspan="5">✅ All products have sufficient stock!</td></tr>';
        return;
    }
    products.forEach(p => {
        body.innerHTML += `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>${p.category || '-'}</td>
                <td class="low-stock">${p.quantity}</td>
                <td>₹${p.price}</td>
            </tr>`;
    });
}

// Load products on page start
loadProducts();