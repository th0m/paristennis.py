#!/usr/bin/env python2
import bs4 as BeautifulSoup
import requests
import grequests
import redis
import time
import uuid
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

    date = datetime.now()
    results = []
    # If we already booked a tennis court getting the list will fail if we don't first do that request
    r = s.get('https://teleservices.paris.fr/srtm/reservationCreneauInit.action')

    url = 'https://teleservices.paris.fr/srtm/reservationCreneauListe.action'

    for i in range(1,8):
        data['dateDispo'] = '{:%d/%m/%Y}'.format(date)
        print(data['dateDispo'])
        reqs = []

        for heureDispo in range(8, 22):
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

def saveResults(results):
    r = redis.Redis('localhost')
    for page in results:
        soup = BeautifulSoup.BeautifulSoup(page.content)
        tbody = soup.tbody
        if tbody:
            for row in tbody.findAll('tr'):
                cells = row.findAll('td')
                key = uuid.uuid4()
                # a : arrdt, d : date, h : hour, c : court, i : info, b : book
                r.lpush(cells[0].string, uuid) 
                r.hmset(key, {
                    'a': cells[1].string,
                    'd': cells[2].string,
                    'h': cells[3].string,
                    'c': cells[4].string,
                    'i': cells[5].string,
                    'b': cells[6].string
                })

def main():
    s = requests.Session()
    login(s, '171091026', '5434')
    #login(s, '020689053', '7498')
    #getInfos(s)
    #getTennisList(s)
    results = crawl(s, True, False)
    saveResults(results)

main()
