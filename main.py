import os
from urllib import parse
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager


BASEURL = 'https://megamarket.ru'


def get_pages_html(url,pages):
    chrome_install = ChromeDriverManager().install()

    folder = os.path.dirname(chrome_install)
    chromedriver_path = os.path.join(folder, "chromedriver.exe")

    driver = uc.Chrome(driver_executable_path=chromedriver_path)
    
    driver.maximize_window()
    
    ITEMS = []
    try:
        driver.get(url)
        replaced_url = driver.current_url
        new_url = replaced_url.rsplit('/', 1)
        new_url = f"{new_url[0]}/page/{new_url[1]}"
        for page in range(1, pages+1):
            print(f"[+] Страница {page}")
            replaced_url = new_url.replace(f'page', f'page-{page}')
            print(f"Listen on: {replaced_url}")

            driver.get(url=replaced_url)
            replaced_url = driver.current_url

            WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.TAG_NAME, "html")))
            
            if not get_items_new(driver.page_source, ITEMS):
                break

    # except Exception as ex:
    #     print(f"Exeption: {ex}")

    finally:
        driver.close()
        driver.quit()

    return ITEMS


def write_to_html(html):
    with open('test1.html', 'w') as f:
        print("written html")
        f.write(html)
        f.close()

#only for example
def get_items(html, items):
    soup = BeautifulSoup(html, 'html.parser')
    items_divs = soup.find_all('div', class_='catalog-items-list')
    print(f"len items: {len(items_divs)}")
    if len(items_divs) == 0:
        return False
    for i, item in enumerate(items_divs):
        print(f"item №{i}:\n  {item}")
        link = BASEURL + item.find('a', class_='ddl_product_link').get('href')
        item_price = item.find('div', class_='item-price')
        if item_price:
            item_price_result = item_price.find('span').get_text()
            item_bonus = item.find('div', class_='item-bonus')
            if item_bonus:
                item_bonus_percent = item.find('span', class_='bonus-percent').get_text()
                item_bonus_amount = item.find('span', class_='bonus-amount').get_text()
                item_title = item.find('div', class_='item-title').get_text()
                item_merchant_name = item.find('span', class_='merchant-info__name')
                if item_merchant_name:
                    item_merchant_name = item_merchant_name.get_text()
                else:
                    item_merchant_name = '-'

                bonus = int(item_bonus_amount.replace(' ', ''))
                price = int(item_price_result[0:-1].replace(' ', ''))
                bonus_percent = int(item_bonus_percent.replace('%', ''))
                items.append({
                    'Наименование': item_title,
                    'Продавец': item_merchant_name,
                    'Цена': price,
                    'Сумма бонуса': bonus,
                    'Процент бонуса': bonus_percent,
                    'Ссылка на товар': link
                })
    return True

def get_items_new(html, items):
    soup = BeautifulSoup(html, 'html.parser')
    items_divs = soup.find_all('div', attrs={'data-test' : 'product-item'})
    
    if len(items_divs) == 0:
        return False
    

    for i, item in enumerate(items_divs):
        link = BASEURL + item.find('a', attrs={'data-test' : 'product-name-link'}).get('href')
        item_price = item.find('div', attrs={'data-test' : 'product-price'})
            
        if item_price:
            item_price_result = item_price.get_text().strip()
            item_bonus_percent = item.find('span', attrs={'data-test' : 'bonus-percent'})

            if item_bonus_percent:
                item_bonus_percent = item_bonus_percent.get_text().strip()
                bonus_percent = int(item_bonus_percent.replace('%', ''))
            else:
                bonus_percent = 0
    
            item_bonus_amount = item.find('span', attrs={'data-test' : 'bonus-amount'})

            if item_bonus_amount:
                item_bonus_amount = item_bonus_amount.get_text().strip()
                bonus = int(item_bonus_amount.replace(' ', ''))
            else:
                bonus = 0
            
            item_title = item.find('a', attrs={'data-test' : 'product-name-link'}).get_text().strip()
            item_merchant_name = item.find('span', attrs={'data-test' : 'merchant-name'})

            if item_merchant_name:
                item_merchant_name = item_merchant_name.get_text().strip()
            else:
                item_merchant_name = '-'

            price = int(item_price_result[0:-1].replace(' ', ''))

            #print(f"item #{i}:\n    {link}\n    {price}\n   {bonus_percent}\n   {bonus}\n   {item_title}\n     {item_merchant_name}")

            items.append({
                'Наименование': item_title,
                'Продавец': item_merchant_name,
                'Цена': price,
                'Сумма бонуса': bonus,
                'Процент бонуса': bonus_percent,
                'Ссылка на товар': link
            })
    return True


def save_excel(data: list, filename: str):
    """сохранение результата в excel файл"""
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(f'data/{filename}.xlsx')
    df.to_excel(writer, sheet_name='data', index=False)
    # указываем размеры каждого столбца в итоговом файле
    writer.sheets['data'].set_column(0, 1, width=50)
    writer.sheets['data'].set_column(1, 2, width=30)
    writer.sheets['data'].set_column(2, 3, width=8)
    writer.sheets['data'].set_column(3, 4, width=20)
    writer.sheets['data'].set_column(4, 5, width=15)
    writer.close()
    print(f'Все сохранено в {filename}.xlsx')

def main():
    target = input('Введите название товара: ')
    
    pages_count = int(input('Введите количество страниц для просмотра: '))

    target_url = f"{BASEURL}/catalog/?q={target}"
    items = get_pages_html(url=target_url, pages= pages_count)

    save_excel(items, target)


if __name__ == '__main__':
    main()