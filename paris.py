#!/usr/bin/env python
import bs4 as BeautifulSoup
import requests

def login(s, login, password):
    s.get('https://teleservices.paris.fr/srtm/jsp/web/index.jsp')
    payload = {'login': login, 'password': password}
    s.post('https://teleservices.paris.fr/srtm/authentificationConnexion.action', data=payload)

def getInfos(s):
    r = s.get('https://teleservices.paris.fr/srtm/compteConsulterDonneePersoInit.action')

def getTennisList(s):
    r = s.get('https://teleservices.paris.fr/srtm/reservationCreneauInit.action')
    soup = BeautifulSoup.BeautifulSoup(r.text)
    tennis = soup.find(attrs={"name": 'tennisArrond'})
    tlist = []
    for tennis in tennis.findAll('option'):
        split = tennis['value'].split('@',1) 
        if len(split) == 2:
            tlist.append({'name': split[0], 'arrdt': split[1]})
    return tlist

def getDisponibilities(s):
    r = s.get('https://teleservices.paris.fr/srtm/reservationCreneauInit.action')
    print(r.text)

def main():
    s = requests.Session()
    login(s, '171091026', '5434')
    #getInfos(s)
    #getTennisList(s)
    getDisponibilities(s)

main()
