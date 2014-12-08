#!/usr/bin/env python
import bs4 as BeautifulSoup
import requests

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

    data['dateDispo'] = '09/12/2014'
    for heureDispo in range(8, 22):
        data['heureDispo'] = heureDispo
        r = s.post('https://teleservices.paris.fr/srtm/reservationCreneauListe.action', data=data)
        soup = BeautifulSoup.BeautifulSoup(r.text)
        pagelinks = soup.find(attrs={'class': 'pagelinks'}).findAll('a')
        if len(pagelinks) > 0:
            print(data['dateDispo']+' at '+str(heureDispo)+' '+pagelinks[-1]['href'].split('d-41734-p=')[1].split('&')[0])
        else:
            print(data['dateDispo']+' at '+str(heureDispo)+' 1')

def main():
    s = requests.Session()
    login(s, '171091026', '5434')
    #getInfos(s)
    #getTennisList(s)
    crawl(s, True, False)

main()
