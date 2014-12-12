#!/usr/bin/env python2
import bs4 as BeautifulSoup
import requests
import grequests
import time
import uuid
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta

def login(login, password):
    s.get('https://teleservices.paris.fr/srtm/jsp/web/index.jsp')
    data = {'login': login, 'password': password}
    s.post('https://teleservices.paris.fr/srtm/authentificationConnexion.action', data=data)

def getTennisList(s):
    r = s.get('https://teleservices.paris.fr/srtm/reservationCreneauInit.action')
    soup = BeautifulSoup.BeautifulSoup(r.text)
    tennis = soup.find(attrs={'name': 'tennisArrond'})
    tlist = []
    for tennis in tennis.findAll('option'):
        split = tennis['value'].split('@',1) 
        if len(split) == 2:
            tlist.append({'name': split[0], 'arrdt': split[1]})
    return tlist

def crawl(alert):
    data = {
        'actionInterne': 'recherche',
        'provenanceCriteres': 'true',
    }

    if alert['allArrdt']:
        data['tousArrondissements'] = 'on'

    if alert['coveredCourt']:
        data['courtCouvert'] = 'on'

    date = datetime.now()
    results = []
    # If we already booked a tennis court getting the list will fail if we don't first do that request
    r = s.get('https://teleservices.paris.fr/srtm/reservationCreneauInit.action')
    print(r.text)

    url = 'https://teleservices.paris.fr/srtm/reservationCreneauListe.action'

    for i in range(1,8):
        data['dateDispo'] = '{:%d/%m/%Y}'.format(date)
        print(data['dateDispo'])
        reqs = []

        for heureDispo in range(alert['startHour'], alert['endHour']):
            data['heureDispo'] = heureDispo
            r = s.post(url, data=data)
            soup = BeautifulSoup.BeautifulSoup(r.text)
            pagelinks = soup.find(attrs={'class': 'pagelinks'})
            pages = 0
            if pagelinks:
                links = pagelinks.findAll('a')
                if len(links) > 0:
                    pages = int(links[-1]['href'].split('d-41734-p=')[1].split('&')[0])
                else:
                    pages = 1
            for page in range(0, pages):
                data['d-41734-p'] = page
                reqs.append(grequests.post(url, data=data, session=s))

        results.extend(grequests.map(reqs))
        date = date + timedelta(days=1)
    return results

def checkAlerts():
    for i in db.alerts.find():
        crawl(i)


if __name__ == '__main__':
    db = MongoClient().tennis
    s = requests.Session()
    login('171091026', '5434')
    #login(s, '020689053', '7498')
    #getInfos(s)
    #getTennisList(s)
    #results = crawl(s, True, False)
    print(checkAlerts())
