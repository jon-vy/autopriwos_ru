import requests
from user_agent import generate_user_agent
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import lxml
import re
import math
import datetime
from xml.dom import minidom
import time
from asyncio import Semaphore


link_list = []
def get_pagin(url):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": generate_user_agent()
    }
    r = requests.get(url=url, headers=headers)
    html_cod = r.text
    soup = BeautifulSoup(html_cod, "lxml")
    try:
        pagination = soup.find('span', class_='label').text.split('/')[1].replace(".", "")
    except:
        pagination = soup.find('span', class_='label').text.split(' ')[2]
    print(pagination)
    return int(pagination)

# <editor-fold desc="Собираю ссылки с категорий">


async def get_link(url, pag, semaphore):
    await semaphore.acquire()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": generate_user_agent()
    }
    params = {
        "pg": pag
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, params=params) as r:
            html_cod = await r.text()
            soup = BeautifulSoup(html_cod, "lxml")
            a_list = soup.find_all('a', itemprop='url')
            for link in a_list:
                link_item = link.get('href')
                print(link_item)
                link_list.append(link_item)
    semaphore.release()

async def gather_get_link():
    semaphore = Semaphore(30)
    urls_category = [
        'https://www.autopriwos.ru/catalogue-engines/auto-parts-by-name/dvs-dvigatel.html',
        'https://www.autopriwos.ru/catalogue-transmission/auto-parts-by-name/kpp-4-st.html',
        'https://www.autopriwos.ru/catalogue-transmission/auto-parts-by-name/kpp-5-st.html',
        'https://www.autopriwos.ru/catalogue-transmission/auto-parts-by-name/kpp-6-st.html',
        'https://www.autopriwos.ru/catalogue-transmission/auto-parts-by-name/kpp-avt.html',
        'https://www.autopriwos.ru/catalogue/auto-parts-by-name/kpp-robot.html',
        'https://www.autopriwos.ru/catalogue/auto-parts-by-name/kpp-reduktor-razdatochnyj-razdatka-kpp.html',
        'https://www.autopriwos.ru/catalogue/auto-parts-by-name/reduktor-perednego-mosta.html',
        'https://www.autopriwos.ru/catalogue/auto-parts-by-name/reduktor-zadnego-mosta.html',
        'https://www.autopriwos.ru/catalogue/auto-parts-by-name/tnvd.html',
        'https://www.autopriwos.ru/catalogue/auto-parts-by-name/turbina.html'
    ]
    for url in urls_category:  # [3:4][8:9]
        pagination = get_pagin(url)

        tasks = []  # список задач
        for pag in range(1, int(pagination)):  #
            task = asyncio.create_task(get_link(url, pag, semaphore))  # создал задачу
            tasks.append(task)  # добавил её в список
        await asyncio.gather(*tasks)


# Собираю ссылки с категорий
# </editor-fold>



# <editor-fold desc="Собираю инфу по ссылкам">
async def parser(link_item, semaphore, root, offers):  #
    await semaphore.acquire()
    id_item = re.findall('(?<=/).*?(?=/)', link_item)[-1]
    offer = root.createElement('offer')
    offers.appendChild(offer)
    offer.setAttribute('id', f'{id_item}')
    offer.setAttribute('available', 'true')

    urlItem = root.createElement('url')
    offer.appendChild(urlItem)
    urlItem_text = root.createTextNode(f'{link_item}')
    urlItem.appendChild(urlItem_text)

    currencyId = root.createElement('currencyId')
    offer.appendChild(currencyId)
    currencyId_text = root.createTextNode('RUB')
    currencyId.appendChild(currencyId_text)

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": generate_user_agent()
    }
    # async with aiohttp.ClientSession() as session:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=200), trust_env=True) as session:
        await asyncio.sleep(3)
        async with session.get(url=link_item, headers=headers) as r:
            html_cod = await r.text()
            soup = BeautifulSoup(html_cod, "lxml")

            title = soup.find('h1').text
            titleItem = root.createElement('title')
            offer.appendChild(titleItem)
            title_text = root.createTextNode(f'{title}')
            titleItem.appendChild(title_text)

            cat = soup.find('ul', class_='breadcrumb').text
            if cat.find("вигатель") != -1:
                category_id = "0"
            elif cat.find("втоматическая") != -1:
                category_id = "1"
            elif cat.find("роботизированная") != -1:
                category_id = "1"
            elif cat.find("еханическ") != -1:
                category_id = "2"
            elif cat.find("аздаточн") != -1:
                category_id = "3"
            elif cat.find("Редуктор переднего моста") != -1:
                category_id = "4"
            elif cat.find("Редуктор заднего моста") != -1:
                category_id = "5"
            elif cat.find("ТНВД") != -1:
                category_id = "6"
            elif cat.find("Турбина") != -1:
                category_id = "7"
            categoryId = root.createElement('categoryId')
            offer.appendChild(categoryId)
            categoryId_text = root.createTextNode(f'{category_id}')
            categoryId.appendChild(categoryId_text)

            url_img = ""
            a_list = soup.find_all('a', class_='fancybox')
            for url in a_list:
                url_img = f"{url_img} {url.get('href')} |"
            picture = root.createElement('picture')
            offer.appendChild(picture)
            picture_text = root.createTextNode(f'{url_img}')
            picture.appendChild(picture_text)


            # specifications = {}
            table = soup.find('table', id='_part_details_table').find_all('tr')
            for tr in table:
                try:
                    key = tr.find('td', class_='text-muted').text.replace(' ', '_').strip()
                    if key.find('Консультация_специалиста') == -1:
                        val = ' '.join(tr.find_all('td')[1].text.strip().split())
                        if val.find('Звоните!') == -1:
                            pass
                        else: break
                    else: break

                    if key.find('Цена:') != -1:
                        val = tr.find_all('td')[1].find('span', class_="text-danger").text.strip()
                    elif key.find('Цена в сборе:') != -1:
                        val = re.findall('(?<=\t).*?(?=\r)', tr.find_all('td')[1].text)[0].strip()
                    elif key.find('Артикул:') != -1:
                        val = val.split(' ')[0].split()[0]

                    key = key.replace(':', '')
                    specificationsItem = root.createElement(f'{key}')  # Создал тег
                    offer.appendChild(specificationsItem)  # Привязал тег
                    specificationsItem_text = root.createTextNode(f"{' '.join(val.split())}")  # Создал текст для тега
                    specificationsItem.appendChild(specificationsItem_text)  # Добавил текст в тег
                except: pass

                # снятые запчасти

            chek = soup.find('table', id='_part_details_table').find_all('tr')[0].text
            if chek.find("Запчасть разукомплектована") != -1:
                table_parts = soup.find('div', id='table-resp').find_all('td')  # нашёл снятые запчасти
                parts = root.createElement('Снятые_запчасти')
                offer.appendChild(parts)
                for data in table_parts:
                    parts_key = data.get('data-title').replace(' ', '_').strip()
                    if parts_key == 'Артикул':
                        pass
                    else:
                        parts_val = ' '.join(data.text.split())

                        partsKey = root.createElement('Запчасть')
                        parts.appendChild(partsKey)
                        partsKey_text = root.createTextNode(f'{parts_val}')
                        partsKey.appendChild(partsKey_text)
            else: pass

                # снятые запчасти
    print(f"{link_item} | {title}")
    semaphore.release()

async def gather_parser(root, offers):  #
    semaphore = Semaphore(30)
    tasks = []
    for link_item in link_list:
        # print(f"Создал задачу с ссылкой {link_item}")
        task = asyncio.create_task(parser(link_item, semaphore, root, offers))  #
        tasks.append(task)
    await asyncio.gather(*tasks)
# </editor-fold>



def main():
    print("Начат сбор ссылок на товары")
    asyncio.get_event_loop().run_until_complete(gather_get_link())
    print("Сбор ссылок закончен")
    print(f"собрано {len(link_list)} ссылок")
    print("Начинаю сбор данных о товаре")
    # <editor-fold desc="xml начало">
    today = datetime.datetime.today()
    date = today.strftime("%Y-%m-%d %H:%M")

    root = minidom.Document()  # основной элемент

    xml_root = root.createElement('yml_catalog')  # создал элемент с именем yml_catalog
    root.appendChild(xml_root)  # добавил его в качестве дочернего к root
    xml_root.setAttribute('date', date)  # Записал данные в элемент xml_root

    shop = root.createElement('shop')
    xml_root.appendChild(shop)

    name = root.createElement('name')
    shop.appendChild(name)
    text_name = root.createTextNode('f-avto.ru')
    name.appendChild(text_name)

    company = root.createElement('company')
    shop.appendChild(company)
    text_name = root.createTextNode('f-avto.ru')
    company.appendChild(text_name)

    url_company = root.createElement('url')
    shop.appendChild(url_company)
    text_name = root.createTextNode('https://f-avto.ru')
    url_company.appendChild(text_name)

    currencies = root.createElement('currencies')
    shop.appendChild(currencies)

    currency = root.createElement('currency')
    currencies.appendChild(currency)
    currency.setAttribute('id', 'RUB')
    currency.setAttribute('rate', '1')

    categories = root.createElement('categories')
    shop.appendChild(categories)

    category_list = [
        "Двигатели",
        "КПП - автомат",
        "КПП - механика",
        "Раздаточные коробки",
        "Редуктор передний",
        "Редуктор задний",
        "ТНВД",
        "Турбины"
    ]
    for i, cat in enumerate(category_list):
        # for cat in category_list:
        category = root.createElement('category')
        categories.appendChild(category)
        category.setAttribute('id', f'{i}')
        textCategory = root.createTextNode(cat)
        category.appendChild(textCategory)

    offers = root.createElement('offers')
    shop.appendChild(offers)

    # </editor-fold>
    asyncio.get_event_loop().run_until_complete(gather_parser(root, offers))  #
    # <editor-fold desc="Сохранение xml">
    xml_str = root.toprettyxml(indent="\t")
    save_path_file = "yandex.xml"
    with open(save_path_file, "w", encoding="utf-8") as f:
        f.write(xml_str)
    # </editor-fold>
    print("Работа закончена")


if __name__ == '__main__':
    start_time = time.time()
    main()
    # asyncio.run(parser("https://f-avto.ru/goods/d3845399"))
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Затрачено времени {total_time} сек {total_time / 60} мин")
    # Затрачено времени 1991.1107165813446 сек 33.185178609689075 мин

