""""""

"""
Задание 1 - easy

Напишите код, который находит все видимые кнопки на странице и в цикле нажимает на каждую из них.

"""

buttons = page.get_by_role("button").all()
for button in buttons:
    if button.is_visible():
        button.click()

# код пишем тут

"""
Задание 2  - medium
Напишите скрипт заходит на сайт https://localapi-doc-en.adspower.com/,
и собирает адреса всех ссылок на странице в список, после чего переходит по каждой ссылке.

"""

page.goto("https://localapi-doc-en.adspower.com/")
links = page.locator("a").all()
links_list = [link.get_attribute("href") for link in links]
for link in links_list:
    if not link:
        continue

    page.goto(link)


# код пишем тут

"""
Задание 3 - hard
Напишите скрипт, который переходит на сайт https://pancakeswap.finance/info/v3
и собирает информацию о каждом токене из списка Top Tokens в список словарей:
{
    "number": "4",
    "name": "Ethereum Token",
    "price": "$3.15K",
    "price_change": "↑0.04%",
    "volume_24h": "$36.76M",
    "TVL": "$34.87M",
    "link": "https://pancakeswap.finance/info/v3/tokens/0x2170ed0880ac9a755fd29b2688956bd959f933f8"
}
"""

page.goto('https://pancakeswap.finance/info/v3')
tokens_block = page.locator('//h2[text()="Top Tokens"]/following-sibling::div').first
tokens = tokens_block.get_by_role('link').all()
tokens_info = []
for token in tokens:
    token_data = token.inner_text()
    number, name, _, price, price_change, volume_24h, TVL = token_data.split('\n')
    token_info = {}
    token_info['number'] = number
    token_info['name'] = name
    token_info['price'] = price
    token_info['price_change'] = price_change
    token_info['volume_24h'] = volume_24h
    token_info['TVL'] = TVL
    token_info['link'] = token.get_attribute('href')
    tokens_info.append(token_info)

print(tokens_info)




# код пишем тут

