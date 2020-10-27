#!/usr/bin/python3

import requests
import regex as re
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
import xml.etree.ElementTree as ET
import mysql.connector
import logging
import base64
import urllib


# Input basic information below..
## Your router's address (format: http://ip_address or https://ip_address)
asusAddr = '' # eg. http://192.168.1.1
## Your Asus router's management web page login user and password
asusUser = ''
asusPasswd = ''
## Your MySQL infomation (IP address, user, password, database, table)
sqlIP = '' # MySQL IP address, eg. 127.0.0.1
sqlPort = '3306' # Default port is 3306
sqlUser = '' # MySQL Username
sqlPasswd = '' # MySQL Password
sqlDb = '' # MySQL Database you're gonna use
sqlTable = '' # MySQL Table you're gonna use
# Input basic information Above






# Script starts here
authURL = '{}/login.cgi'.format(asusAddr)
speedURL = '{}/update.cgi'.format(asusAddr)
tempURL = '{}/ajax_coretmp.asp'.format(asusAddr)
statusURL = '{}/cpu_ram_status.xml'.format(asusAddr)
bandwidthURL = '{}/Main_TrafficMonitor_monthly.asp'.format(asusAddr)

asusIP = re.search(r'((?<=https://)|(?<=http://))\d+\.\d+\.\d+\.\d+', asusAddr)[0]
asusAuth = base64.b64encode('{}:{}'.format(asusUser, asusPasswd).encode())
asusAuthEncode = urllib.parse.quote(asusAuth)

logging.basicConfig(filename='/var/log/asusMonitor.log', encoding='utf-8', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.WARNING)

sessions = requests.Session()

authPayload = 'group_id=&action_mode=&action_script=&action_wait=5&current_page=Main_Login.asp&next_page=index.asp&login_authorization={}'.format(asusAuthEncode)
authHeaders = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Content-Length': '154',
  'host': '{}'.format(asusIP),
  'referer': '{}/Main_Login.asp'.format(asusAddr)
}

dataPayload = "output=netdev&_http_id=TIDe855a6487043d70a"
dataHeaders = {
  'Cookie': '',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.3',
  'Content-Type': 'text/plain',
  'Referer': '{}/device-map/router_status.asp'.format(asusAddr)
}

bandwidthHeaders = {
    'Cookie': ''
}

mydb = mysql.connector.connect(
    host='{}'.format(sqlIP),
    port='{}'.format(sqlPort),
    user='{}'.format(sqlUser),
    passwd='{}'.format(sqlPasswd),
    database='{}'.format(sqlDb)
    )
mycursor = mydb.cursor()

def getAuth():
    global token
    # ignore tls warning
    requests.packages.urllib3.disable_warnings()
    
    sessions.post(authURL, headers=authHeaders, data = authPayload, verify=False)
    token = sessions.cookies.get_dict()['asus_token']
    # print(token)
    logging.info('New Token: {}'.format(token))
    return token
    
    
def getData(token):
    # ignore tls warning
    requests.packages.urllib3.disable_warnings()
    
    # cookie
    dataHeaders['Cookie'] = 'asus_token={}'.format(token)
    bandwidthHeaders['Cookie'] = 'asus_token={}'.format(token)
    
    # get speed and cpu ram status
    speedResponse1 = sessions.post(speedURL, headers=dataHeaders, data=dataPayload, verify=False)
    statusResponse1 = sessions.get(statusURL, headers=dataHeaders, verify=False)
    time1 = time.time()
    time.sleep(1)
    speedResponse2 = sessions.post(speedURL, headers=dataHeaders, data=dataPayload, verify=False)
    statusResponse2 = sessions.get(statusURL, headers=dataHeaders, verify=False)
    time2 = time.time()
    
    # get coretemp
    tempResponse = sessions.get(tempURL, headers=dataHeaders, verify=False)
    
    # get bandwidth
    bandwidthResponse = requests.get(bandwidthURL, headers=bandwidthHeaders, verify=False)

    # speed result
    speedResult1 = speedResponse1.text
    speedResult2 = speedResponse2.text
    
    # coretemp result
    tempResult = tempResponse.text
    
    # cpu ram status result
    statusResult1 = ET.fromstring(statusResponse1.text)
    statusResult2 = ET.fromstring(statusResponse2.text)
    
    # bandwidth result
    bandwidthResult = bandwidthResponse.text
    
    # speed data cleaning
    wiredRX1 = int(re.search(r'(?<=WIRED\':{rx:).*(?=\,tx)', speedResult1)[0], 0)
    wiredRX2 = int(re.search(r'(?<=WIRED\':{rx:).*(?=\,tx)', speedResult2)[0], 0)
    
    wiredTX1 = int(re.search(r'(?<=WIRED\':{rx:.*\,tx:).*(?=})', speedResult1)[0], 0)
    wiredTX2 = int(re.search(r'(?<=WIRED\':{rx:.*\,tx:).*(?=})', speedResult2)[0], 0)
    
    internetRX1 = int(re.search(r'(?<=INTERNET\':{rx:).*(?=\,tx)', speedResult1)[0], 0)
    internetRX2 = int(re.search(r'(?<=INTERNET\':{rx:).*(?=\,tx)', speedResult2)[0], 0)
    
    internetTX1 = int(re.search(r'(?<=INTERNET\':{rx:.*\,tx:).*(?=})', speedResult1)[0], 0)
    internetTX2 = int(re.search(r'(?<=INTERNET\':{rx:.*\,tx:).*(?=})', speedResult2)[0], 0)
    
    wireless2gRX1 = int(re.search(r'(?<=WIRELESS0\':{rx:).*(?=\,tx)', speedResult1)[0], 0)
    wireless2gRX2 = int(re.search(r'(?<=WIRELESS0\':{rx:).*(?=\,tx)', speedResult2)[0], 0)
    
    wireless2gTX1 = int(re.search(r'(?<=WIRELESS0\':{rx:.*\,tx:).*(?=})', speedResult1)[0], 0)
    wireless2gTX2 = int(re.search(r'(?<=WIRELESS0\':{rx:.*\,tx:).*(?=})', speedResult2)[0], 0)
    
    wireless5gRX1 = int(re.search(r'(?<=WIRELESS1\':{rx:).*(?=\,tx)', speedResult1)[0], 0)
    wireless5gRX2 = int(re.search(r'(?<=WIRELESS1\':{rx:).*(?=\,tx)', speedResult2)[0], 0)
    
    wireless5gTX1 = int(re.search(r'(?<=WIRELESS1\':{rx:.*\,tx:).*(?=})', speedResult1)[0], 0)
    wireless5gTX2 = int(re.search(r'(?<=WIRELESS1\':{rx:.*\,tx:).*(?=})', speedResult2)[0], 0)
    
    internetRXSpeed = round((internetRX2 - internetRX1)/1024/(time2 - time1), 2)
    internetTXSpeed = round((internetTX2 - internetTX1)/1024/(time2 - time1), 2)
    
    wiredRXSpeed = round((wiredRX2 - wiredRX1)/1024/(time2 - time1), 2)
    wiredTXSpeed = round((wiredTX2 - wiredTX1)/1024/(time2 - time1), 2)
    
    wireless2gRXSpeed = round((wireless2gRX2 - wireless2gRX1)/1024/(time2 - time1), 2)
    wireless2gTXSpeed = round((wireless2gTX2 - wireless2gTX1)/1024/(time2 - time1), 2)
    
    wireless5gRXSpeed = round((wireless5gRX2 - wireless5gRX1)/1024/(time2 - time1), 2)
    wireless5gTXSpeed = round((wireless5gTX2 - wireless5gTX1)/1024/(time2 - time1), 2)
    
    # coretemp data cleaning
    coretemp2g = int(re.search(r'(?<=curr_coreTmp_2_raw = ")\d+', tempResult)[0])
    coretemp5g = int(re.search(r'(?<=curr_coreTmp_5_raw = ")\d+', tempResult)[0])
    coretempCPU = int(re.search(r'(?<=curr_coreTmp_cpu = ")\d+', tempResult)[0])
    
    # cpu ram status data cleaning
    cpu1Total1 = int(statusResult1[0][0][0].text)
    cpu1Total2 = int(statusResult2[0][0][0].text)
    
    cpu1Usage1 = int(statusResult1[0][0][1].text)
    cpu1Usage2 = int(statusResult2[0][0][1].text)
    cpu1Percentage = round(100*(cpu1Usage2-cpu1Usage1)/(cpu1Total2-cpu1Total1), 2)
    
    cpu2Total1 = int(statusResult1[0][1][0].text)
    cpu2Total2 = int(statusResult2[0][1][0].text)
    
    cpu2Usage1 = int(statusResult1[0][1][1].text)
    cpu2Usage2 = int(statusResult2[0][1][1].text)
    cpu2Percentage = round(100*(cpu2Usage2-cpu2Usage1)/(cpu2Total2-cpu2Total1), 2)
    
    # ramTotal = int(int(statusResult1[1][0].text)/1024)
    ramUsage = int(int(statusResult1[1][2].text)/1024)
    
    # bandwidth data cleaning
    historyList = re.findall(r'(?<=monthly_history = \[\n).*(?=\]\;)', bandwidthResult)[0]
    hexList = re.findall(r'0x\w+|\d+', historyList)
    bandwidthRX = round(int(hexList[-2], 0)/1024/1024, 2)
    bandwidthTX = round(int(hexList[-1], 0)/1024/1024, 2)

    # SQL Insert
    sqlCommand = '''INSERT INTO {}(internetRXSpeed, 
                    internetTXSpeed, 
                    wiredRXSpeed, 
                    wiredTXSpeed, 
                    wireless2gRXSpeed, 
                    wireless2gTXSpeed, 
                    wireless5gRXSpeed, 
                    wireless5gTXSpeed, 
                    coretemp2g, 
                    coretemp5g, 
                    coretempCPU, 
                    cpu1Percentage, 
                    cpu2Percentage, 
                    ramUsage, 
                    bandwidthRX, 
                    bandwidthTX) 
                    VALUE ({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})'''\
                        .format(sqlTable, \
                                internetRXSpeed, \
                                internetTXSpeed, \
                                wiredRXSpeed, \
                                wiredTXSpeed, \
                                wireless2gRXSpeed, \
                                wireless2gTXSpeed, \
                                wireless5gRXSpeed, \
                                wireless5gTXSpeed, \
                                coretemp2g, \
                                coretemp5g, \
                                coretempCPU, \
                                cpu1Percentage, \
                                cpu2Percentage, \
                                ramUsage, \
                                bandwidthRX, \
                                bandwidthTX)
    mycursor.execute(sqlCommand)
    mydb.commit()
    
    # final data
    # print('+'*20)
    # print('Current Time: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
    # print('[Internet] RX: '+str(internetRXSpeed)+' kB/s')
    # print('[Internet] TX: '+str(internetTXSpeed)+' kB/s\n')
    # print('[Wired] RX: '+str(wiredRXSpeed)+' kB/s')
    # print('[Wired] TX: '+str(wiredTXSpeed)+' kB/s\n')
    # print('[2.4G] RX: '+str(wireless2gRXSpeed)+' kB/s')
    # print('[2.4G] TX: '+str(wireless2gTXSpeed)+' kB/s\n')
    # print('[5G] RX: '+str(wireless5gRXSpeed)+' kB/s')
    # print('[5G] TX: '+str(wireless5gTXSpeed)+' kB/s')
    # print('-'*20)
    # print('[2.4G Temp] '+str(coretemp2g)+' *C')
    # print('[5G Temp] '+str(coretemp5g)+' *C')
    # print('[CPU Temp] '+str(coretempCPU)+' *C')
    # print('-'*20)
    # print('[CPU1 Usage] '+str(cpu1Percentage)+' %')
    # print('[CPU2 Usage] '+str(cpu2Percentage)+' %')
    # print('[RAM Usage] {} MB'.format(str(ramUsage)))
    # print('\n')
    logging.debug('Get Data Done')
    return internetRXSpeed, internetTXSpeed, wiredRXSpeed, wiredTXSpeed, wireless2gRXSpeed, wireless2gTXSpeed, wireless5gRXSpeed, wireless5gTXSpeed, coretemp2g, coretemp5g, coretempCPU, cpu1Percentage, cpu2Percentage, ramUsage, bandwidthRX, bandwidthTX


def listener(event):
    if event.exception:
        logging.warning('Monitor interupted, restarting..')
        scheduler.remove_all_jobs()
        getAuth()
        scheduler.add_job(getAuth, 'interval', hours=6)
        scheduler.add_job(getData, 'interval', seconds=2, max_instances=5, args=[token])
        logging.warning('Monitor Restarted.')
        
        
if __name__ == '__main__':
    logging.warning('Monitor started.')
    scheduler= BlockingScheduler()
    getAuth()
    scheduler.add_job(getAuth, 'interval', hours=6)
    scheduler.add_job(getData, 'interval', seconds=2, max_instances=5, args=[token])
    scheduler.add_listener(listener, EVENT_JOB_ERROR)
    scheduler.start()
    try:
        while True:
            continue
    except (KeyboardInterrupt, SystemExit):
        logging.warning('Monitor forced stopped.')
        scheduler.shutdown(wait=False)
