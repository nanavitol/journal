# -- Города --
@router.get("/cities", response_model=list[CityResponse])
async def get_cities(
    admin_token: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    cities = await db.execute(select(City))
    return cities.scalars().all()

# -- Посты --
@router.get("/posts", response_model=list[PostResponse])
async def get_posts(
    admin_token: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    posts = await db.execute(select(Post))
    return posts.scalars().all()

# -- Смены --
@router.get("/shifts", response_model=list[ShiftResponse])
async def get_shifts(
    admin_token: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    shifts = await db.execute(select(Shift))
    return shifts.scalars().all()

# -- Журнал --
@router.get("/journal", response_model=list[JournalEntryResponse])
async def get_journal(
    admin_token: str = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    journal_entries = await db.execute(select(JournalEntry))
    return journal_entries.scalars().all()