"""Лабораторная работа №2, вариант 10 — разбор currency.xml.

Вариант 10: словарь «Name - CharCode».
"""
from xml.dom import minidom


def get_text(node, tag):
    """Текст первого дочернего элемента с тегом tag."""
    el = node.getElementsByTagName(tag)[0]
    return el.firstChild.data.strip() if el.firstChild else ""


def parse_name_charcode(path="currency.xml"):
    """Возвращает словарь {Name: CharCode} по всем валютам.

    Кодировка (windows-1251) берётся из XML-декларации, minidom/expat
    декодирует файл сам. Оба поля — строки, приведение типов не требуется
    (для других вариантов Value/Nominal пришлось бы делать
    float(value.replace(',', '.')) и int(nominal))."""
    dom = minidom.parse(path)
    result = {}
    for valute in dom.getElementsByTagName("Valute"):
        result[get_text(valute, "Name")] = get_text(valute, "CharCode")
    return result
