import asyncio
import config
from database import Database
import api_search as api_search
from aiogram import Bot, types, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import links_operations as links_operations


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

film_database = Database()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # database = sqlite3.connect('data.db')
    await message.answer(config.START_MSG)


@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(config.HELP_MSG)


@dp.message(Command("history"))
async def send_history(message: types.Message):
    history = film_database.retrieve_history(message)

    if not history:
        await message.answer('История пуста')
        return

    output_str = ''     # название и ссылка на кинопоиск
    for row in history:
        output_str += row[2] + '\n' + row[3] + '\n\n'
    await message.answer('История поиска фильмов:\n' + output_str)


@dp.message(Command("stats"))
async def send_stats(message: types.Message):
    stats = film_database.retrieve_stats(message)
    if not stats:
        await message.answer('Статистика пуста')
        return
    await message.reply('Статистика поиска:\n' +
                        '\n'.join([f'{row[2]}:\
                        {row[4]:<3} \n{row[3]}' for row in stats]))


@dp.message()
async def echo(message: Message):
    await message.answer(f'Ищу фильм по запросу "{message.text}"')
    kinopoisk_link = ''
    # получаю первые 10 ссылок по запросу в гугле
    found_items = await api_search.google_api(message.text,
                                              page_num=0,
                                              pirate=True)
    # получаю id фильма на кинопоиске
    film_id = await links_operations.film_id(found_items)

    new_found_items = {}
    if film_id == -1:
        await message.answer("Ссылка на кинопоиск не найдена, повторяю запрос")
        new_found_items = await api_search.google_api(message.text,
                                                      page_num=0,
                                                      pirate=False)
        film_id = await links_operations.film_id(new_found_items)

    # получаю информацию о фильме на кинопоиске
    kinopoisk_json = await api_search.kinopoisk_api(film_id)

    if kinopoisk_json:
        film_description = f'{kinopoisk_json["nameRu"]} \n\
        Год: {kinopoisk_json["year"]}\n\
        {kinopoisk_json["description"]}'

        await message.reply_photo(photo=kinopoisk_json["posterUrl"],
                                  caption=film_description)
        kinopoisk_link = kinopoisk_json["webUrl"]

    pirate_links = await links_operations.pirate_links(found_items)

    # если делали дополнительный запрос, можно попробовать взять ссылки оттуда
    if new_found_items:
        pirate_links.update(
            await links_operations.pirate_links(new_found_items)
        )

    if pirate_links:
        await message.answer(f'Ссылки на онлайн просмотр:\n\
        {'\n'.join(pirate_links)}')
    else:
        await message.answer('Ссылки на онлайн просмотр не найдены,\
        повторяю запрос')
        found_items = await api_search.google_api(
            message.text, page_num=1, pirate=True
        )
        pirate_links = await links_operations.pirate_links(found_items)
        await message.answer(f'Ссылки на онлайн просмотр:\n\
        {'\n'.join(pirate_links)}')

    film_database.add_note(message, kinopoisk_json, kinopoisk_link)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
