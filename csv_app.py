"""Лабораторная работа №2, вариант 10 — работа с CSV (books.csv / books-en.csv).

Ограничение варианта 10 для выдачи при поиске:
    books.csv     — от 2018 года
    books-en.csv  — от 2000 года
"""
import csv
import html
import random
import re

# Ограничение по году для варианта 10
MIN_YEAR_RU = 2018   # books.csv
MIN_YEAR_EN = 2000   # books-en.csv

TITLE_MAX_LEN = 30   # порог длины названия для задания №1
REFS_COUNT = 20      # сколько библиографических ссылок генерировать


def read_text(path):
    """Читает файл целиком; сначала пробует UTF-8, потом CP1251."""
    for enc in ("utf-8-sig", "cp1251"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось определить кодировку файла {path}")


def find_col(header, *names, default=None):
    """Индекс столбца по названию (сначала точное совпадение, затем по вхождению)."""
    cells = [c.strip().lower() for c in header]
    for name in names:
        if name.lower() in cells:
            return cells.index(name.lower())
    for name in names:
        for i, c in enumerate(cells):
            if name.lower() in c:
                return i
    return default


def get(row, idx):
    """Безопасное получение значения ячейки (строки бывают короче заголовка)."""
    if idx is None or idx >= len(row):
        return ""
    return html.unescape(row[idx].strip())


def parse_year(value):
    """Достаёт год из строки: '15.10.2021 9:22' -> 2021, '2002' -> 2002."""
    m = re.search(r"(?<!\d)(\d{4})(?!\d)", value)
    return int(m.group(1)) if m else None


def load_books(path):
    """Загружает книги в единый формат: список словарей
    {title, author, author_full, year}. Формат (ru/en) определяется по заголовку."""
    text = read_text(path)
    reader = csv.reader(text.splitlines(), delimiter=";")
    header = next(reader)

    books = []
    if find_col(header, "Book-Title") is not None:      # books-en.csv
        i_title = find_col(header, "Book-Title")
        i_author = find_col(header, "Book-Author")
        i_year = find_col(header, "Year-Of-Publication")
        for row in reader:
            if not row:
                continue
            author = get(row, i_author)
            books.append({
                "title": get(row, i_title),
                "author": author,
                "author_full": author,
                "year": parse_year(get(row, i_year)),
            })
        min_year = MIN_YEAR_EN
    else:                                               # books.csv
        i_type = find_col(header, "Тип")
        # поле «Название» — столбец перед «Тип»
        i_title = find_col(header, "Название",
                           default=(i_type - 1) if i_type else 0)
        i_author = find_col(header, "Автор")
        i_author_full = find_col(header, "Автор (ФИО)", default=i_author)
        # В books.csv нет года издания — берём год из «Даты поступления»
        i_date = find_col(header, "Дата поступления")
        for row in reader:
            if not row:
                continue
            books.append({
                "title": get(row, i_title),
                "author": get(row, i_author),
                "author_full": get(row, i_author_full),
                "year": parse_year(get(row, i_date)),
            })
        min_year = MIN_YEAR_RU
    return books, min_year


# ---------- Задание 1: названия длиннее 30 символов ----------
def count_long_titles(books, limit=TITLE_MAX_LEN):
    return sum(1 for b in books if len(b["title"]) > limit)


# ---------- Задание 2: поиск по автору с ограничением варианта ----------
def search_by_author(books, query, min_year):
    """Ищет книги по подстроке в имени автора (без учёта регистра).
    В выдачу попадают только книги, у которых год >= min_year."""
    q = query.strip().lower()
    if not q:
        return []
    return [
        b for b in books
        if (q in b["author"].lower() or q in b["author_full"].lower())
        and b["year"] is not None and b["year"] >= min_year
    ]


def format_book(b):
    return f'{b["author"]}. {b["title"]} - {b["year"]}'


# ---------- Задание 3: генератор библиографических ссылок ----------
def reference_generator(books, count=REFS_COUNT, seed=None):
    """Генератор ссылок вида '<автор>. <название> - <год>' для count случайных записей."""
    valid = [b for b in books if b["author"] and b["title"] and b["year"]]
    rnd = random.Random(seed)
    for b in rnd.sample(valid, min(count, len(valid))):
        yield format_book(b)


def save_references(books, path="references.txt", count=REFS_COUNT, seed=None):
    """Сохраняет ссылки в текстовый файл с нумерацией строк."""
    with open(path, "w", encoding="utf-8") as f:
        for n, ref in enumerate(reference_generator(books, count, seed), start=1):
            f.write(f"{n}. {ref}\n")
    return path
