def generate_login(full_name: str, city_name: str, db_session) -> str:
    """
    Генерирует логин по правилу:
    1. Фамилия транслитерируется целиком (заглавная первая буква, остальные строчные)
    2. Добавляются первые буквы имени и отчества (заглавные латиницей)
    3. Добавляется первая буква города (заглавная латиницей)
    4. Если такой логин уже существует, добавляется минимальная цифра начиная с 2

    Транслитерация:
    а-a, б-b, в-v, г-g, д-d, е-e, ё-e, ж-zh, з-z, и-i, й-y, к-k, л-l, м-m, н-n, о-o, п-p, р-r, с-s, т-t, у-u, ф-f, х-kh, ц-ts, ч-ch, ш-sh, щ-shch, ъ-ie, ы-y, ь-', э-e, ю-iu, я-ia
    """
    from sqlalchemy import select
    from app.models.users import User

    # Транслитерация согласно ТЗ
    translit_map = str.maketrans(
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "abvgdeejzhzijklmnoprstufkhztschshshchiey'eiuiaABVGDEEjzhzijklmnoprstufkhztschshshchiey'eiuia"
    )

    # Разбор ФИО
    parts = full_name.strip().split()
    if len(parts) < 2:
        raise ValueError("Full name must contain at least surname and name")

    surname = parts[0]
    name = parts[1] if len(parts) > 1 else ""
    patronymic = parts[2] if len(parts) > 2 else ""

    # Транслитерация фамилии
    surname_translit = surname.translate(translit_map)
    surname_translit = surname_translit[0].upper() + surname_translit[1:].lower()

    # Транслитерация и получение инициалов имени и отчества
    initials = ""
    if name:
        initials += name[0].translate(translit_map).upper()
    if patronymic:
        initials += patronymic[0].translate(translit_map).upper()

    # Первая буква города (транслитерируем)
    city_initial = ""
    if city_name:
        city_initial = city_name.translate(translit_map)[0].upper()

    # Базовый логин
    base_login = f"{surname_translit}{initials}{city_initial}"

    # Проверка уникальности
    login = base_login
    counter = 2
    while True:
        stmt = select(User).where(User.login == login)
        result = db_session.execute(stmt)
        if not result.scalar_one_or_none():
            break
        login = f"{base_login}{counter}"
        counter += 1

    return login