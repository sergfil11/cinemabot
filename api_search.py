import config
import aiohttp


async def google_api(message_text: str | None, page_num: int, pirate: bool) -> dict:
    custom_url = "https://www.googleapis.com/customsearch/v1"
    start = page_num * 10 + 1   # перевод номера страницы в номер ссылки

    if pirate:
        q = f"{message_text} фильм смотреть онлайн бесплатно"
    else:
        q = f"{message_text} фильм кинопоиск"

    params = {
        "key": config.google_api_2,
        "cx": config.SEARCH_ENGINE_API,
        "q": f"{q}",
        "num": 10,                      # считываем 10 запросов со страницы
        "start": start                  # начиная с нужного номера ссылки
    }
    json_items = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(custom_url, params=params) as response:
            if response.status == 200:
                # await message.answer('Выполнен поиск с помощью API')
                json_data = await response.json()
                json_items = json_data.get("items", [])

        return json_items


async def kinopoisk_api(film_id: int) -> dict:
    url = "https://kinopoiskapiunofficial.tech\
    /api/v2.2/films/{}".format(film_id)
    headers = {"X-API-KEY": config.KINOPOISK_API}

    async with aiohttp.ClientSession() as kino_session:
        async with kino_session.get(url, headers=headers) as response:
            if response.status == 200:
                json_data = await response.json()
                return json_data
    return {}
