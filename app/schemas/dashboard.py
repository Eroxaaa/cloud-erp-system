from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    total_stock: int


class DashboardStatsResponse(BaseModel):
    data: DashboardStats
