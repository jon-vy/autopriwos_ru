import aiohttp
import asyncio

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

link_list = []

def get_pagin(url):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": generate_user_agent()
    }
    r = requests.get(url=url, headers=headers)
    html_cod = r.text
    soup = BeautifulSoup(html_cod, "lxml")
    pagination = soup.find('span', class_='label').text.split('/')[1].replace(".", "")
    print(pagination)
    return int(pagination)




def get_link(url):  #, semaphore, pag
    # await semaphore.acquire()
    pagin = get_pagin(url)
    for pag in range(1, pagin):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": generate_user_agent()
        }
        params = {
            "pg": pag
        }
        r = requests.get(url=url, headers=headers, params=params)
        html_cod = r.text
        soup = BeautifulSoup(html_cod, "lxml")
        a_list = soup.find_all('a', itemprop='url')
        for link in a_list:
            link_item = link.get('href')
            print(f"{pag} {link_item}")
            link_list.append(link_item)
    print(f"найдено ссылок {len(link_list)}")
        # semaphore.release()

    # print("1")


def main():
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
    get_link(urls_category[0])
    # asyncio.run(get_link(urls_category[0]))
    # asyncio.get_event_loop().run_until_complete(urls_category[0])
    # get_pagin(urls_category[0])


if __name__ == '__main__':
    main()
