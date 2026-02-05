import re


async def film_id(found_items: dict) -> int:
    kinopoisk_links = []
    # чтобы убрать всякие кинопоиск топ 500
    pattern = r"(\/film\/|\/series\/)"
    for item in found_items:
        full_link = item.get("link")
        print(f'displayLink = {item.get("displayLink")},\
        full_link = {full_link}')
        if (item.get("displayLink") == 'www.kinopoisk.ru'
           and re.search(pattern, full_link)):
            kinopoisk_links.append(full_link)

    if not kinopoisk_links:         # нет подходящих ссылок
        return -1

    print(kinopoisk_links)

    pattern = r'\d{2,}'     # получаю заветные циферки ID
    for url in kinopoisk_links:
        found_id = re.findall(pattern, url)
        if found_id:
            return found_id[0]
    return -1


async def pirate_links(found_items: dict) -> set:
    prohibited_sites = {
        'okko.tv',
        'www.ivi.tv',
        'www.ivi.ru',
        'kinobar.my',
        'www.kinopoisk.ru',
        'kinogo.inc',
        'wink.ru'
    }
    pirate_links = set()
    pattern = r"(?=.*онлайн)"
    for item in found_items:
        print(f'snippet = {item.get("snippet")}, title = {item.get("title")}')
        if (item.get("displayLink") not in prohibited_sites
            and (re.search(pattern, item.get("snippet").lower())
                 or re.search(pattern, item.get("title").lower()))):
            pirate_links.add(item.get("link"))
    return pirate_links
