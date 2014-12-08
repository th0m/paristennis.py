#!/usr/bin/env python2
import bs4 as BeautifulSoup
import requests
import grequests
from datetime import datetime
from datetime import timedelta

def login(s, login, password):
    s.get('https://teleservices.paris.fr/srtm/jsp/web/index.jsp')
    data = {'login': login, 'password': password}
    s.post('https://teleservices.paris.fr/srtm/authentificationConnexion.action', data=data)

def getInfos(s):
    r = s.get('https://teleservices.paris.fr/srtm/compteConsulterDonneePersoInit.action')

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
    for i in range(1,8):
        data['dateDispo'] = '{:%d/%m/%Y}'.format(date)
        rs = []
        for heureDispo in range(8, 22):
            data['heureDispo'] = heureDispo
            r = s.post('https://teleservices.paris.fr/srtm/reservationCreneauListe.action', data=data)
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
                rs.append(grequests.post('https://teleservices.paris.fr/srtm/reservationCreneauListe.action', data=data, session=s))

        print(data['dateDispo'])
        print(grequests.map(rs))
        date = date + timedelta(days=1)


def main():
    s = requests.Session()
    login(s, '171091026', '5434')
    #getInfos(s)
    #getTennisList(s)
    crawl(s, True, False)

main()
