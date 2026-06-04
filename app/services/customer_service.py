from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.schemas.customer import CustomerCreate


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    existing_customer = db.scalar(
        select(Customer).where(Customer.email == customer_in.email)
    )
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists",
        )

    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def list_customers(db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
    return list(db.scalars(select(Customer).offset(skip).limit(limit)))


def get_customer(db: Session, customer_id: int) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    return customer


def delete_customer(db: Session, customer_id: int) -> int:
    customer = get_customer(db, customer_id)
    order_count = db.scalar(
        select(func.count(Order.id)).where(Order.customer_id == customer_id)
    )

    if order_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a customer that is linked to existing orders",
        )

    db.delete(customer)
    db.commit()
    return customer_id
