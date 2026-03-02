import asyncio
import logging
import os
import threading
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from flask import Flask

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = "8574535040:AAHqkLpcFgJ9xq8rPWjMehs5r1bXlbfB00s"

# Дни недели
WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== РАСПИСАНИЕ В КОДЕ ==================
# Все данные расписания хранятся прямо здесь!
SCHEDULE_DATA = [
    # Психология (37.03.01)
    {"group": "Психология (37.03.01)", "date": "02.03.2026", "day": "Понедельник", "time": "18:40 - 20:15", "room": "4-541", "type": "Лекционные занятия", "subject": "Гражданское население в противодействии распространению идеологии терроризма", "teacher": "Овчинников Д.А."},
    {"group": "Психология (37.03.01)", "date": "03.03.2026", "day": "Вторник", "time": "10:25 - 12:00", "room": "3-107", "type": "Лекционные занятия", "subject": "Оказание первой помощи", "teacher": "Корнеева Л.Н."},
    {"group": "Психология (37.03.01)", "date": "03.03.2026", "day": "Вторник", "time": "12:40 - 14:15", "room": "Спортзал", "type": "Элективные дисциплины", "subject": "Физическая культура и спорт", "teacher": "Цветкова Л.Н., Орехов А.И., Девятиярова Е.А., Михалева О.В., Солнцева Н.С., Шестакова Т.А."},
    {"group": "Психология (37.03.01)", "date": "03.03.2026", "day": "Вторник", "time": "14:25 - 16:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Психология развития и возрастная психология", "teacher": "Шелиспанская Э.В."},
    {"group": "Психология (37.03.01)", "date": "04.03.2026", "day": "Среда", "time": "12:40 - 14:15", "room": "4-540", "type": "Лекционные занятия", "subject": "Деловая коммуникация в профессиональной деятельности", "teacher": "Яковлева А.А."},
    {"group": "Психология (37.03.01)", "date": "04.03.2026", "day": "Среда", "time": "14:25 - 16:00", "room": "4-540", "type": "Практические занятия", "subject": "Учебная ознакомительная практика", "teacher": "Бобровникова Н.С."},
    {"group": "Психология (37.03.01)", "date": "04.03.2026", "day": "Среда", "time": "16:10 - 17:45", "room": "4-540", "type": "Практические занятия", "subject": "Общая психология с практикумом", "teacher": "Бобровникова Н.С."},
    {"group": "Психология (37.03.01)", "date": "05.03.2026", "day": "Четверг", "time": "08:40 - 10:15", "room": "4-519", "type": "Лекционные занятия", "subject": "Психолингвистика", "teacher": "Чихачева Т.А."},
    {"group": "Психология (37.03.01)", "date": "05.03.2026", "day": "Четверг", "time": "10:25 - 12:00", "room": "4-530", "type": "Практические занятия", "subject": "Психология развития и возрастная психология", "teacher": "Бобровникова Н.С."},
    {"group": "Психология (37.03.01)", "date": "05.03.2026", "day": "Четверг", "time": "12:40 - 14:15", "room": "4-541", "type": "Лекционные занятия", "subject": "Основы российской государственности", "teacher": "Солопов О.В."},
    {"group": "Психология (37.03.01)", "date": "05.03.2026", "day": "Четверг", "time": "14:25 - 16:00", "room": "4-519", "type": "Практические занятия", "subject": "Основы российской государственности", "teacher": "Солопов О.В."},
    {"group": "Психология (37.03.01)", "date": "06.03.2026", "day": "Пятница", "time": "08:40 - 10:15", "room": "2-306", "type": "Практические занятия", "subject": "Иностранный язык (немецкий)", "teacher": "Бессонова Н.В."},
    {"group": "Психология (37.03.01)", "date": "06.03.2026", "day": "Пятница", "time": "08:40 - 10:15", "room": "4-540", "type": "Практические занятия", "subject": "Иностранный язык (английский)", "teacher": "Волкова Е.В."},
    {"group": "Психология (37.03.01)", "date": "06.03.2026", "day": "Пятница", "time": "10:25 - 12:00", "room": "2-306", "type": "Практические занятия", "subject": "Иностранный язык (немецкий)", "teacher": "Бессонова Н.В."},
    {"group": "Психология (37.03.01)", "date": "06.03.2026", "day": "Пятница", "time": "10:25 - 12:00", "room": "4-540", "type": "Практические занятия", "subject": "Иностранный язык (английский)", "teacher": "Кудинова О.А."},
    {"group": "Психология (37.03.01)", "date": "07.03.2026", "day": "Суббота", "time": "10:25 - 12:00", "room": "4-519", "type": "Практические занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Архипцева М.С."},
    {"group": "Психология (37.03.01)", "date": "07.03.2026", "day": "Суббота", "time": "12:40 - 14:15", "room": "4-540", "type": "Практические занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Архипцева М.С."},
    {"group": "Психология (37.03.01)", "date": "07.03.2026", "day": "Суббота", "time": "12:40 - 14:15", "room": "4-541", "type": "Практические занятия", "subject": "Основы российской государственности", "teacher": "Солопов О.В."},
    {"group": "Психология (37.03.01)", "date": "07.03.2026", "day": "Суббота", "time": "14:25 - 16:00", "room": "4-540", "type": "Лекционные занятия", "subject": "Социальная психология с практикумом", "teacher": "Шалагинова К.С."},
    {"group": "Психология (37.03.01)", "date": "07.03.2026", "day": "Суббота", "time": "16:10 - 17:45", "room": "4-519", "type": "Лекционные занятия", "subject": "Психология конфликта", "teacher": "Шалагинова К.С."},
    
    # Психолого-педагогическое образование (44.03.02)
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "02.03.2026", "day": "Понедельник", "time": "10:25 - 12:00", "room": "4-528а", "type": "Лекционные занятия", "subject": "Психология конфликта", "teacher": "Шалагинова К.С."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "02.03.2026", "day": "Понедельник", "time": "12:40 - 14:15", "room": "4-528а", "type": "Лекционные занятия", "subject": "Введение в логопедическую специальность", "teacher": "Лещенко С.Г."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "02.03.2026", "day": "Понедельник", "time": "14:25 - 16:00", "room": "4-540", "type": "Лекционные занятия", "subject": "Психология развития и возрастная психология", "teacher": "Пазухина С.В."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "03.03.2026", "day": "Вторник", "time": "10:25 - 12:00", "room": "4-541", "type": "Лекционные занятия", "subject": "Психология общения и речевые практики", "teacher": "Залыгаева С.А."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "03.03.2026", "day": "Вторник", "time": "12:40 - 14:15", "room": "4-540", "type": "Практические занятия", "subject": "Педагогика", "teacher": "Катков Д.Р."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "03.03.2026", "day": "Вторник", "time": "14:25 - 16:00", "room": "4-116", "type": "Практические занятия", "subject": "Педагогика", "teacher": "Яковлева А.А."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "04.03.2026", "day": "Среда", "time": "08:40 - 10:15", "room": "4-540", "type": "Лекционные занятия", "subject": "Общая психология с практикумом", "teacher": "Хвалина Н.А."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "04.03.2026", "day": "Среда", "time": "10:25 - 12:00", "room": "4-514", "type": "Лекционные занятия", "subject": "Психология развития и возрастная психология", "teacher": "Хвалина Н.А."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "04.03.2026", "day": "Среда", "time": "12:40 - 14:15", "room": "4-514", "type": "Лекционные занятия", "subject": "Педагогика", "teacher": "Федотенко И.Л."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "04.03.2026", "day": "Среда", "time": "14:25 - 16:00", "room": "4-538", "type": "Практические занятия", "subject": "Введение в логопедическую специальность", "teacher": "Шопина С.А."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "04.03.2026", "day": "Среда", "time": "16:10 - 17:45", "room": "4-538", "type": "Практические занятия", "subject": "Учебная ознакомительная практика", "teacher": "Шопина С.А."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "05.03.2026", "day": "Четверг", "time": "10:25 - 12:00", "room": "2-75", "type": "Лекционные занятия", "subject": "Основы нейропсихологии", "teacher": "Красникова И.В."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "05.03.2026", "day": "Четверг", "time": "12:40 - 14:15", "room": "4-538", "type": "Практические занятия", "subject": "Возрастная психология", "teacher": "Требушенкова О.Ю."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "06.03.2026", "day": "Пятница", "time": "08:40 - 10:15", "room": "4-540", "type": "Практические занятия", "subject": "Иностранный язык (английский)", "teacher": "Волкова Е.В."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "06.03.2026", "day": "Пятница", "time": "10:25 - 12:00", "room": "4-521", "type": "Практические занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Архипцева М.С."},
    {"group": "Психолого-педагогическое образование (44.03.02)", "date": "06.03.2026", "day": "Пятница", "time": "12:40 - 14:15", "room": "4-540", "type": "Практические занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Архипцева М.С."},
    
    # Специальное (дефектологическое) образование (44.03.03)
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "02.03.2026", "day": "Понедельник", "time": "10:25 - 12:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Социальная психология", "teacher": "Шелиспанская Э.В."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "02.03.2026", "day": "Понедельник", "time": "14:25 - 16:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Социальная педагогика", "teacher": "Карандеева А.В."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "03.03.2026", "day": "Вторник", "time": "08:40 - 10:15", "room": "4-541", "type": "Лекционные занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Петрова М.С."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "03.03.2026", "day": "Вторник", "time": "12:40 - 14:15", "room": "4-541", "type": "Практические занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Архипцева М.С."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "03.03.2026", "day": "Вторник", "time": "14:25 - 16:00", "room": "4-530", "type": "Практические занятия", "subject": "Безопасность жизнедеятельности", "teacher": "Архипцева М.С."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "04.03.2026", "day": "Среда", "time": "08:40 - 10:15", "room": "2-69", "type": "Лекционные занятия", "subject": "Невропатология", "teacher": "Маркова М.П."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "04.03.2026", "day": "Среда", "time": "10:25 - 12:00", "room": "2-69", "type": "Лекционные занятия", "subject": "Невропатология", "teacher": "Маркова М.П."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "04.03.2026", "day": "Среда", "time": "12:40 - 14:15", "room": "4-538", "type": "Практические занятия", "subject": "Психология общения и речевые практики", "teacher": "Бобровникова Н.С."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "04.03.2026", "day": "Среда", "time": "16:10 - 17:45", "room": "4-519", "type": "Лекционные занятия", "subject": "Социальная психология", "teacher": "Шелиспанская Э.В."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "05.03.2026", "day": "Четверг", "time": "10:25 - 12:00", "room": "4-519", "type": "Практические занятия", "subject": "Иностранный язык (английский)", "teacher": "Данилова Ю.С."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "05.03.2026", "day": "Четверг", "time": "14:25 - 16:00", "room": "4-530", "type": "Практические занятия", "subject": "Социальная психология", "teacher": "Шалагинова К.С."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "06.03.2026", "day": "Пятница", "time": "08:40 - 10:15", "room": "4-519", "type": "Практические занятия", "subject": "Психолингвистика", "teacher": "Корабельникова Е.И."},
    {"group": "Специальное (дефектологическое) образование (44.03.03)", "date": "06.03.2026", "day": "Пятница", "time": "12:40 - 14:15", "room": "4-519", "type": "Практические занятия", "subject": "Социальная педагогика", "teacher": "Карандеева А.В."},
    
    # Педагогика и психология девиантного поведения (44.05.01)
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "02.03.2026", "day": "Понедельник", "time": "10:25 - 12:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Психология конфликта", "teacher": "Шалагинова К.С."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "02.03.2026", "day": "Понедельник", "time": "14:25 - 16:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Социальная педагогика", "teacher": "Карандеева А.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "03.03.2026", "day": "Вторник", "time": "10:25 - 12:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Психология личности педагога и обучающегося", "teacher": "Куликова Т.И."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "03.03.2026", "day": "Вторник", "time": "12:40 - 14:15", "room": "4-116", "type": "Лекционные занятия", "subject": "Возрастная психология", "teacher": "Кацеро А.А."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "03.03.2026", "day": "Вторник", "time": "14:25 - 16:00", "room": "2-77", "type": "Лекционные занятия", "subject": "Нейрофизиология", "teacher": "Красников Г.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "03.03.2026", "day": "Вторник", "time": "16:10 - 17:45", "room": "2-77", "type": "Лекционные занятия", "subject": "Нейрофизиология", "teacher": "Красников Г.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "04.03.2026", "day": "Среда", "time": "08:40 - 10:15", "room": "4-514", "type": "Лекционные занятия", "subject": "Социальная психология", "teacher": "Шалагинова К.С."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "04.03.2026", "day": "Среда", "time": "10:25 - 12:00", "room": "4-514", "type": "Лекционные занятия", "subject": "Социальная психология", "teacher": "Шалагинова К.С."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "04.03.2026", "day": "Среда", "time": "12:40 - 14:15", "room": "4-519", "type": "Лекционные занятия", "subject": "Психологическое консультирование по проблемам девиантного поведения", "teacher": "Шелиспанская Э.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "04.03.2026", "day": "Среда", "time": "14:25 - 16:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Психологическое консультирование по проблемам девиантного поведения", "teacher": "Шелиспанская Э.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "05.03.2026", "day": "Четверг", "time": "10:25 - 12:00", "room": "4-519", "type": "Лекционные занятия", "subject": "Основы нейропсихологии", "teacher": "Красникова И.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "05.03.2026", "day": "Четверг", "time": "14:25 - 16:00", "room": "2-75", "type": "Лекционные занятия", "subject": "Основы нейропсихологии", "teacher": "Красникова И.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "06.03.2026", "day": "Пятница", "time": "10:25 - 12:00", "room": "4-519", "type": "Практические занятия", "subject": "Психология общения и речевые практики", "teacher": "Подкопаева Е.С."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "06.03.2026", "day": "Пятница", "time": "14:25 - 16:00", "room": "4-519", "type": "Практические занятия", "subject": "Основы нейропсихологии", "teacher": "Красникова И.В."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "07.03.2026", "day": "Суббота", "time": "08:40 - 10:15", "room": "4-519", "type": "Практические занятия", "subject": "Учебная ознакомительная практика", "teacher": "Бобровикова Н.С."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "07.03.2026", "day": "Суббота", "time": "12:40 - 14:15", "room": "2-108", "type": "Лабораторные занятия", "subject": "Оказание первой помощи", "teacher": "Ибрагимова Т.А."},
    {"group": "Педагогика и психология девиантного поведения (44.05.01)", "date": "07.03.2026", "day": "Суббота", "time": "14:25 - 16:00", "room": "2-108", "type": "Лабораторные занятия", "subject": "Оказание первой помощи", "teacher": "Ибрагимова Т.А."},
]

# ================== РАБОТА С РАСПИСАНИЕМ ==================
class ScheduleDatabase:
    def __init__(self):
        self.schedule = SCHEDULE_DATA
        self.groups = sorted(list(set(item["group"] for item in self.schedule)))
        logger.info(f"✅ Загружено {len(self.schedule)} записей из памяти")
        logger.info(f"📋 Найдены группы: {', '.join(self.groups)}")
    
    def get_groups_list(self) -> list:
        return self.groups
    
    def get_schedule_for_date(self, group: str, target_date: datetime) -> list:
        """Получить расписание на конкретную дату"""
        result = []
        target_date_str = target_date.strftime('%d.%m.%Y')
        
        for lesson in self.schedule:
            if lesson["group"] == group and lesson["date"] == target_date_str:
                result.append(lesson)
        
        return sorted(result, key=lambda x: x["time"])
    
    def get_schedule_for_week(self, group: str, start_date: datetime) -> dict:
        """Получить расписание на неделю"""
        # Определяем границы недели
        monday = start_date - timedelta(days=start_date.weekday())
        sunday = monday + timedelta(days=6)
        
        weekly = {day: [] for day in WEEKDAYS}
        
        for lesson in self.schedule:
            if lesson["group"] != group:
                continue
            
            # Парсим дату занятия
            try:
                lesson_date = datetime.strptime(lesson["date"], '%d.%m.%Y')
                if monday <= lesson_date <= sunday:
                    day_name = lesson["day"]
                    if day_name in weekly:
                        weekly[day_name].append(lesson)
            except:
                continue
        
        # Сортируем по времени
        for day in weekly:
            weekly[day] = sorted(weekly[day], key=lambda x: x["time"])
        
        return weekly

# ================== СОСТОЯНИЯ ==================
class ScheduleStates(StatesGroup):
    waiting_for_group = State()
    viewing_schedule = State()

# ================== КЛАВИАТУРЫ ==================
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура"""
    buttons = [
        [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="📆 Завтра")],
        [KeyboardButton(text="📋 Эта неделя"), KeyboardButton(text="📌 Следующая неделя")],
        [KeyboardButton(text="🔍 Выбрать группу")]
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

def get_groups_keyboard(groups: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком групп"""
    if not groups:
        return None
    
    buttons = []
    for i in range(0, len(groups), 2):
        row = []
        row.append(InlineKeyboardButton(text=groups[i], callback_data=f"group_{i}"))
        if i + 1 < len(groups):
            row.append(InlineKeyboardButton(text=groups[i + 1], callback_data=f"group_{i+1}"))
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================== ИНИЦИАЛИЗАЦИЯ ==================
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
db = ScheduleDatabase()

# ================== ОБРАБОТЧИКИ ==================
@dp.message_handler(Command("start"), state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    
    await message.answer(
        "👋 Привет! Я бот для просмотра расписания ТГПУ\n"
        "Чтобы начать, выберите вашу группу:",
        reply_markup=get_main_keyboard()
    )
    
    await message.answer(
        "📚 Доступные группы:\nВыберите вашу группу:",
        reply_markup=get_groups_keyboard(db.groups)
    )
    await ScheduleStates.waiting_for_group.set()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("group_"), state="*")
async def process_group_selection(callback: CallbackQuery, state: FSMContext):
    group_index = int(callback.data.replace("group_", ""))
    
    if 0 <= group_index < len(db.groups):
        group = db.groups[group_index]
        await state.update_data(selected_group=group)
        await ScheduleStates.viewing_schedule.set()
        
        await callback.message.edit_text(f"✅ Выбрана группа: {group}")
        await callback.message.answer(
            f"Что хотите узнать?",
            reply_markup=get_main_keyboard()
        )
    else:
        await callback.message.edit_text("❌ Ошибка выбора группы")
    
    await callback.answer()

@dp.message_handler(lambda message: message.text == "📅 Сегодня", state=ScheduleStates.viewing_schedule)
async def cmd_today(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data.get("selected_group")
    
    if not group:
        await ScheduleStates.waiting_for_group.set()
        await message.answer("Сначала выберите группу!")
        return
    
    today = datetime.now()
    lessons = db.get_schedule_for_date(group, today)
    
    if not lessons:
        await message.answer(f"📅 {today.strftime('%d.%m.%Y')}\n___________________________________\n\nПар нет 🎉")
        return
    
    text = f"📅 {today.strftime('%d.%m.%Y')}\n___________________________________\n"
    for i, lesson in enumerate(lessons):
        text += f"\n{lesson['time']}  📚"
        text += f"\n🏛 {lesson['room']}"
        text += f"\n📖 {lesson['type']}"
        text += f"\n📚 {lesson['subject']}"
        text += f"\n👨‍🏫 {lesson['teacher']}"
        if i < len(lessons) - 1:
            text += "\n" + "-" * 40 + "\n"
    
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📆 Завтра", state=ScheduleStates.viewing_schedule)
async def cmd_tomorrow(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data.get("selected_group")
    
    if not group:
        await ScheduleStates.waiting_for_group.set()
        await message.answer("Сначала выберите группу!")
        return
    
    tomorrow = datetime.now() + timedelta(days=1)
    lessons = db.get_schedule_for_date(group, tomorrow)
    
    if not lessons:
        await message.answer(f"📅 {tomorrow.strftime('%d.%m.%Y')}\n___________________________________\n\nПар нет 🎉")
        return
    
    text = f"📅 {tomorrow.strftime('%d.%m.%Y')}\n___________________________________\n"
    for i, lesson in enumerate(lessons):
        text += f"\n{lesson['time']}  📚"
        text += f"\n🏛 {lesson['room']}"
        text += f"\n📖 {lesson['type']}"
        text += f"\n📚 {lesson['subject']}"
        text += f"\n👨‍🏫 {lesson['teacher']}"
        if i < len(lessons) - 1:
            text += "\n" + "-" * 40 + "\n"
    
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📋 Эта неделя", state=ScheduleStates.viewing_schedule)
async def cmd_this_week(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data.get("selected_group")
    
    if not group:
        await ScheduleStates.waiting_for_group.set()
        await message.answer("Сначала выберите группу!")
        return
    
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    weekly = db.get_schedule_for_week(group, today)
    
    text = f"📋 Текущая неделя (с {monday.strftime('%d.%m')})\n" + "=" * 40 + "\n"
    
    has_lessons = False
    for i, day in enumerate(WEEKDAYS):
        day_lessons = weekly[day]
        current_date = monday + timedelta(days=i)
        
        if day_lessons:
            has_lessons = True
            text += f"\n📅 {day}, {current_date.strftime('%d.%m')}\n" + "-" * 30 + "\n"
            
            for lesson in day_lessons:
                text += f"\n{lesson['time']}  📚"
                text += f"\n🏛 {lesson['room']}"
                text += f"\n📖 {lesson['type']}"
                text += f"\n📚 {lesson['subject']}"
                text += f"\n👨‍🏫 {lesson['teacher']}\n"
    
    if not has_lessons:
        text += "\nНа этой неделе пар нет 🎉"
    
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📌 Следующая неделя", state=ScheduleStates.viewing_schedule)
async def cmd_next_week(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data.get("selected_group")
    
    if not group:
        await ScheduleStates.waiting_for_group.set()
        await message.answer("Сначала выберите группу!")
        return
    
    next_week = datetime.now() + timedelta(weeks=1)
    monday = next_week - timedelta(days=next_week.weekday())
    weekly = db.get_schedule_for_week(group, next_week)
    
    text = f"📌 Следующая неделя (с {monday.strftime('%d.%m')})\n" + "=" * 40 + "\n"
    
    has_lessons = False
    for i, day in enumerate(WEEKDAYS):
        day_lessons = weekly[day]
        current_date = monday + timedelta(days=i)
        
        if day_lessons:
            has_lessons = True
            text += f"\n📅 {day}, {current_date.strftime('%d.%m')}\n" + "-" * 30 + "\n"
            
            for lesson in day_lessons:
                text += f"\n{lesson['time']}  📚"
                text += f"\n🏛 {lesson['room']}"
                text += f"\n📖 {lesson['type']}"
                text += f"\n📚 {lesson['subject']}"
                text += f"\n👨‍🏫 {lesson['teacher']}\n"
    
    if not has_lessons:
        text += "\nНа следующей неделе пар нет 🎉"
    
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "🔍 Выбрать группу", state="*")
async def cmd_change_group(message: types.Message, state: FSMContext):
    await ScheduleStates.waiting_for_group.set()
    await message.answer(
        "📚 Доступные группы:\nВыберите вашу группу:",
        reply_markup=get_groups_keyboard(db.groups)
    )

@dp.message_handler(state="*")
async def handle_unknown(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == ScheduleStates.viewing_schedule.state:
        await message.answer(
            "Используйте кнопки для навигации 👆",
            reply_markup=get_main_keyboard()
        )
    elif current_state == ScheduleStates.waiting_for_group.state:
        await message.answer(
            "⚠️ Сначала выберите группу через кнопку '🔍 Выбрать группу'"
        )
    else:
        await message.answer(
            "👋 Отправьте /start для начала работы"
        )

async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск бота...")
    await dp.start_polling()

# ================== FLASK СЕРВЕР ДЛЯ RAILWAY ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот расписания ТГПУ работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Запуск бота в отдельном потоке"""
    asyncio.run(main())

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Бот запущен в фоновом потоке")
    
    # Запускаем Flask сервер для Railway
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Запуск Flask сервера на порту {port}")
    app.run(host="0.0.0.0", port=port)
