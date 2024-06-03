from fastapi import APIRouter, HTTPException, status, Depends
from auth import get_current_user
from database import get_db
from sqlalchemy.orm import Session
from models import User, Order
from schemas import OrderModel, OrderModelResponse, OrderItem, CodeValuePair, OrderStatusModel
from typing import List


order_router = APIRouter(
    prefix="/orders",
    tags=['orders']
)


@order_router.get('/')
async def hello(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"message": "hello world"}


@order_router.post('/order', status_code=status.HTTP_201_CREATED, response_model=OrderModelResponse)
async def place_an_order(order: OrderModel, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
        ## Placing an Order
        This requires the following
        - quantity : integer
        - pizza_size: str
    
    """

    user = db.query(User).filter(User.username == current_user.username).first()
    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )

    new_order.user = user

    db.add(new_order)

    db.commit()

    # response = OrderModelResponse(
    #     pizza_size=new_order.pizza_size,
    #     quantity=new_order.quantity,
    #     id=new_order.id,
    #     order_status=new_order.order_status

    # )

    response = OrderModelResponse(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
        id=new_order.id,
        order_status=order.order_status,
        user_id=order.user_id
    )

    return response


@order_router.get('/orders', )
async def list_all_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
        ## List all orders
        This lists all  orders made. It can be accessed by superusers

    """
    user = db.query(User).filter(User.username == current_user.username).first()

    if user.is_staff:
        orders = db.query(Order).all()

        return orders

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not a superuser"
                        )


@order_router.get('/orders/{id}', response_model=OrderItem)
async def get_order_by_id(id: int, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)) -> List[OrderItem]:
    """
    Retrieve an order by its ID.

    This endpoint allows a staff member to retrieve the details of a specific order by its ID.
    Access is restricted to users with staff privileges.

    Parameters:
    - id (int): The unique identifier of the order to be retrieved.
    - current_user (User, optional): The currently authenticated user. This is automatically provided by the dependency.
    - db (Session, optional): The database session. This is automatically provided by the dependency.

    Returns:
    - Order: The order details if found.

    Raises:
    - HTTPException: If the current user is not a staff member (status code 401).
    - HTTPException: If the order with the specified ID is not found (status code 404).


"""
    if not current_user.is_staff:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Not allowed")
    order = db.query(Order).filter(Order.id == id).first()

    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="Order not found")

    return order


@order_router.get('/user/orders', response_model=List[OrderItem])
async def get_user_orders(current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)) -> List[OrderItem]:
    """
        ## Get current user's orders
        This lists the orders made by the currently logged in users
    
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

# Fetch orders made by the current user from the databas
    user_orders = db.query(Order).filter(Order.user_id == current_user.id).all()

    if not user_orders:
        #  if no orders are found, return an empty list
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=" No orders found "
        )

    # handle exception when empty list is returned in endpoint  like {"message": "No orders found"}

    order_items = []

    for order in user_orders:
   
        order_item_dict = {
            "pizza_size": CodeValuePair(code=order.pizza_size.code, value=order.pizza_size.value),
            "order_status": CodeValuePair(code=order.order_status.code, value=order.order_status.value),
            "user_id": order.user_id,
            "quantity": order.quantity,
            "id": order.id
        }
        order_items.append(order_item_dict)

    return order_items


@order_router.get('/user/order/{id}/')
async def get_specific_order(id: int, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    """
        ## Get a specific order by the currently logged in user
        This returns an order by ID for the currently logged in user

    """

    current_order = db.query(Order).filter(Order.id == id).first()

    if current_order is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No order with such id")

    return current_order


@order_router.put('/order/update/{id}/')
async def update_order(id: int, order: OrderModel, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    """
        ## Updating an order
        Updates an order and requires the following fields
        - quantity : integer
        - pizza_size: str

    """
    order_to_update = db.query(Order).filter(Order.id == id).first()

    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    db.add(order_to_update)
    db.commit()

    response = {
                "id": order_to_update.id,
                "quantity": order_to_update.quantity,
                "pizza_size": order_to_update.pizza_size,
                "order_status": order_to_update.order_status,
            }

    return response


@order_router.patch('/order/update/{id}/')
async def update_order_status(id: int, order: OrderStatusModel, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):

    """
        ## Update an order's status
        This is for updating an order's status and requires ` order_status ` in str format
    """

    # current_user = db.query(User).filter(User.username == current_user.username).first()

    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    order_to_update = db.query(Order).filter(Order.id == id).first()

    if order_to_update is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

    order_to_update.order_status = order.order_status

    db.commit()

    response = {
                "id": order_to_update.id,
                "quantity": order_to_update.quantity,
                "pizza_size": order_to_update.pizza_size,
                "order_status": order_to_update.order_status,
            }

    return response


@order_router.delete('/order/delete/{id}/',status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):

    """
        ## Delete an Order
        This deletes an order by its ID
    """
# Check if order to delete exists
# Then delete order

    order_to_delete = db.query(Order).filter(Order.id == id).first()
    if order_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id={id} not found")

    db.delete(order_to_delete)
    db.commit()
    return order_to_delete
