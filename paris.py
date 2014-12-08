#!/usr/bin/env python2
import bs4 as BeautifulSoup
import requests
import grequests
import redis
from datetime import datetime
from datetime import timedelta

def login(s, login, password):
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

def crawl(s, tousArrondissements, courtCouvert):
    data = {
        'actionInterne': 'recherche',
        'provenanceCriteres': 'true',
    }

    if tousArrondissements:
        data['tousArrondissements'] = 'on'

    if courtCouvert:
        data['courtCouvert'] = 'on'

    url = 'https://teleservices.paris.fr/srtm/reservationCreneauListe.action'
    date = datetime.now()
    results = []

    #for i in range(1,3):
    for i in range(1,8):
        #date = date + timedelta(days=1)
        data['dateDispo'] = '{:%d/%m/%Y}'.format(date)
        reqs = []

        #for heureDispo in range(20, 22):
        for heureDispo in range(8, 22):
            data['heureDispo'] = heureDispo
            r = s.post(url, data=data)
            soup = BeautifulSoup.BeautifulSoup(r.text)
            pagelinks = soup.find(attrs={'class': 'pagelinks'})
            pages = 0
            key = data['dateDispo']+':'+str(heureDispo)
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

def saveResults(results):
    i = 0
    r = redis.Redis('localhost')
    for page in results:
        soup = BeautifulSoup.BeautifulSoup(page.content)
        tbody = soup.tbody
        if tbody:
            for row in tbody.findAll('tr'):
                cells = row.findAll('td')
                r.hset(cells[0].string, 'arrdt', cells[1].string)
                r.hset(cells[0].string, 'date', cells[2].string)
                r.hset(cells[0].string, 'hour', cells[3].string)
                r.hset(cells[0].string, 'court', cells[4].string)
                r.hset(cells[0].string, 'info', cells[5].string)
                r.hset(cells[0].string, 'book', cells[6].string)
                #r.expire(cells[0].string, 600)

def main():
    s = requests.Session()
    login(s, '171091026', '5434')
    #getInfos(s)
    #getTennisList(s)
    results = crawl(s, True, False)
    saveResults(results)

main()
