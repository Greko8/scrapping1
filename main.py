import requests
import fake_headers
import bs4
import re
import json

headers = fake_headers.Headers(browser="firefox", os="win")
headers_dict = headers.generate()

main_html = requests.get(
    "https://hh.ru/search/vacancy?text=python&area=1&area=2", headers=headers_dict
).text

main_soup = bs4.BeautifulSoup(main_html, "lxml")

div_vacancy_list = main_soup.find("div", id="a11y-main-content")
vacancies = div_vacancy_list.find_all("div", class_="serp-item")

vacancies_info = []

for vacancy in vacancies:
    salary = "не указана"
    h3_tag = vacancy.find("h3")
    a_tag = h3_tag.find("a")
    link = a_tag["href"]
    salary_tag = vacancy.find("span", class_=re.compile(r"bloko-header-section-\d+"))
    if salary_tag:
        salary = salary_tag.text
    company = vacancy.find("a", class_="bloko-link").text
    company_address = vacancy.find(
        "div", attrs={"data-qa": "vacancy-serp__vacancy-address"}
    ).text
    city = re.search(r"^[\w-]+[$,]*", company_address)[0]
    city_name = re.sub(",", "", city)
    vacancy_html = requests.get(link, headers=headers.generate()).text
    vacancy_soup = bs4.BeautifulSoup(vacancy_html, "lxml")
    description_tag = vacancy_soup.find("div", class_="vacancy-description")
    description = vacancy_soup.find(
        "div", attrs={"data-qa": "vacancy-description"}
    ).text
    if len(re.findall(r"Django|Flask", description)) != 0:
        vacancies_info.append(
            {"link": link, "salary": salary, "company": company, "city": city_name}
        )
data = {}
data["info"] = vacancies_info
with open("data/result.json", "w", encoding="utf-8") as file:
    json.dump(data, file)
