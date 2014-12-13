#!/usr/bin/env python2
import bs4 as BeautifulSoup
import requests
import grequests
import smtplib
from email.mime.text import MIMEText
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
    url = 'https://teleservices.paris.fr/srtm/reservationCreneauListe.action'

    for i in range(1,8):
        data['dateDispo'] = '{:%d/%m/%Y}'.format(date)
        print(data['dateDispo'])
        reqs = []

        for heureDispo in range(alert['startHour'], alert['endHour']+1):
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
            for page in range(1, pages+1):
                data['d-41734-p'] = page
                reqs.append(grequests.post(url, data=data, session=s))

        results.extend(grequests.map(reqs))
        date = date + timedelta(days=1)

    content = {}
    for page in results:
        soup = BeautifulSoup.BeautifulSoup(page.content)
        tbody = soup.tbody
        if tbody:
            for row in tbody.findAll('tr'):
                cells = row.findAll('td')
                date = cells[2].string
                hour = cells[3].string
                content[date] = {}
                content[date][hour] = []
                content[date][hour].append({
                    'tennis': cells[0].string,
                    'arrdt': cells[1].string,
                    'court': cells[4].string,
                    'info': cells[5].a['href'],
                    'book': cells[6].a['href']
                })

    return content

def sendMail(mail, content):
    return

def checkAlerts():
    for user in db.users.find():
        mail = user['mail']
        for alert in db.alerts.find({'key': user['key']}):
            name = alert['alertName']
            content = crawl(alert)
            sendMail(mail, content)

if __name__ == '__main__':
    db = MongoClient().tennis
    s = requests.Session()
    login('171091026', '5434')
    #login(s, '020689053', '7498')
    #getInfos(s)
    #getTennisList(s)
    #results = crawl(s, True, False)
    checkAlerts()
