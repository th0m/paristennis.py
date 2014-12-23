#!/usr/bin/env python2
import bs4 as BeautifulSoup
import requests
import logging
import smtplib
import redis
import hashlib
import json
import time
import yaml
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from pymongo import MongoClient
from datetime import datetime, timedelta

def login(login, password):
    s.get('https://teleservices.paris.fr/srtm/jsp/web/index.jsp')
    data = {'login': login, 'password': password}
    s.post('https://teleservices.paris.fr/srtm/authentificationConnexion.action', data=data)

def get_req_checksum(post_data):
    return hashlib.md5(json.dumps(post_data, sort_keys=True)).hexdigest()

def get_resp_cache(url, post_data=False):
    if not post_data:
        reqchksum = hashlib.md5(url).hexdigest()
    else:
        reqchksum = get_req_checksum(post_data)
    resp = rdb.get(reqchksum)
    if not resp:
        if not post_data:
            resp = s.get(url).text
        else:
            resp = s.post(url, data=post_data).text
        rdb.setex(reqchksum, resp, 60)
    return resp

def crawl(alert):
    post_data = {
        'actionInterne': 'recherche',
        'provenanceCriteres': 'true',
    }

    if alert['allArrdt']:
        post_data['tousArrondissements'] = 'on'

    if alert['coveredCourt']:
        post_data['courtCouvert'] = 'on'

    date = datetime.now()
    results = []
    # If we already booked a tennis court getting the list will fail if we don't first do that request
    get_resp_cache('https://teleservices.paris.fr/srtm/reservationCreneauInit.action')
    url = 'https://teleservices.paris.fr/srtm/reservationCreneauListe.action'

    for i in range(1,8):
        post_data['dateDispo'] = '{:%d/%m/%Y}'.format(date)

        for heureDispo in range(alert['startHour'], alert['endHour']+1):
            post_data['heureDispo'] = heureDispo
            resp = get_resp_cache(url, post_data)
            soup = BeautifulSoup.BeautifulSoup(resp)
            pagelinks = soup.find(attrs={'class': 'pagelinks'})
            pages = 0 
            if pagelinks:
                links = pagelinks.findAll('a')
                if len(links) > 0:
                    pages = int(links[-1]['href'].split('d-41734-p=')[1].split('&')[0])
                else:
                    pages = 1
            for page in range(1, pages+1):
                post_data['d-41734-p'] = page
                resp = get_resp_cache(url, post_data)
                results.append(resp)
        date = date + timedelta(days=1)

    content = {}
    for page in results:
        soup = BeautifulSoup.BeautifulSoup(page)
        tbody = soup.tbody
        if tbody:
            for row in tbody.findAll('tr'):
                cells = row.findAll('td')
                date = cells[2].string
                hour = cells[3].string
                if not date in content:
                    content[date] = {}
                if not hour in content[date]:
                    content[date][hour] = []
                content[date][hour].append({
                    'tennis': cells[0].string,
                    'arrdt': cells[1].string,
                    'court': cells[4].string,
                    'info': cells[5].a['href'],
                    'book': cells[6].a['href']
                })

    return content

def send_mail(mail, alertName, content):
    env = Environment(loader=FileSystemLoader('/home/tennis/templates'))
    template = env.get_template('mail.html')
    output = template.render(content=content)
    msg = MIMEText(output, 'html', 'utf-8')
    me = sender
    msg['Subject'] = 'Alert for %s' % alertName
    msg['From'] = me
    msg['To'] = mail
    s = smtplib.SMTP('localhost')
    s.sendmail(me, mail, msg.as_string())
    s.quit()

def check_alerts():
    for user in db.users.find():
        mail = user['mail']
        for alert in db.alerts.find({'key': user['key']}):
            alertName = alert['alertName']
            content = crawl(alert)
            r_chksum = rdb.get(alert['_id'])
            chksum = hashlib.md5(json.dumps(content, sort_keys=True)).hexdigest() 
            if r_chksum != chksum:
                rdb.set(alert['_id'], chksum)
                send_mail(mail, alertName, content)

if __name__ == '__main__':
    db = MongoClient().tennis
    rdb = redis.Redis('localhost')
    s = requests.Session()
    conf = yaml.load(open('conf/config.yaml', 'r'))
    sender = conf['sender']
    login = conf['login']
    password = conf ['password']
    
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    while True:
        logging.info('check_alerts() started')
        login(login, password)
        check_alerts()
        logging.info('check_alerts() ended')
        time.sleep(60)
