import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import text
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Функции для работы с командами
def load_commands():
    try:
        with open("commands.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_commands(commands):
    try:
        with open("commands.json", "w", encoding="utf-8") as f:
            json.dump(commands, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка сохранения команд: {e}")
        raise


# Обработчик команды /addc
@dp.message(Command(commands=["addc"]))
async def add_command(message: types.Message):
    args = message.text.split(None, 2)
    if len(args) < 2:
        await message.reply("Используйте: /addc <имя_команды> <текст>\nТы че серьезно??? Может еще документацию написать ахахаха")
        return

    command_name, response_text = args[1:]
    command_name = command_name.lstrip("/")  # Удаляем /, если пользователь его добавил

    commands = load_commands()
    commands[command_name] = response_text

    try:
        save_commands(commands)
        await message.reply(f"Команда `/{command_name}` добавлена. Тегай скок хочешь броски\nТекст: {response_text}")
    except Exception as e:
        await message.reply("Не удалось сохранить команду. Соси жопу")


@dp.message(Command(commands=["show"]))
async def show_command(message: types.Message):
    commands = load_commands()
    s = '\nСписок команд:\n\n'
    for i in commands.keys():
        s += f'/{i}: {commands[i]}\n\n'
    await message.reply(f"```{s}```", parse_mode="Markdown")


@dp.message(Command(commands=["delete"]))
async def delete_command(message: types.Message):
    commands = load_commands()
    try:
        commands.pop(message.text.split(' ')[1])
        save_commands(commands)
        await message.reply("Команда удалена")
    except:
        await message.reply("Такой команды нет")


# Обработчик пользовательских команд
@dp.message(lambda message: message.text.startswith("/"))
async def handle_custom_command(message: types.Message):
    command_name = message.text.split()[0][1:].split("@")[0]
    commands = load_commands()

    if command_name in commands:
        await message.reply(commands[command_name])
    else:
        await message.reply("Команда не найдена. Поплачь еще")


# Стандартные команды
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.reply(
        "Салют! Я бот для создания команд.\n"
        "Добавь команду: /addc <имя> <текст>\n"
        "Например: /addc hello Иди нахуй"
    )

if __name__ == "__main__":
    if not os.path.exists("commands.json"):
        with open("commands.json", "w") as f:
            f.write("{}")

    asyncio.run(dp.start_polling(bot, skip_updates=True))