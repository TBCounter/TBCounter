
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from itertools import zip_longest
import jwt
from pytesseract import image_to_string, image_to_data, Output
import easyocr

import numpy as np

from time import sleep, time
import re
from PIL import Image
import imagehash

from random import randint
import os

from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# log_cookie fpc6314ed242d26c3.24711110
# 1515, 166, 793, 190 - chest name
# 900, 170, 1130, 215 - time to dissappear
# 420, 160, 1145, 260 - full image
# 420, 160, 1145, 556 - 4 chests


FILE_PATH = 'H://TotalBattle/'


class OCR_reader:
    def __init__(self) -> None:
        # OCR 1. почему OCR в классе робота
        self.reader = easyocr.Reader(
            ['ru', 'en'], gpu='cuda:0', model_storage_directory='C:\\Users\\Omega\\.EasyOCR\\model', download_enabled=False)

        # подготовить набор идеальных изображений
        pass

    def are_images_identical(self, image_ideal, image_temp, is_image=True):
        if is_image:
            return imagehash.phash(image_ideal, hash_size=32) - imagehash.phash(image_temp, hash_size=32) < 19
        else:
            return imagehash.phash(Image.open(image_ideal), hash_size=32) - imagehash.phash(Image.open(image_temp), hash_size=32) < 19

    def is_button(self, image_temp):
        button_ideal = 'true_images/open_button_truthy.png'
        button_delete = 'true_images/open_button_delete.png'
        open_good = self.are_images_identical(
            Image.open(button_ideal), image_temp)
        open_bad = self.are_images_identical(
            Image.open(button_delete), image_temp)
        return open_bad | open_good

    def read_image_banks(self, image_path):

        tes = image_to_data(image_path, lang='eng',
                            config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789', output_type=Output.DICT)
        easy = self.reader.recognize(image_path)

        tes_conf = float(tes.get('conf')[np.argmax(tes.get('conf'))])
        easy_conf = 0
        if len(easy) > 0:
            easy_conf = easy[0][-1]*100

        if (tes_conf < 70) & (easy_conf < 70):
            return ''
        if (easy_conf > tes_conf):
            return easy[0][-2].strip()
        if (tes_conf > easy_conf):
            return tes.get('text')[np.argmax(tes.get('conf'))].strip()

    def read_image(self, image_path, easy_only=False):
        tes = image_to_data(
            image_path, lang="eng+rus", output_type=Output.DICT)
        easy = self.reader.readtext(image_path)

        tes_conf = float(tes.get('conf')[np.argmax(tes.get('conf'))])
        easy_conf = 0
        if len(easy) > 0:
            easy_conf = easy[0][-1]*100

        if (tes_conf < 40) & (easy_conf < 40):
            return ''

        text = ''
        text_easy = ''
        text_tess = ''
        try:
            text_easy = ' '.join([easy_text[-2].strip() for easy_text in easy])
        except:
            print('error in easy text')
        try:
            text_tess = text = ' '.join(tes.get('text')).strip().replace("Склеп уровня", "Склеп 5 уровня").replace(
                "'", '').replace("‘", '').replace('Cknen', 'Склеп').replace('|', '')
        except:
            print('error in tess text')

        if ((easy_conf > tes_conf) | (len(text_tess) < 2)):
            text = text_easy
        if (tes_conf > easy_conf):
            text = text_tess
        if (easy_only):
            return text_easy

        text = text.replace('"', '').replace("'", "")
        return text


def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)


def robo_killer(url, session_id, account_id):
    driver2 = webdriver.Remote(command_executor=url)
    driver2.close()
    driver2.session_id = session_id
    driver2.save_screenshot(
        FILE_PATH + "temp_images/"+str(account_id)+"_screenshot.png")
    driver2.save_screenshot(
        "before_kill.png")
    driver2.quit()


class Robot:  # Что делает робот? Отвечает за работу в браузере
    # Заходит в браузер, логинится, кликает по кнопкам и делает скриншоты

    def __init__(self, account) -> None:

        self.reader = OCR_reader()

        # данные пользователя
        self.login = account.get('login')
        self.password = jwt.decode(account.get(
            'password'), SECRET_KEY, algorithms="HS256").get('password')

        self.isTriumph = account.get('isTriumph')

        self.avatar = account.get('avatar')

        self.account = account

        # настройки браузера 2. Вынести в конфиг файл
        options = Options()
        # options.add_experimental_option("detach", True)
        options.add_argument("--incognito")
        options.add_argument("--ignore-gpu-blacklist")
        options.add_argument("--use-gl")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        options.add_argument("--headless")
        options.add_argument("window-size=1384,667")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--mute-audio")

        # инициализируем браузера
        self.driver = webdriver.Chrome(
            'chromedriver.exe', options=options)  # селениум
        set_viewport_size(self.driver, 1384, 667)
        self.actions = ActionChains(self.driver)  # селениум
        # заходим на страницу
        if (self.isTriumph):
            print('triumph')
            self.driver.get('https://triumph.totalbattle.com/ru')
        else:
            print('not triumph')
            self.driver.get('https://totalbattle.com/ru')

        print('got page')

        self.url = self.driver.command_executor._url
        self.session_id = self.driver.session_id

        self.trying = 0

        # loaded = self.login_cookie()

    def start(self):
        loaded = self.login_pass()
        if not loaded:
            # self.driver.save_screenshot("beforedeath.png")
            # self.create_checking_screenshot()
            raise Exception('wrong login or password finale')
        if (self.avatar):
            self.update_avatar()

    def update_avatar(self):
        self.actions.send_keys(Keys.ESCAPE).perform()
        sleep(0.5)
        self.driver.save_screenshot("screenshot.png")
        screenshot = Image.open('screenshot.png')
        avatar = screenshot.crop((350, 50, 430, 130))
        avatar.save(self.avatar)

    def info(self):
        self.driver.save_screenshot("screenshot.png")
        screenshot = Image.open('screenshot.png')
        avatar = screenshot.crop((350, 50, 430, 130))

        name = screenshot.crop((445, 78, 650, 98))
        name.save('temp_name.png')
        print('ok saving name')

        # name_text = image_to_string(name, lang="eng+rus").strip()
        name_text = self.reader.read_image('temp_name.png')
        print(name_text)
        # print(image_to_string(name, lang="eng+rus"))

        avatar_path = 'avatars/'+name_text+'.png'
        avatar.save(avatar_path)

        # открываем клан
        self.actions.move_by_offset(
            750, 580).click().perform()  # кнопка "клан"
        sleep(0.5)
        self.actions.click().perform()
        self.actions.move_by_offset(-750, -580).perform()
        sleep(2)
        self.driver.save_screenshot("screenshot.png")
        screenshot = Image.open('screenshot.png')
        clan = screenshot.crop((630, 110, 800, 140))
        clan.save('temp_clan.png')
        # clan_text = self.reader.readtext('temp_clan.png', detail=0)[0]
        clan_text = self.reader.read_image('temp_clan.png')
        # clan_text = image_to_string(clan, lang="eng+rus").strip()
        print('clan', clan_text)

        return avatar_path, name_text, clan_text

    def sleepAndClick(self, path):
        try:
            sleep(2)
            self.driver.find_element(By.XPATH, path).click()
        except:
            print('cant find!', path)
            self.driver.save_screenshot("cantfind.png")

    def sleepPointAndClick(self, x, y):
        self.actions.move_by_offset(x, y).click().perform()
        sleep(randint(1, 10)*0.1)
        self.actions.click().perform()
        self.actions.move_by_offset(-x, -y).perform()

    def typeTextInInput(self, text):
        for char in text:
            self.actions.send_keys(char).pause(randint(1, 10)*0.1).perform()
        pass

    def create_checking_screenshot(self):
        self.driver.save_screenshot(
            FILE_PATH+"temp_images/"+str(self.account['id'])+"_screenshot.png")

    def login_pass(self):
        self.trying = self.trying+1

        if (self.trying > 5):
            print('limit')
            # self.create_checking_screenshot()
            return False
        if(self.isTriumph):
            self.sleepAndClick('/html/body/div[4]/noindex/div[2]/button[1]')
        else:
            self.sleepAndClick('//*[@id="cky-btn-accept"]')
        self.sleepPointAndClick(400, 183)  # 400 180 - log in
        self.sleepPointAndClick(400, 170)  # 400 170 - email
        self.typeTextInInput(self.login)
        self.sleepPointAndClick(400, 230)  # 400 230 - password
        self.typeTextInInput(self.password)
        self.sleepPointAndClick(400, 270)  # 400 270 - button

        sleep(3)

        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="game_frame"]/div[5]/div[1]/div[2]/video')
            print('i found element')
        except:
            self.driver.save_screenshot("wrong.png")
            self.create_checking_screenshot()
            print('wrong login or password cause wrong')

            if (self.isTriumph):
                print('triumph')
                self.driver.get('https://triumph.totalbattle.com/ru')
            else:
                print('not triumph')
                self.driver.get('https://totalbattle.com/ru')

            print('got page')
            sleep(randint(1, 4))

            loaded = self.login_pass()
            return loaded

        sleep(30)
        print('wtf')
        exit_limit = 0
        loaded = self.check_loaded()
        while not loaded:
            loaded = self.check_loaded()
            sleep(10)
            exit_limit += 1
            if(exit_limit > 30):
                print('cant login')
                return False
        sleep(10)
        exit_limit = 0
        exited = False
        while not exited:
            exit_limit += 1
            exited = not self.check_loaded()
            self.actions.send_keys(Keys.ESCAPE).perform()
            sleep(2)
            if(exit_limit > 20):
                print('cant exit')
                return False

        return loaded

    def check_loaded(self):
        self.driver.save_screenshot("checking_screenshot.png")
        checking_screenshot = Image.open('checking_screenshot.png')
        menu = checking_screenshot.crop((1340, 50, 1380, 80))  # 1384, 667
        menu.save('checking_menu.png')  # TODO remove
        self.create_checking_screenshot()

        menu_hash = imagehash.average_hash(menu)
        ideal_menu = imagehash.average_hash(
            Image.open('checking_menu_true.png'))

        # print((menu_hash-ideal_menu == 0) | (menu_hash-ideal_menu_2 == 0)
        #       | (menu_hash-ideal_menu_3 == 0))
        return (menu_hash-ideal_menu == 0)

    def open_gifts_page(self):

        self.actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)
        self.actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)
        self.actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)

        self.actions.move_by_offset(
            750, 580).click().perform()  # кнопка "клан"
        sleep(0.5)
        self.actions.click().perform()
        self.actions.move_by_offset(-750, -580).perform()
        sleep(2)

        self.actions.move_by_offset(
            300, 250).click().perform()  # кнопка "подарки"
        sleep(0.2)
        self.actions.click().perform()
        self.actions.move_by_offset(-300, -250).perform()

    def count_all_chests(self):
        self.driver.save_screenshot("screenshot.png")
        screenshot = Image.open('screenshot.png')

        chests_image = screenshot.crop(
            (620, 115, 645, 140))  # количество сундуков
        chests_image.save('chests.png')
        bank_image = screenshot.crop((865, 115, 890, 140))  # количество банков
        bank_image.save('banks.png')

        chests_count = self.reader.read_image_banks('chests.png')
        banks_count = self.reader.read_image_banks('banks.png')

        print(chests_count)
        print(banks_count)

        fnd = re.findall(r'([\d]+)', chests_count)
        chests = int(fnd[0] if len(fnd) > 0 else 0)

        fnd = re.findall(r'([\d]+)', banks_count)
        banks = int(fnd[0] if len(fnd) > 0 else 0)

        return chests, banks

    def show_open_button(self):
        self.driver.save_screenshot("screenshot.png")
        screenshot = Image.open('screenshot.png')

        open_button_image = screenshot.crop(
            (1024, 215, 1137, 251))  # кнопка открыть сундук
        open_button_image.save(FILE_PATH+'temp_images/open_button.png')
        return open_button_image

    def count_chests_banks(self):
        self.open_gifts_page()
        chests_count, banks_count = self.count_all_chests()

        while (chests_count == 0):
            print('пусто, пробую снова')
            self.open_gifts_page()
            chests_count, banks_count = self.count_all_chests()

        return chests_count, banks_count

    def get_chest_info(self):
        self.driver.save_screenshot(
            FILE_PATH+"temp_images/"+str(self.account['id'])+"_screenshot.png")
        screenshot = Image.open(
            FILE_PATH+"temp_images/"+str(self.account['id'])+"_screenshot.png")

        player_name = screenshot.crop(
            (546, 190, 740, 218))  # место скриншота игрока
        chest_type = screenshot.crop((596, 215, 900, 235))  # тип сундука
        chest_name = screenshot.crop((515, 166, 793, 190))
        time_to_live = screenshot.crop((900, 185, 1130, 215))
        full_chest_image = screenshot.crop((420, 160, 1150, 260))
        all_chests_image = screenshot.crop((420, 120, 1000, 400))

        now = str(time())

        player_name.save(f'{FILE_PATH}temp_images/player_names/{now}.png')
        chest_type.save(f'{FILE_PATH}temp_images/chest_types/{now}.png')
        chest_name.save(f'{FILE_PATH}temp_images/chest_names/{now}.png')
        time_to_live.save(f'{FILE_PATH}temp_images/ttl/{now}.png')
        full_chest_image.save(f'{FILE_PATH}temp_images/full_chests/{now}.png')
        all_chests_image.save(f'{FILE_PATH}temp_images/all_chests/{now}.png')

        return f'{FILE_PATH}temp_images/player_names/{now}.png', f'{FILE_PATH}temp_images/chest_types/{now}.png', f'{FILE_PATH}temp_images/chest_names/{now}.png', f'{FILE_PATH}temp_images/ttl/{now}.png', f'{FILE_PATH}temp_images/full_chests/{now}.png', f'{FILE_PATH}temp_images/all_chests/{now}.png'

    def click_open_button(self):
        self.actions.move_by_offset(1080, 230).perform()  # кнопка открыть
        self.actions.click().perform()
        # кнопка открыть
        self.actions.move_by_offset(-1080, -230).perform()

    def open_chest_and_save(self):

        self.driver.save_screenshot(str(self.account['id'])+"_screenshot.png")
        screenshot = Image.open(str(self.account['id'])+"_screenshot.png")

        player_name = screenshot.crop(
            (546, 190, 740, 218))  # место скриншота игрока
        # место скриншота типа сундука
        chest_type = screenshot.crop((596, 215, 900, 240))
        now = str(time())

        player_name.save('temp_player_name.png')
        player_name.save('names/temp_player_name'+now+'.png')
        chest_type.save('temp_chest_type.png')
        chest_type.save('chests/temp_chest_type'+now+'.png')

        text_name = self.reader.read_image('temp_player_name.png')
        text_type = self.reader.read_image('temp_chest_type.png')

        self.actions.move_by_offset(1080, 230).click(
        ).move_by_offset(-1080, -230).perform()  # кнопка открыть

        passed = self.check_prize(text_name)
        faile = 0

        while not passed:
            self.actions.move_by_offset(1080, 230).perform()  # кнопка открыть
            self.actions.click().perform()
            # кнопка открыть
            self.actions.move_by_offset(-1080, -230).perform()
            sleep(0.1)
            passed = self.check_prize(text_name)
            faile = faile + 1
            if (faile > 10):
                break

        return text_name, text_type, 'names/temp_player_name'+now+'.png'

    def check_prize(self, prev_name):
        self.driver.save_screenshot("check_prize.png")
        screenshot = Image.open('check_prize.png')
        player_name = screenshot.crop((546, 190, 740, 220))
        player_name.save('temp_check_player_name.png')

        text_name = self.reader.read_image('temp_check_player_name.png')
        if(text_name != prev_name):
            print(text_name, prev_name, 'разные имена')
            return True

        prize = screenshot.crop((650, 440, 730, 485))

        prize.save('check_prize_cropped.png')
        text_prize = self.reader.read_image('check_prize_cropped.png')

        print(text_prize, "награда" in text_prize.lower())
        return "награда" in text_prize.lower()

    def banks(self):
        self.actions.move_by_offset(770, 135).perform()
        self.actions.click().perform()
        self.actions.click().perform()
        self.actions.click().perform()
        self.actions.move_by_offset(-770, -135).perform()
        # self.driver.save_screenshot("banks_check.png")
        # banks_check = Image.open("banks_check.png")
        # banks_check.crop((750, 115, 790, 155)).save('banks_check_cropped.png')
        sleep(2)

    def un_banks(self):
        self.actions.move_by_offset(570, 135).perform()
        self.actions.click().perform()
        self.actions.click().perform()
        self.actions.click().perform()
        self.actions.move_by_offset(-570, -135).perform()
        # self.driver.save_screenshot("unbanks_check.png")
        # banks_check = Image.open("unbanks_check.png")
        # banks_check.crop((550, 115, 590, 155)).save(
        #     'unbanks_check_cropped.png')
        sleep(2)

    # (770, 135)  # кнопка для банков
    # (350, 50, 430, 130)  # аватарка
    # (445, 80, 650, 100)  # Имя
    # (630, 110, 760, 140)  # клан
    # (650, 640, 730, 485) # награда


class RobotCookie(Robot):
    def __init__(self, account, url, cookies) -> None:

        self.reader = OCR_reader()
        self.cookies = cookies
        self.gameurl = url
        # данные пользователя

        print(cookies)
        print(self.gameurl)
        self.log_cookie = cookies.get('log_cookie')
        self.cookieyesID = cookies.get('cookieyesID')
        self.PTBHSSID = cookies.get('PTBHSSID')
        self.PTRHSSID = cookies.get('PTBRSSID')

        self.avatar = account.get('avatar')

        self.account = account

        # настройки браузера 2. Вынести в конфиг файл
        options = Options()
        # options.add_experimental_option("detach", True)
        options.add_argument("--incognito")
        options.add_argument("--ignore-gpu-blacklist")
        options.add_argument("--use-gl")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        options.add_argument("--headless")
        options.add_argument("window-size=1384,667")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--mute-audio")

        # инициализируем браузера
        self.driver = webdriver.Chrome(
            'chromedriver.exe', options=options)  # селениум
        set_viewport_size(self.driver, 1384, 667)
        self.actions = ActionChains(self.driver)  # селениум
        # заходим на страницу

        self.driver.get(self.gameurl)

        print('got page')

        self.url = self.driver.command_executor._url
        self.session_id = self.driver.session_id

        self.trying = 0

        # loaded = self.login_cookie()

    def login_pass(self):
        sleep(2)
        self.driver.get(self.gameurl)
        self.driver.delete_all_cookies()
        if(self.log_cookie):
            self.driver.add_cookie(
                {"name": "log_cookie", "value": self.log_cookie})
        if(self.cookieyesID):
            self.driver.add_cookie(
                {"name": "cookieyesID", "value": self.cookieyesID})
        if(self.PTBHSSID):
            self.driver.add_cookie(
                {"name": "PTBHSSID", "value": self.PTBHSSID})
        if(self.PTBHSSID):
            self.driver.add_cookie(
                {"name": "PTRHSSID", "value": self.PTBHSSID})
        self.driver.add_cookie({"name": "cky-action", "value": "yes"})
        self.driver.add_cookie({"name": "cky-consent", "value": "yes"})
        self.driver.add_cookie({"name": "cookieyes-necessary", "value": "yes"})
        self.driver.add_cookie(
            {"name": "cookieyes-functional", "value": "yes"})
        self.driver.add_cookie({"name": "cookieyes-analytics", "value": "yes"})
        self.driver.add_cookie(
            {"name": "cookieyes-perfomance", "value": "yes"})
        self.driver.add_cookie(
            {"name": "cookieyes-advertisement", "value": "yes"})
        self.driver.add_cookie(
            {"name": "cookieyes-other", "value": "yes"})

        self.driver.refresh()
        sleep(2)
        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="cky-btn-accept"]').click()
        except:
            pass

        try:
            self.driver.save_screenshot("wtfaka.png")
            self.driver.find_element(
                By.XPATH, '//*[@id="gameContainer"]')
            print('i found element')
        except:
            self.driver.save_screenshot("wrong_cookie.png")
            print('wrong login or password')
            return False
        sleep(30)
        print('wtf')
        loaded = self.check_loaded()
        exit_limit = 0
        while not loaded:
            loaded = self.check_loaded()
            sleep(10)
            exit_limit += 1
            if(exit_limit > 30):
                print('cant login')
                return False

        print('all rigt, loaded')
        sleep(10)
        exit_limit = 0
        exited = False
        while not exited:
            exit_limit += 1
            exited = not self.check_loaded()
            self.actions.send_keys(Keys.ESCAPE).perform()
            sleep(2)
            if(exit_limit > 20):
                print('cant exit')
                return False

        return loaded


if __name__ == "__main__":
    robot = Robot({"login": "login", "password":"password", "isTriumph":False}) #password should be hashed
