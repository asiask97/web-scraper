from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from requests_html import AsyncHTMLSession
import pandas as pd

URL = 'https://www.flashscore.com/football/england/premier-league-2018-2019/results/'
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(URL)

# Wait for page to fully render 
sleep(25)

#Putting all the ids into array
tags = []

soup = BeautifulSoup(driver.page_source, "html.parser")
for tag in soup.select(".event__match", limit=None) :
    tags.append(tag.get('id'))

driver.quit()

print(tags)

matches = []
for tag in tags:
    new_tag = tag.replace("g_1_", "")
    matches.append(new_tag)
    
print(len(matches))

#making a database
category_list = []
URL_match = 'https://www.flashscore.com/match/'+matches[9]+'/#match-summary/match-statistics/'
    
driver = webdriver.Chrome(r"C:\Users\Asia\.wdm\drivers\chromedriver\win32\91.0.4472.101\chromedriver.exe")
driver.get(URL_match)
# Wait for page to fully render
sleep(5)
soup = BeautifulSoup(driver.page_source, "html.parser")

category = soup.find_all(class_= "categoryName___3Keq6yi")
for c in category:
    category_list.append(c.text)

red =0
yellow =0
passes=0

for c in category_list:
    if c == "Red Cards":
        red +=1
    if c == "Yellow Cards":
        yellow +=1  
    if c == "Completed Passes":
        passes+=1

db = pd.DataFrame(columns = category_list)

if red == 0:
    db.insert( loc = 11, column='Red Cards', value = None)
if yellow == 0:
    db.insert( loc = 12, column='Yellow Cards', value = None)
if passes == 0:
    db.insert( loc = 13, column='Completed Passes', value = None)
db["Team"] = None
db["Goals"] = None
db["Status"] = None
db.to_csv('C:/Users/Asia/Project/live.csv')
driver.quit()


for match in matches:
    #getting all the halftime data
    URL_match = 'https://www.flashscore.com/match/'+match+'/#match-summary/match-statistics/1'
    driver = webdriver.Chrome(r"C:\Users\Asia\.wdm\drivers\chromedriver\win32\91.0.4472.101\chromedriver.exe")
    driver.get(URL_match)
    # Wait for page to fully render
    sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    homedata = []
    awaydata = []
    
    home = soup.find_all(class_= "homeValue___Al8xBea")
    away = soup.find_all(class_= "awayValue___SXUUfSH")
    name = soup.find_all(class_= "participantName___3lRDM1i")
    print(name[1].text, name[2].text)
    namehome = name[1].text
    nameaway = name[2].text
    
    #filling in empty data for yellow and red cards
    category = soup.find_all(class_= "categoryName___3Keq6yi") 
    redcard = 0
    yellowcard = 0
    thrownin = 0
    for c in category:
        
        if c.text == 'Red Cards':
            redcard +=1
        
        if c.text == 'Yellow Cards':
            yellowcard +=1   
            
        if c.text == 'Completed Passes':
            thrownin +=1
    driver.quit()
    
    #getting results
    URL_match_score = 'https://www.flashscore.com/match/'+match+'/#match-summary/match-summary'
    driver = webdriver.Chrome(r"C:\Users\Asia\.wdm\drivers\chromedriver\win32\91.0.4472.101\chromedriver.exe")
    driver.get(URL_match_score)
    # Wait for page to fully render
    sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    #end of the match
    end_scores = soup.find_all(class_= 'wrapper___3rU3Jah')
    second_half = end_scores[0].text 
    print(second_half)
    end_home = second_half[0]
    end_away = second_half[2]
    
    #half time 
    scores = soup.find_all(class_= 'incidentsHeader___7PI0XDi')
    first_half = scores[0].text
    home_score = first_half[-5]
    away_score = first_half[-1]
    driver.quit()
    
    #placing all the data into csv
    for h, a, in zip(home, away):

        homedata.append(h.text)
        awaydata.append(a.text)

    #append 0 to card number place in home and away data sheets

    if redcard == 0:
        homedata.insert(10, '0')
        awaydata.insert(10, '0')
        
    if yellowcard == 0:
        homedata.insert(11, '0')
        awaydata.insert(11, '0') 
        
    if thrownin == 0:
        homedata.insert(-3, '0')
        awaydata.insert(-3, '0')

    homedata.append(namehome)
    awaydata.append(nameaway)
    homedata.append(home_score)
    awaydata.append(away_score)
    
    if end_home > end_away :
        homedata.append('W')
        awaydata.append('L')
    elif end_home == end_away:
        homedata.append('D')
        awaydata.append('D')
    elif end_home < end_away:
        homedata.append('L')
        awaydata.append('W')
      
    #appending all data to csv and skipping mathes with not enough statistics
    if len(homedata) and len(awaydata) == 20:
        db_lenght = len(db)
        db.loc[db_lenght] = homedata
        db.loc[db_lenght+1] = awaydata
        db.to_csv('C:/Users/Asia/Project/live.csv')
    else:
        continue