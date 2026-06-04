# Wholesale ERP/CRM/WMS FastAPI Backend

Production-ready FastAPI backend for inventory, customer, order, dashboard, and health-check workflows.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Default Auth

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Override with environment variables:

```bash
ERP_ADMIN_USERNAME=admin
ERP_ADMIN_PASSWORD=change-me
ERP_AUTH_TOKEN=change-me-token
DATABASE_URL=sqlite:///./erp_crm_wms.db
```

## Key Endpoints

- `POST /auth/login`
- `GET /health`
- `GET /dashboard/stats`
- `POST /products`
- `GET /products`
- `GET /products/{product_id}`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`
- `POST /customers`
- `GET /customers`
- `GET /customers/{customer_id}`
- `DELETE /customers/{customer_id}`
- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`

## Frontend

The vanilla JavaScript admin panel is in `frontend/` and is served by the same FastAPI app.

Run one server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/` to start at the landing page, or `http://localhost:8000/login.html` to go directly to sign in.
