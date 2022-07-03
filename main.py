import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import *
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

import tellonym_api

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import credentials
import image_editor as editor
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import random

Window.size = (1000,700)
Window.clearcolor = (.1, .2, .4, .4)
 
Builder.load_string("""
<Login>
    knopf1: btn_data
    knopf2: btn_bot
 
    GridLayout:
        cols: 1
        size: root.width,root.height
        GridLayout:
            cols: 1
            spacing: 0, 60
            padding: 0, 1
            Label:
                text: "Tellonym Tracker"
                font_size: 40
                height: 20
            Label:
                text: 'Developed by Johannes Krüger\\n        Website: www.jksd.de'
                size_hint: 0.5, 5
                pos_hint: {'center_x':0.5,'center_y':0.45}
        Button:
            size_hint: (0.1, 0.5)
            text:"Tellonym-Data"
            id: btn_data
            font_size: 30
            height: 28
            background_color: (0.694, 0.705, 0.784, 1.0)
            on_release: 
                root.manager.current = "tracker_data"
                root.manager.transition.direction = "left"
        Button:
            size_hint: (0.1, 0.5)
            text:"Tellonym Question Bot"
            id: btn_bot
            font_size: 30
            background_color: (0.694, 0.705, 0.784, 1.0)
            on_release: 
                root.manager.current = "geheim"
                root.manager.transition.direction = "right"
 
<geheimerBereich>:
    GridLayout:
        cols: 1
        size: root.width,root.height
        Label:
            text: "Question-Bot"
            font_size: 30
        GridLayout:
            cols: 2
            Label:
                text: "source"
                font_size: 30
            TextInput:
                id: source
                multiline: False
                font_size: 30
            Label:
                text: "target"
                font_size: 30
            TextInput:
                id: target
                multiline: False
                font_size: 30
            Label:
                text: "number of repetitions"
                font_size: 30
            TextInput:
                id: number_of_repetitions
                multiline: False
                font_size: 30
                input_filter: 'int'
        Button:
            text: "Start"
            font_size: 30
            background_color: (0.015, 0.545, 0.043)
            on_release:
                root.tellonym_question_bot()
        Button:
            text: "zurück"
            font_size: 30
            background_color: (0.921, 0.117, 0.278, 1.0)
            on_release:
                root.manager.current = "login"
                root.manager.transition.direction = "left"

<tracker_data>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: "Tracking-Results"
            font_size: 30
        TextInput:
            id: name_input
            multiline: False
            font_size: 30
        Button:
            text: "Start Tracking"
            font_size: 30
            background_color: (0.015, 0.545, 0.043)
            on_release:
                root.popup()
                root.track()
        Label:
            id: name_label
            text: ""
            font_size: 30
        Label:
            id: tells
            text: ""
            font_size: 30
        Label:
            id: first_tell_question
            text: ""
            font_size: 20
        Label:
            id: first_tell_answer
            text: ""
            font_size: 20
        Label:
            id: first_tell_date
            text: ""
            font_size: 20
        Label:
            id: following
            text: ""
            font_size: 30
        Label:
            id: first_following
            text: ""
            font_size: 20
        Label:
            id: first_following_bio
            text: ""
            font_size: 20
        Label:
            id: first_following_status
            text: ""
            font_size: 20
        Label:
            id: follower
            text: ""
            font_size: 30
        Label:
            id: first_follower
            text: ""
            font_size: 20
        Label:
            id: first_follower_bio
            text: ""
            font_size: 20
        Label:
            id: first_follower_status
            text: ""
            font_size: 20
        Label:
            id: tell_count
            text: ""
            font_size: 30
        Button:
            text: "zurück"
            font_size: 30
            background_color: (0.921, 0.117, 0.278, 1.0)
            on_release:
                root.manager.current = "login"
                root.manager.transition.direction = "right"
 
""")

def tellonym_bot(username, target, number_of_repetitions):
    Tell_List = []

    api = tellonym_api.TellonymApi(False)
    user = api.GetUser(username)
    if not user.IsProfileFound() == True:
        popup = Popup(title='Error',
        content = Label(text="Source-Profile not found"),
        size_hint=(None,None),size=(400,400))
        popup.open()
        return

    user_2 = api.GetUser(target)
    if not user_2.IsProfileFound() == True:
        popup = Popup(title='Error',
        content = Label(text="Target-Profile not found"),
        size_hint=(None,None),size=(400,400))
        popup.open()
        return


    #Fetch Tell-Api-Arrays

    user.FetchTells()

    # Save Api-Data in List (Tells, Followers, Followings)

    objX = user.GetTells()

    def main():
        count = 0
        outfile = open("C:/Users/Johannes/Desktop/tellonym_Bot/data.txt", "w")
        for i in objX:
            try:
                outfile.write(str(i.question) + "\n")
                Tell_List.append(str(i.question))
            except:
                pass
        outfile = open("C:/Users/Johannes/Desktop/tellonym_Bot/data.txt", "r")
        for line in outfile:
            count = count + 1
        outfile.close()

    main()

    DRIVER = webdriver.Chrome(executable_path="C:\\Users\\Johannes\\Desktop\\tellonym_Bot\\cromedriver\\chromedriver.exe")
    URL = "https://tellonym.me/login?redirect=/" + target

    class Bot:
        def __init__(self):
            repetitions_counter = int(number_of_repetitions) - 1
            self.loadPage()
            self.agree_options()
            while repetitions_counter >= 0:
                self.send_tells()
                repetitions_counter = repetitions_counter - 1
            self.number = 0

        def loadPage(self):
            DRIVER.get(URL)
            assert "Tellonym" in DRIVER.title
            email = WebDriverWait(DRIVER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#root > div > div > div.css-1dbjc4n.r-150rngu.r-eqz5dr.r-16y2uox.r-1wbh5a2.r-11yh6sk.r-1rnoaur.r-1sncvnh > div > div > div.rmq-9213326f > div > div:nth-child(2) > form > div:nth-child(1) > input")))
            email.send_keys(credentials.USERNAME)
            email.send_keys(Keys.TAB)

            password = DRIVER.find_element_by_css_selector("#root > div > div > div.css-1dbjc4n.r-150rngu.r-eqz5dr.r-16y2uox.r-1wbh5a2.r-11yh6sk.r-1rnoaur.r-1sncvnh > div > div > div.rmq-9213326f > div > div:nth-child(2) > form > div:nth-child(2) > input")
            password.send_keys(credentials.PASSWORD)
            password.send_keys(Keys.RETURN)
            send = DRIVER.find_element_by_css_selector("#root > div > div > div.css-1dbjc4n.r-150rngu.r-eqz5dr.r-16y2uox.r-1wbh5a2.r-11yh6sk.r-1rnoaur.r-1sncvnh > div > div > div.rmq-9213326f > div > div:nth-child(2) > form > button > div > div")
            send.click

        def agree_options(self):
            assert "Tellonym" in DRIVER.title
            agree = WebDriverWait(DRIVER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled > div > button.sc-ifAKCX.hIGsQq")))
            agree.click()
            selected = WebDriverWait(DRIVER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#qc-cmp2-ui > div.qc-cmp2-footer > div.qc-cmp2-buttons-desktop > button.sc-ifAKCX.hIGsQq")))
            selected.click()

        def send_tells(self):
            tell = DRIVER.find_element_by_css_selector("#root > div > div > div.css-1dbjc4n.r-150rngu.r-eqz5dr.r-16y2uox.r-1wbh5a2.r-11yh6sk.r-1rnoaur > div > div.css-1dbjc4n.r-13qz1uu > div.css-1dbjc4n > div.rmq-f5f56a03 > div > div > div.rmq-27769a9d > div > textarea")
            tell.send_keys(Tell_List[random.randrange(0, int(len(Tell_List)))])
            tell.send_keys(Keys.RETURN)
            send_tell = DRIVER.find_element_by_css_selector("#root > div > div > div.css-1dbjc4n.r-150rngu.r-eqz5dr.r-16y2uox.r-1wbh5a2.r-11yh6sk.r-1rnoaur > div > div.css-1dbjc4n.r-13qz1uu > div.css-1dbjc4n > div.rmq-f5f56a03 > div > div > div > div > div.rmq-27769a9d > div > form > button > div > div.css-901oao.css-bfa6kz")
            send_tell.click()
            print("Tell Sent")
            time.sleep(5)
            
    bot = Bot()


def track_data_by_username(username):
    api = tellonym_api.TellonymApi(False)
    user = api.GetUser(username)
    if not user.IsProfileFound() == True:
        return

    L = []

    #Fetch Tell-Api-Arrays

    user.FetchFollowers()
    user.FetchFollowings()
    user.FetchTells()

    # Save Api-Data in List (Tells, Followers, Followings)

    objX = user.GetTells()
    objY = user.GetFollowings()
    objZ = user.GetFollowers()

    for i in objX:
        try:
            L.append(i)
        except:
            pass
    tell_count = str(len(L))

    return objX, objY, objZ, tell_count


class Login(Screen):
    ben = StringProperty()
    pw = StringProperty()
    knopf = ObjectProperty()
 
class geheimerBereich(Screen):
    def tellonym_question_bot(self):
        tellonym_bot(self.ids.source.text, self.ids.target.text, self.ids.number_of_repetitions.text)


class tracker_data(Screen):
    def track(self):
        try:
            name = self.ids.name_input.text
            self.ids.name_label.text = f'Benutzername:  {name}'
            self.ids.name_input.text = ''
            objX, objY, objZ, tell_count = track_data_by_username(name)
            self.ids.tells.text = 'Tells'
            try:
                self.ids.first_tell_question.text = 'First Tellonym Question: ' + str(objX[0].question)
                self.ids.first_tell_answer.text = 'First Tellonym Answer: ' + str(objX[0].answer)
                self.ids.first_tell_date.text = 'First Tellonym Date: ' + str(objX[0].createdAt) + " || Likes: " + str(objX[0].likeCount)
            except:
                self.ids.first_tell_question.text = 'No Tellonym Questions answered'
                self.ids.first_tell_answer.text = 'No Tellonym Answers'
                self.ids.first_tell_date.text = 'No Data existing'
            
            self.ids.following.text = 'Followings'
            try:
                self.ids.first_following.text = 'First Following: ' + str(objY[0].username) + " || Name: " + str(str(objY[0].displayName))
                self.ids.first_following_bio.text = 'Bio: ' + str(objY[0].bio)
                self.ids.first_following_status.text = 'Status: ' + str(objY[0].isActive)
            except:
                self.ids.first_following.text = 'No Followings'
                self.ids.first_following_bio.text = 'No Data existing'
                self.ids.first_following_status.text = 'No Data existing'

            self.ids.follower.text = 'Followers'
            try:
                self.ids.first_follower.text = 'First Follower: ' + str(objZ[0].username) + " || Name " +  str(str(objZ[0].displayName))
                self.ids.first_follower_bio.text = 'Bio: ' + str(objZ[0].bio)
                self.ids.first_follower_status.text = 'Status: ' + str(objZ[0].isActive)
            except:
                self.ids.first_follower.text = 'No Followers'
                self.ids.first_follower_bio.text = 'No Data existing'
                self.ids.first_follower_status.text = 'No Data existing'

            self.ids.tell_count.text = 'Tell_Count: ' + tell_count

        except:
            pass

    def popup(self):
        api = tellonym_api.TellonymApi(False)
        user = api.GetUser(self.ids.name_input.text)
        if not user.IsProfileFound() == True:
            popup = Popup(title='Error',
            content = Label(text="No Profile found"),
            size_hint=(None,None),size=(400,400))
            popup.open()

ms = ScreenManager()
ms.add_widget(Login(name='login'))
ms.add_widget(geheimerBereich(name='geheim'))
ms.add_widget(tracker_data(name='tracker_data'))
 
class StartApp(App):
    def build(self):
        return ms

if __name__ == "__main__":
    StartApp().run()