const API_BASE_URL = window.location.origin;

function getToken() {
  return localStorage.getItem("erpToken");
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function showAlert(message, type = "success") {
  const alertBox = document.getElementById("alertBox");
  if (!alertBox) {
    return;
  }

  alertBox.textContent = message;
  alertBox.className = `alert show ${type}`;

  window.clearTimeout(showAlert.timeoutId);
  showAlert.timeoutId = window.setTimeout(() => {
    alertBox.className = "alert";
    alertBox.textContent = "";
  }, 3500);
}

function setLoading(isLoading) {
  const spinner = document.getElementById("loadingSpinner");
  if (spinner) {
    spinner.classList.toggle("show", isLoading);
  }
}

function protectPage() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

function logoutUser() {
  localStorage.removeItem("erpToken");
  window.location.href = "login.html";
}

function toggleSidebar() {
  document.body.classList.toggle("sidebar-open");
}

async function parseResponse(response) {
  const rawBody = await response.text();
  let data = null;

  if (rawBody) {
    try {
      data = JSON.parse(rawBody);
    } catch (error) {
      data = rawBody;
    }
  }

  if (!response.ok) {
    const message = data && typeof data === "object" && data.detail
      ? formatApiError(data.detail)
      : typeof data === "string" && data
      ? data
      : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data ?? {};
}

function formatApiError(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg || JSON.stringify(item))
      .join(", ");
  }

  if (typeof detail === "string") {
    return detail;
  }

  return "Something went wrong";
}

async function apiRequest(path, options = {}) {
  const headers = {
    ...authHeaders(),
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  return parseResponse(response);
}

function readForm(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function getResponseData(payload, fallback = null) {
  if (payload && Object.prototype.hasOwnProperty.call(payload, "data")) {
    return payload.data;
  }

  return payload ?? fallback;
}

function getResponseMessage(payload, fallback) {
  return payload && payload.message ? payload.message : fallback;
}

function money(value) {
  return Number(value).toFixed(2);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function emptyRow(colspan, text) {
  return `<tr><td class="empty-state" colspan="${colspan}">${text}</td></tr>`;
}

async function loginUser(event) {
  event.preventDefault();
  const form = event.target;
  const credentials = readForm(form);
  const loginButton = document.getElementById("loginButton");

  if (loginButton) {
    loginButton.disabled = true;
    loginButton.classList.add("is-loading");
  }

  try {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });

    const tokenData = getResponseData(data, data);
    const token = typeof tokenData === "string"
      ? tokenData
      : tokenData.access_token;
    if (!token) {
      throw new Error("Login response did not include a token");
    }

    localStorage.setItem("erpToken", token);
    if (credentials.rememberMe) {
      localStorage.setItem("erpRememberedUsername", credentials.username);
    } else {
      localStorage.removeItem("erpRememberedUsername");
    }

    showAlert("Signed in successfully. Preparing your workspace...");
    document.body.classList.add("auth-success");
    window.setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 850);
  } catch (error) {
    showAlert(error.message, "error");
    if (loginButton) {
      loginButton.disabled = false;
      loginButton.classList.remove("is-loading");
    }
  }
}

async function loadDashboardStats() {
  setLoading(true);

  try {
    const response = await apiRequest("/dashboard/stats");
    const stats = getResponseData(response, {});
    document.getElementById("totalProducts").textContent = stats.total_products;
    document.getElementById("totalCustomers").textContent = stats.total_customers;
    document.getElementById("totalOrders").textContent = stats.total_orders;
    document.getElementById("totalStock").textContent = stats.total_stock;
  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function loadProducts() {
  const tableBody = document.getElementById("productsTableBody");
  if (!tableBody) {
    return;
  }

  setLoading(true);

  try {
    const response = await apiRequest("/products");
    const products = getResponseData(response, []);
    tableBody.innerHTML = products.length
      ? products.map((product) => `
          <tr>
            <td>${product.id}</td>
            <td>${escapeHtml(product.name)}</td>
            <td>${escapeHtml(product.category)}</td>
            <td>$${money(product.price)}</td>
            <td>${product.stock_quantity}</td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-light" type="button" onclick="editProduct(${product.id})">
                  Edit
                </button>
                <button class="btn btn-danger" type="button" onclick="deleteProduct(${product.id})">
                  Delete
                </button>
              </div>
            </td>
          </tr>
        `).join("")
      : emptyRow(6, "No products found");
  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function createProduct(event) {
  event.preventDefault();
  const form = event.target;
  const data = readForm(form);
  const productId = data.id ? Number(data.id) : null;

  const payload = {
    name: data.name.trim(),
    category: data.category.trim(),
    price: Number(data.price),
    stock_quantity: Number(data.stock_quantity),
  };

  if (!payload.name || !payload.category || payload.price <= 0 || payload.stock_quantity < 0) {
    showAlert("Please enter valid product details", "error");
    return;
  }

  if (productId) {
    await updateProduct(productId, payload, form);
    return;
  }

  try {
    const response = await apiRequest("/products", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    form.reset();
    showAlert(getResponseMessage(response, "Product added successfully"));
    await loadProducts();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

async function editProduct(productId) {
  try {
    const response = await apiRequest(`/products/${productId}`);
    const product = getResponseData(response);

    document.getElementById("productId").value = product.id;
    document.getElementById("productName").value = product.name;
    document.getElementById("productCategory").value = product.category;
    document.getElementById("productPrice").value = product.price;
    document.getElementById("productStock").value = product.stock_quantity;
    document.getElementById("productSubmitButton").textContent = "Update Product";
    document.getElementById("productCancelButton").hidden = false;
  } catch (error) {
    showAlert(error.message, "error");
  }
}

async function updateProduct(productId, payload, form) {
  try {
    const response = await apiRequest(`/products/${productId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    resetProductForm();
    showAlert(getResponseMessage(response, "Product updated successfully"));
    await loadProducts();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

function resetProductForm() {
  const form = document.getElementById("productForm");
  const submitButton = document.getElementById("productSubmitButton");
  const cancelButton = document.getElementById("productCancelButton");

  if (form) {
    form.reset();
  }

  if (submitButton) {
    submitButton.textContent = "Add Product";
  }

  if (cancelButton) {
    cancelButton.hidden = true;
  }
}

async function deleteProduct(productId) {
  if (!window.confirm("Delete this product?")) {
    return;
  }

  try {
    const response = await apiRequest(`/products/${productId}`, { method: "DELETE" });
    const productIdInput = document.getElementById("productId");
    if (productIdInput && productIdInput.value === String(productId)) {
      resetProductForm();
    }
    showAlert(getResponseMessage(response, "Product deleted successfully"));
    await loadProducts();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

async function loadCustomers() {
  const tableBody = document.getElementById("customersTableBody");
  if (!tableBody) {
    return;
  }

  setLoading(true);

  try {
    const response = await apiRequest("/customers");
    const customers = getResponseData(response, []);
    tableBody.innerHTML = customers.length
      ? customers.map((customer) => `
          <tr>
            <td>${customer.id}</td>
            <td>${escapeHtml(customer.name)}</td>
            <td>${escapeHtml(customer.email)}</td>
            <td>${escapeHtml(customer.phone)}</td>
            <td>
              <button class="btn btn-danger" type="button" onclick="deleteCustomer(${customer.id})">
                Delete
              </button>
            </td>
          </tr>
        `).join("")
      : emptyRow(5, "No customers found");
  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function createCustomer(event) {
  event.preventDefault();
  const form = event.target;
  const data = readForm(form);

  const payload = {
    name: data.name.trim(),
    email: data.email.trim(),
    phone: data.phone.trim(),
  };

  if (!payload.name || !payload.email || !payload.phone) {
    showAlert("Please enter valid customer details", "error");
    return;
  }

  try {
    const response = await apiRequest("/customers", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    form.reset();
    showAlert(getResponseMessage(response, "Customer added successfully"));
    await loadCustomers();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

async function deleteCustomer(customerId) {
  if (!window.confirm("Delete this customer?")) {
    return;
  }

  try {
    const response = await apiRequest(`/customers/${customerId}`, { method: "DELETE" });
    showAlert(getResponseMessage(response, "Customer deleted successfully"));
    await loadCustomers();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

async function loadOrders() {
  const tableBody = document.getElementById("ordersTableBody");
  if (!tableBody) {
    return;
  }

  setLoading(true);

  try {
    const response = await apiRequest("/orders");
    const orders = getResponseData(response, []);
    tableBody.innerHTML = orders.length
      ? orders.map((order) => `
          <tr>
            <td>${order.id}</td>
            <td>${order.customer_id}</td>
            <td>${order.product_id}</td>
            <td>${order.quantity}</td>
            <td>$${money(order.total_price)}</td>
            <td><span class="badge">${escapeHtml(order.status)}</span></td>
          </tr>
        `).join("")
      : emptyRow(6, "No orders found");
  } catch (error) {
    showAlert(error.message, "error");
  } finally {
    setLoading(false);
  }
}

async function createOrder(event) {
  event.preventDefault();
  const form = event.target;
  const data = readForm(form);

  const payload = {
    customer_id: Number(data.customer_id),
    product_id: Number(data.product_id),
    quantity: Number(data.quantity),
  };

  if (payload.customer_id <= 0 || payload.product_id <= 0 || payload.quantity <= 0) {
    showAlert("Please enter valid order details", "error");
    return;
  }

  try {
    const response = await apiRequest("/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    form.reset();
    showAlert(getResponseMessage(response, "Order created successfully"));
    await loadOrders();
  } catch (error) {
    showAlert(error.message, "error");
  }
}

window.loginUser = loginUser;
window.loadDashboardStats = loadDashboardStats;
window.loadProducts = loadProducts;
window.createProduct = createProduct;
window.deleteProduct = deleteProduct;
window.editProduct = editProduct;
window.updateProduct = updateProduct;
window.resetProductForm = resetProductForm;
window.loadCustomers = loadCustomers;
window.createCustomer = createCustomer;
window.deleteCustomer = deleteCustomer;
window.loadOrders = loadOrders;
window.createOrder = createOrder;
window.protectPage = protectPage;
window.logoutUser = logoutUser;
window.toggleSidebar = toggleSidebar;
