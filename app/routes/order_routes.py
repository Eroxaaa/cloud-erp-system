from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderDetailResponse, OrderListResponse, OrderResponse
from app.services import order_service


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
) -> OrderResponse:
    order = order_service.create_order(db, order_in)
    return OrderResponse(message="Order created successfully", data=order)


@router.get("", response_model=OrderListResponse)
def list_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> OrderListResponse:
    orders = order_service.list_orders(db, skip=skip, limit=limit)
    return OrderListResponse(data=orders)


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
) -> OrderDetailResponse:
    order = order_service.get_order(db, order_id)
    return OrderDetailResponse(data=order)
