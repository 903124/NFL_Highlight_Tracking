from bs4 import BeautifulSoup
from seleniumwire import webdriver
import json
import pandas as pd
import numpy as np
import time
from selenium.common.exceptions import ElementClickInterceptedException
driver_path = r"/Path/to/webdriver/chromedriver.exe" #Or  r"/Path/to/webdriver/geckodriver.exe" 
driver = webdriver.Chrome(executable_path=driver_path) #Or webdriver.Firefox(executable_path=driver_path)



out_df = pd.DataFrame({})

for week in range(5): #loop for week

    driver.get("https://nextgenstats.nfl.com/highlights/play-list/type/team/2019/" + str(18+j) +  "/playerId/playerNameSlug")  #post season start at "week 18"
    time.sleep(13)



    for scroll_page in range(4): #scroll page for more highlight
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    play_link_list = soup.find_all('a', {"class": "highlight-container-link"},href=True) 


    for play in range(len(play_link_list)): 
        time.sleep(3)

        if (play == 0 ):
            driver.get("https://nextgenstats.nfl.com" + event_link_list[0]['href'])
            time.sleep(5)
            if (week == 0):
                cookie_button = driver.find_element_by_xpath('/html/body/div[1]/div/a')
                cookie_button.click()
                complete_request = driver.requests

        try: #press "next play" button

            submit_button = driver.find_elements_by_xpath('/html/body/div[2]/div[5]/main/div/div/div[2]/div/div[2]/div[1]/div/div[1]/button/div/i')[0]
            submit_button.click()
        except  (ElementClickInterceptedException,IndexError ) as e:
            continue


for request in driver.requests: #collect data from requsted json file
    address_path = request.path

    if('slim' in address_path ):
        text = request.response.body
    #                     print(text)
        try:
            data = json.loads(text.decode('utf-8'))

            home_df = (pd.concat({i: pd.DataFrame(x) for i, x in pd.DataFrame(data['homeTrackingData']).pop('playerTrackingData').items()})
                       .reset_index(level=1, drop=True)
                       .join(pd.DataFrame(data['homeTrackingData']))
                       .reset_index(drop=True))[['dir','o' ,'s','time','x' ,'y','displayName','nflId'  ,'position']]

            away_df = (pd.concat({i: pd.DataFrame(x) for i, x in pd.DataFrame(data['awayTrackingData']).pop('playerTrackingData').items()})
                       .reset_index(level=1, drop=True)
                       .join(pd.DataFrame(data['awayTrackingData']))
                       .reset_index(drop=True))[['dir','o' ,'s','time','x' ,'y','displayName','nflId'  ,'position']]


            ball_df = pd.DataFrame(data['ballTrackingData'])[['s' ,'time' ,'x' ,'y']]
            ball_df.columns = ['s' ,'time' ,'x' ,'y']
            ball_df['displayName'] = 'ball'
            temp_df = pd.concat([home_df,away_df,ball_df])
            temp_df['game_id'] = data['gameId']
            temp_df['play_id'] = data['gsisPlayId']

            event_df = pd.DataFrame(data['events'])[['name','time']]
            event_df.columns = ['event_name','time']
            temp_df['time'] = pd.to_datetime(temp_df['time'])
            event_df['time'] = pd.to_datetime(event_df['time'])
            event_df['time'] = event_df['time'].dt.round("100ms")

            temp_df = pd.merge(temp_df,event_df,how='left')
            out_df = pd.concat([out_df,temp_df ])


        except json.JSONDecodeError:
            continue
out_df.to_csv('NFL_Highlight_Tracking/Highlight_19_post.csv')