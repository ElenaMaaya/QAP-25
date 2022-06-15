#  python -m pytest -v --driver Chrome --driver-path C://chromedriver/chromedriver.exe tests/test_selenium_petfriends_2531.py

import pytest
from settings import valid_name, valid_email, valid_password
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def autoriz():
    """Загружает веб-драйвер Хром, меняет размер окна, устанавливает явные и неявные ожидания,
  открывает страницу авторизации Pet Friends, авторизуется на сайте, после выполнения основного кода закрывает браузер"""

    pytest.driver = webdriver.Chrome('C:/chromedriver/chromedriver.exe')
    pytest.driver.set_window_size(1280, 720)
    pytest.driver.implicitly_wait(10)

    # Переходим на страницу авторизации

    pytest.driver.get('https://petfriends.skillfactory.ru/login')

    valid_email = "elena.maaya@yandex.ru"
    valid_password = "1qaz2wsx"
    valid_name = "Maaya"

    # Вводим email

    WebDriverWait(pytest.driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
    pytest.driver.find_element_by_id('email').send_keys(valid_email)

    # Вводим пароль

    WebDriverWait(pytest.driver, 10).until(EC.presence_of_element_located((By.ID, 'pass')))
    pytest.driver.find_element_by_id('pass').send_keys(valid_password)

    # Нажимаем на кнопку входа в аккаунт

    pytest.driver.find_element_by_css_selector('button[type="submit"]').click()

    yield

    pytest.driver.quit()


def test_login_pass():
    """Тест проверяет загрузку страницы "Все питомцы"""

    # Проверка, что мы на главной странице

    assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"


def test_show_all_pets():
    """Тест проверяет наличие фото у питомца;
     наличие имени, возраста и породы"""

    # Получение массива данных из таблицы всех питомцев
    images_all_pets = pytest.driver.find_elements_by_css_selector('.card-deck.card-img-top')
    names_all_pets = pytest.driver.find_elements_by_css_selector('.card-deck.card-title')
    descriptions_all_pets = pytest.driver.find_elements_by_css_selector('.card-deck.card-text')

    # Внутри соответствующего массива есть имя питомца, возраст и вид

    for i in range(len(names_all_pets)):
        # Проверяем наличие атрибута src у картинки
        assert images_all_pets[i].get_attribute('src') != ''
        # Проверяем элемент, который должен содержать его имя, имеет не пустой текст
        assert names_all_pets[i].text != ''
        # Проверяем, что в элементе выводится и возраст, и вид питомца
        assert descriptions_all_pets[i].text != ''
        assert ', ' in descriptions_all_pets[i]
        parts = descriptions_all_pets[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def test_show_my_pets():
    """Тест проверяет загрузку страницы "Мои питомцы";
   наличие имени, возраста и породы;
   в статистике пользователя и в таблице одинаковое количество питомцев;
   хотя бы у половины питомцев есть фото;
   в таблице нет повторяющихся питомцев и повторяющихся имен питомцев"""

    # Открываем страницу Мои питомцы

    pytest.driver.find_element_by_xpath("//a[@href='/my_pets']").click()

    # Проверяем, что мы оказались на странице пользователя My Pets
    assert pytest.driver.find_element_by_tag_name('h2').text == valid_name

    # Получение массива данных из таблицы моих питомцев
    images_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr th img')
    names_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr td:nth-of-type(1)')
    types_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr td:nth-of-type(2)')
    ages_my_pets = pytest.driver.find_elements_by_css_selector('div#all_my_pets table tbody tr td:nth-of-type(3)')

    # Получение количества питомцев из статистики пользователя
    data_stat = pytest.driver.find_element_by_css_selector('html body div div div').text.split('\n')
    count_my_pets = int((data_stat[1].split(' '))[1])

    # Вводим переменные для подсчета питомцев с именем, с фото, для сбора данных питомцев в списки и в массивы.
    count_name = 0
    count_img = 0
    list_names = []
    list_types = []
    list_ages = []
    list_my_pets = []
    unique_list_my_pets = []

    for j in range(len(names_my_pets)):
        count_name += 1

        if images_my_pets[j].get_attribute('src') != '':
            count_img += 1

        list_names += names_my_pets[j].text.split(", ")
        list_types += types_my_pets[j].text.split(", ")
        list_ages += ages_my_pets[j].text.split(", ")
        list_my_pets.append([names_my_pets[j].text, types_my_pets[j].text, ages_my_pets[j].text])

        if list_my_pets[j] not in unique_list_my_pets:
            unique_list_my_pets.append(list_my_pets[j])



        # У всех питомцев есть имя, возраст и порода
        assert names_my_pets[j].text != ''
        assert types_my_pets[j].text != ''
        assert ages_my_pets[j].text != ''

    # Присутствуют все питомцы
    assert count_my_pets == count_name, "ERROR: В статистике пользователя " \
                                                      "и в таблице разное количество питомцев"

    # Хотя бы у половины питомцев есть фото
    assert count_my_pets // 2 <= count_img, "ERROR: Фото есть менее, чем у " \
                                                                              "половины питомцев"

    # У всех питомцев разные имена
    assert len(list_names) == len(set(list_names)), 'ERROR: Есть питомцы с повторяющимися именами'

    # В списке нет повторяющихся питомцев
    assert len(list_my_pets) == len(unique_list_my_pets), 'ERROR: Есть не уникальный питомец'



def test_exit():
    """Тест проверяет работу кнопки "Выйти"""

    pytest.driver.find_element_by_xpath("//button[@class='btn btn-outline-secondary']").click()
    assert pytest.driver.find_element_by_xpath(
        "//button[@class='btn btn-success']").text == 'Зарегистрироваться', 'ERROR: ошибка Log Out'
