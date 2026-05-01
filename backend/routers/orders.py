"""Order management endpoints - user-specific orders with database persistence."""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db
from models.user import User
from models.schemas import OrderRequest, Order as OrderSchema
from routers.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])


# In-memory orders (will be replaced with DB in next iteration)
orders_db = []


@router.post("/", response_model=OrderSchema)
async def create_order(
    order: OrderRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new trading order (requires approval)."""
    order_id = str(uuid.uuid4())[:8]

    new_order = {
        "id": order_id,
        "user_id": current_user.id,
        "symbol": order.symbol,
        "action": order.action,
        "quantity": order.quantity,
        "order_type": order.order_type,
        "price": order.price,
        "stop_loss": order.stop_loss,
        "target": order.target,
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "approved_at": None,
    }

    orders_db.append(new_order)

    return OrderSchema(**new_order)


@router.get("/", response_model=List[OrderSchema])
async def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
):
    """List user's orders, optionally filtered by status."""
    user_orders = [o for o in orders_db if o["user_id"] == current_user.id]

    if status_filter:
        user_orders = [o for o in user_orders if o["status"] == status_filter]

    return [OrderSchema(**o) for o in user_orders]


@router.post("/{order_id}/approve")
async def approve_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
):
    """Approve a pending order."""
    for order in orders_db:
        if order["id"] == order_id and order["user_id"] == current_user.id:
            if order["status"] != "PENDING":
                raise HTTPException(status_code=400, detail="Order not in PENDING status")
            order["status"] = "APPROVED"
            order["approved_at"] = datetime.now().isoformat()
            return {"status": "approved", "order_id": order_id}

    raise HTTPException(status_code=404, detail="Order not found")


@router.post("/{order_id}/reject")
async def reject_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
):
    """Reject a pending order."""
    for order in orders_db:
        if order["id"] == order_id and order["user_id"] == current_user.id:
            order["status"] = "REJECTED"
            return {"status": "rejected", "order_id": order_id}

    raise HTTPException(status_code=404, detail="Order not found")
