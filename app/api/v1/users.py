from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.users import User
from app.models.shift_assignments import ShiftAssignment
from app.models.shifts import Shift
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего пользователя"""
    return current_user

@router.get("/colleagues", response_model=List[UserResponse])
async def get_colleagues(
    city_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить коллег.
    - Worker: возвращает всех worker в своем городе
    - Admin: если передан city_id - по этому городу, иначе всех worker
    """
    if current_user.role == "worker":
        # Worker видит только коллег из своего города
        stmt = select(User).where(
            User.city_id == current_user.city_id,
            User.role == "worker",
            User.id != current_user.id
        )
    else:
        # Admin видит всех worker, optionally filtered by city_id
        stmt = select(User).where(User.role == "worker")
        if city_id:
            stmt = stmt.where(User.city_id == city_id)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить профиль пользователя. Worker может видеть только коллег из своего города."""
    from sqlalchemy import select
    import uuid
    stmt = select(User).where(User.id == uuid.UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверка доступа для worker
    if current_user.role == "worker":
        if user.city_id != current_user.city_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return user

@router.get("/{user_id}/shifts-count")
async def get_user_shifts_count(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить количество отработанных смен (со статусом completed) для пользователя."""
    from sqlalchemy import select, func
    import uuid
    
    # Проверка доступа для worker
    if current_user.role == "worker":
        target_user_id = uuid.UUID(user_id)
        if current_user.id != target_user_id and current_user.city_id != current_user.city_id:
            # Проверим, что пользователь в том же городе
            stmt = select(User).where(User.id == target_user_id)
            result = await db.execute(stmt)
            target_user = result.scalar_one_or_none()
            if not target_user or target_user.city_id != current_user.city_id:
                raise HTTPException(status_code=403, detail="Access denied")
    
    # Подсчет завершенных смен
    stmt = (
        select(func.count(ShiftAssignment.id))
        .join(Shift)
        .where(
            ShiftAssignment.user_id == uuid.UUID(user_id),
            Shift.status == "completed"
        )
    )
    result = await db.execute(stmt)
    count = result.scalar()
    
    return {"shifts_count": count}