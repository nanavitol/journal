from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, date
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.users import User
from app.models.shifts import Shift
from app.models.shift_assignments import ShiftAssignment
from app.models.journal_entries import JournalEntry
from app.models.posts import Post
from app.models.cities import City
from app.schemas.user import UserResponse
from app.schemas.shift import ShiftResponse
from app.schemas.journal import JournalEntryCreate, JournalEntryResponse

router = APIRouter(prefix="/worker", tags=["worker"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    photo_url: str = None,
    phone: str = None,
    rank: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if photo_url is not None:
        setattr(current_user, "photo_url", photo_url)
    if phone is not None:
        setattr(current_user, "phone", phone)
    if rank is not None:
        setattr(current_user, "rank", rank)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/colleagues", response_model=List[UserResponse])
async def get_colleagues(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.city_id == current_user.city_id, User.id != current_user.id)
    result = await db.execute(stmt)
    colleagues = result.scalars().all()
    return colleagues

@router.get("/my-shifts", response_model=List[ShiftResponse])
async def get_my_shifts(
    month: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # month format: YYYY-MM
    year, mon = map(int, month.split("-"))
    start_date = date(year, mon, 1)
    if mon == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, mon + 1, 1)
    stmt = (
        select(Shift)
        .join(ShiftAssignment)
        .where(
            ShiftAssignment.user_id == current_user.id,
            Shift.shift_date >= start_date,
            Shift.shift_date < end_date
        )
    )
    result = await db.execute(stmt)
    shifts = result.scalars().all()
    return shifts

@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
async def get_shift_detail(
    shift_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Shift)
        .join(ShiftAssignment)
        .where(Shift.id == shift_id, ShiftAssignment.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    shift = result.scalar_one_or_none()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found or access denied")
    return shift

@router.get("/shifts/{shift_id}/journal", response_model=List[JournalEntryResponse])
async def get_shift_journal(
    shift_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка, назначен ли пользователь на эту смену
    stmt = select(ShiftAssignment).where(
        ShiftAssignment.shift_id == shift_id,
        ShiftAssignment.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not assigned to this shift")
    stmt = select(JournalEntry).where(JournalEntry.shift_id == shift_id)
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return entries

@router.post("/shifts/{shift_id}/journal", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    shift_id: int,
    entry_in: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка смены и статуса
    shift = await db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    # Проверка назначения
    stmt = select(ShiftAssignment).where(
        ShiftAssignment.shift_id == shift_id,
        ShiftAssignment.user_id == current_user.id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not assigned to this shift")
    if shift.status != "active":
        raise HTTPException(status_code=403, detail="Shift is not active")
    entry = JournalEntry(
        shift_id=shift_id,
        user_id=current_user.id,
        full_name_snapshot=current_user.full_name,
        note=entry_in.note,
        entry_type=entry_in.entry_type
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry