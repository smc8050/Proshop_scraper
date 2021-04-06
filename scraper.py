import requests
import time
from datetime import datetime
import csv
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

def getproshopData():
    # Windows 10 with Google Chrome
    user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '\
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '\
    'Safari/537.36'

    headers = { 'User-Agent': user_agent_desktop}
    url = "https://www.proshop.de/RTX-30series-overview"
    resp = requests.get(url, headers=headers)  # Send request
    code = resp.status_code  # HTTP response code
    if code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")  # Parsing the HTML
        last_updated = soup.find_all('p',{ "class" : "f-700"})[2].contents[0] # extract last updated from HTML
        last_date = last_updated[10:-9] #extract only date
        last_time = last_updated[-5:]  #extract only time
        last_date_dt = datetime.strptime(last_date, '%d.%m.%Y')
        last_time_dt = datetime.strptime(last_time, '%H.%M')
        last_updated_dt = datetime.combine(last_date_dt.date(), last_time_dt.time())
        outstanding = soup.find_all('table',{ "class" : "table"})[3].find_all('td')[3].contents[0].replace('\n','') # extract outstanding data from HTML
        incoming = soup.find_all('table',{ "class" : "table"})[3].find_all('td')[5].contents[0].replace('\n','') # extract ingoming data from HTML
    else:
        print('error reaching the website!')

    return last_updated_dt,outstanding,incoming

def log_data(csv_file,last_updated, outstanding, incoming):
    with open (csv_file,'a') as csvfile:
        writer = csv.writer(csvfile)
        now = time.strftime('%d-%m-%Y')
        writer.writerow([now, last_updated, outstanding, incoming])
    return csv_file

def plot_data(csv_file):

    data = pd.read_csv(csv_file, names=['timestamp', 'last_updated', "outstanding", "incoming"], header=1)
    timestamp_array = data['timestamp'].to_numpy()
    timestamp_array_dt = [datetime.strptime(date, '%d-%m-%Y').date() for date in timestamp_array]
    last_updated_array = data['last_updated'].to_numpy()
    last_updated_array_dt = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() for date in last_updated_array]
    outstanding_array = data['outstanding'].to_numpy()
    incoming_array = data['incoming'].to_numpy()

    fig, ax1 = plt.subplots()
    plt.title("Proshop RTX3080 TUF Stock")
    plt.xlabel("Date")
    plt.gcf().subplots_adjust(bottom=0.2) #to prevent x-label from beeing cut on export

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Incoming')
    ax1.plot(timestamp_array_dt, incoming_array, label="Incoming", color='red', drawstyle="steps-post")
    ax1.tick_params(axis='y', labelcolor='red')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation = 45)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Outstanding')  # we already handled the x-label with ax1
    ax2.plot(timestamp_array_dt, outstanding_array, label="Outstanding", color='blue', drawstyle="steps-post")
    ax2.tick_params(axis='y', labelcolor= 'blue')
    ax2.set_ylim([0,920])

    #Plot Site Updates
    #lineheight = 900
    #plt.vlines(last_updated_array_dt, 0, lineheight, colors='k', linestyles='solid', label='', data=None)
    #for i, x in enumerate(last_updated_array_dt):
    #    plt.text(x, lineheight/2, "Site update", rotation=90, verticalalignment='center')

    plt.savefig("Proshop_RTX3080_Stock.png",dpi=300)



def main():
    last_updated, outstanding, incoming = getproshopData()
    file = log_data("proshop_data.csv", last_updated, outstanding, incoming)
    file = "proshop_data.csv"
    plot_data(file)
    #print(last_updated)
    #print("Outstanding RTX 3080 TUF: " + outstanding)
    #print("Incoming RTX 3080 TUF: " + incoming)


if __name__ == "__main__":
    main()