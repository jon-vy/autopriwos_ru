import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import re

def parser(url):
    id_item = re.findall('(?<=/).*?(?=/)',url)[-1]

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": generate_user_agent()
    }
    r = requests.get(url=url, headers=headers)
    html_cod = r.text
    soup = BeautifulSoup(html_cod, "lxml")
    title = soup.find('h1').text

    cat = soup.find('ul', class_='breadcrumb').text
    if cat.find("вигатель") != -1:
        category_id = "0"
    elif cat.find("втоматическая") != -1:
        category_id = "1"

    elif cat.find("еханическ") != -1:
        category_id = "2"

    elif cat.find("аздаточн") != -1:
        category_id = "3"
    elif cat.find("Редуктор переднего моста") != -1:
        category_id = "4"
    elif cat.find("Редуктор задний") != -1:
        category_id = "5"

    elif cat.find("ТНВД") != -1:
        category_id = "4"
    elif cat.find("урбин") != -1:
        category_id = "7"

    url_img = ""
    a_list = soup.find_all('a', class_='fancybox')
    for url in a_list:
        url_img = f"{url_img} {url.get('href')} |"

    specifications = {}
    table = soup.find('table', id='_part_details_table').find_all('tr')
    for tr in table:
        # снятые запчасти
        if tr.find('td', class_='bg-warning text-danger'):
            parts = {}
            table_parts = soup.find('div', id='table-resp').find_all('td')
            for data in table_parts:
                parts_key = data.get('data-title')
                parts_val = ' '.join(data.text.split())
                parts[parts_key] = parts_val
            print("q")
        # снятые запчасти
        else:
            key = tr.find('td', class_='text-muted').text.strip()
            if key.find('Консультация специалиста') == -1:
                val = ' '.join(tr.find_all('td')[1].text.strip().split())
            else: break

            if key.find('Цена:') != -1:
                val = tr.find_all('td')[1].find('span', class_="text-danger").text.strip()
            elif key.find('Цена в сборе:') != -1:
                val = re.findall('(?<=\t).*?(?=\r)', tr.find_all('td')[1].text)[0].strip()
            elif key.find('Артикул:') != -1:
                val = val.split(' ')[0].split()


            specifications[key] = val


    print("1")

def main():
    # parser('https://www.autopriwos.ru/catalogue-engines/audi/a6-c5-1997-2005/sku/53823118/index.html')
    parser('https://www.autopriwos.ru/catalogue-engines/audi/a6-c5-1997-2005/sku/53066173/index.html')


if __name__ == '__main__':
    main()