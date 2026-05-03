from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.deps import require_role
from app.models.users import User
from app.models.cities import City
from app.models.posts import Post
from app.models.shifts import Shift
from app.models.shift_assignments import ShiftAssignment
from app.models.journal_entries import JournalEntry
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.city import CityCreate, CityUpdate, CityResponse
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse
from app.schemas.journal import JournalEntryResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# -- Пользователи --
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    from app.core.security import get_password_hash    import uuid
    from sqlalchemy.dialects.postgresql import UUID
    # Проверка уникальности
    for field in ["email", "login"]:
        val = getattr(user_in, field)
        stmt = select(User).where(getattr(User, field) == val)
        if await db.execute(stmt):
            raise HTTPException(status_code=400, detail=f"{field} already exists")
    # Генерация логина, если не задан
    login = user_in.login    if not login:
        translit = str.maketrans("абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                                  "abvgdeejzijklmnoprstufhzcss_yyejujaABVGDEEJZIJKLMNOPRSTUFHZCSS_YYEJUJA")
        base = ''.join(c for c in user_in.full_name.lower().translate(translit) if c.isalnum())
        city = await db.get(City, user_in.city_id) if user_in.city_id else None
        city_suffix = city.name.lower().translate(translit)[:3] if city else "xx"
        login = f"{base}{city_suffix}"
    # Хеш пароля
    password_hash = get_password_hash(user_in.password)
    user = User(
        id=uuid.uuid4(),
        email=user_in.email,
        login=login,
        password_hash=password_hash,
        full_name=user_in.full_name,
        city_id=user_in.city_id,
        role=user_in.role,
        rank=user_in.rank,
        phone=user_in.phone,
        password_changed=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return None
# -- Города --
@router.get("/cities", response_model=list[CityResponse])
async def get_cities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(City))
    return result.scalars().all()

@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(city_in: CityCreate, db: AsyncSession = Depends(get_db)):
    city = City(**city_in.dict())
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city

@router.get("/cities/{city_id}", response_model=CityResponse)
async def get_city(city_id: int, db: AsyncSession = Depends(get_db)):
    city = await db.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.put("/cities/{city_id}", response_model=CityResponse)
async def update_city(city_id: int, city_in: CityUpdate, db: AsyncSession = Depends(get_db)):
    city = await db.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    for field, value in city_in.dict(exclude_unset=True).items():
        setattr(city, field, value)
    await db.commit()
    await db.refresh(city)
    return city

@router.delete("/cities/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(city_id: int, db: AsyncSession = Depends(get_db)):
    city = await db.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    await db.delete(city)
    await db.commit()
    return None

# -- Посты --
@router.get("/posts", response_model=list[PostResponse])
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    return result.scalars().all()

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_in: PostCreate, db: AsyncSession = Depends(get_db)):
    post = Post(**post_in.dict())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_in: PostUpdate, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    for field, value in post_in.dict(exclude_unset=True).items():
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post)
    return post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.commit()
    return None

# -- Смены --
@router.get("/shifts", response_model=list[ShiftResponse])
async def get_shifts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Shift))
    return result.scalars().all()

@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(shift_in: ShiftCreate, db: AsyncSession = Depends(get_db)):
    # Проверка поста
    post = await db.get(Post, shift_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # Проверка уникальности (пост + дата)
    stmt = select(Shift).where(Shift.post_id == shift_in.post_id, Shift.shift_date == shift_in.shift_date)
    if await db.execute(stmt):
        raise HTTPException(status_code=400, detail="Shift for this post and date already exists")
    shift = Shift(**shift_in.dict())
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    return shift@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
async def get_shift(shift_id: int, db: AsyncSession = Depends(get_db)):
    shift = await db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

@router.put("/shifts/{shift_id}", response_model=ShiftResponse)
async def update_shift(shift_id: int, shift_in: ShiftUpdate, db: AsyncSession = Depends(get_db)):
    shift = await db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, value in shift_in.dict(exclude_unset=True).items():
        setattr(shift, field, value)
    await db.commit()
    await db.refresh(shift)
    return shift

@router.delete("/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shift(shift_id: int, db: AsyncSession = Depends(get_db)):
    shift = await db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    await db.delete(shift)
    await db.commit()
    return None

# -- Назначения --
@router.post("/shifts/{shift_id}/assign", status_code=status.HTTP_201_CREATED)
async def assign_to_shift(shift_id: int, user_id: str, is_leader: bool = False, db: AsyncSession = Depends(get_db)):
    shift = await db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Проверка: город сотрудника должен совпадать с городом поста (если worker)
    if user.role == "worker" and user.city_id != shift.post.city_id:
        raise HTTPException(status_code=400, detail="Worker city does not match post city")
    # Проверка: не больше max_workers
    stmt = select(ShiftAssignment).where(ShiftAssignment.shift_id == shift_id)
    result = await db.execute(stmt)
    if len(list(result.scalars())) >= shift.post.max_workers:
        raise HTTPException(status_code=400, detail="Max workers reached")
    # Проверка: не назначен ли уже в эту смену
    stmt = select(ShiftAssignment).where(ShiftAssignment.shift_id == shift_id, ShiftAssignment.user_id == user_id)
    if await db.execute(stmt):
        raise HTTPException(status_code=400, detail="User already assigned to this shift")
    # Проверка: нет ли смены у сотрудника в тот же день
    from datetime import date
    stmt = select(Shift).join(ShiftAssignment).where(
        ShiftAssignment.user_id == user_id,
        Shift.shift_date == shift.shift_date    )
    if await db.execute(stmt):
        raise HTTPException(status_code=400, detail="User already assigned to another shift on this day")
    # Только один старший на смене
    if is_leader:
        stmt = select(ShiftAssignment).where(ShiftAssignment.shift_id == shift_id, ShiftAssignment.is_leader == True)
        if await db.execute(stmt):
            raise HTTPException(status_code=400, detail="Only one leader per shift")
    assignment = ShiftAssignment(shift_id=shift_id, user_id=user_id, is_leader=is_leader)
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return {"message": "Assigned successfully"}

@router.delete("/shifts/{shift_id}/assign/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_from_shift(shift_id: int, user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ShiftAssignment).where(ShiftAssignment.shift_id == shift_id, ShiftAssignment.user_id == user_id)
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await db.delete(assignment)
    await db.commit()
    return None

# -- Журнал (админ) --
@router.get("/journal", response_model=list[JournalEntryResponse])
async def get_journal(
    shift_id: int = None,
    date_from: str = None,
    date_to: str = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(JournalEntry)
    conditions = []
    if shift_id:
        conditions.append(JournalEntry.shift_id == shift_id)
    if date_from:
        conditions.append(JournalEntry.created_at >= date_from)
    if date_to:
        conditions.append(JournalEntry.created_at <= date_to)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return entries