from bs4 import *
from datetime import date
import requests, os, re, time, schedule

def schedule_download():
    print("Scheduling download")
    schedule.every().day.at("08:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    print("Downloading podcasts...")
    root_folder = "antena3"
    create_folder(root_folder)
    # Find episode date, check if already downloaded, download.
    download_bons_rapazes(root_folder)
    download_mq3(root_folder)
    print("Done...")
 
def create_folder(root_folder): 
    path_exists = os.path.exists(root_folder)
    if not path_exists:
        os.mkdir(root_folder)

def download_bons_rapazes(root_folder):
    # Sexta-feira, entre as 20h e as 22h.
    create_folder(root_folder + "/bons_rapazes")
    webpage = get_page("https://www.rtp.pt/play/p299/")
    episode_name = get_episode_name(webpage)
    target = get_target(root_folder, "/bons_rapazes/" + episode_name)
    path_exists = os.path.exists(target)
    if not path_exists:
        print("Downloading bons rapazes episode: " + episode_name)
        download_and_save_mp3(webpage, target)
    else:
        print("Episode already exists: " + target)

def download_mq3(root_folder):
    # Domingo, entre as 0h e as 2h.
    create_folder(root_folder + "/mq3")
    webpage = get_page("https://www.rtp.pt/play/p255/mq3")
    episode_name = get_episode_name(webpage)
    target = get_target(root_folder, "/mq3/" + episode_name)
    path_exists = os.path.exists(target)
    if not path_exists:
        print("Downloading mq3 episode: " + episode_name)
        webpage = download_and_save_mp3(webpage, target)
        download_mq3_first_hour(webpage, root_folder)
    else:
        print("Episode already exists: " + target)
        download_mq3_first_hour(webpage, root_folder)

def download_mq3_first_hour(webpage, root_folder):
    links = webpage.findAll('a', {'title': re.compile("dio 1ª Hora")})
    first_hour_url = "https://www.rtp.pt" + links[0].get('href')
    webpage = get_page(first_hour_url);
    episode_name = get_episode_name(webpage)
    target = get_target(root_folder, "/mq3/" + episode_name)
    path_exists = os.path.exists(target)
    if not path_exists:
        print("Downloading mq3 episode: " + episode_name)
        download_and_save_mp3(webpage, target)
    else:
        print("Episode already exists: " + target)

def get_episode_name(webpage):
    links = webpage.findAll('meta', {'itemprop': 'name'})
    return links[0].get('content').strip()

def get_target(root_folder, episode_name):
    target = root_folder + episode_name + ".mp3";
    return target

def download_and_save_mp3(webpage, target):    
    mp3_url = re.search("https.*mp3", str(webpage)).group()
    response = requests.get(mp3_url)
    print("Saved to: " + target)
    open(target, "wb").write(response.content)
    return webpage

def get_page(page_url):
    r = requests.get(page_url)
    page = BeautifulSoup(r.text, 'html.parser')
    return page

schedule_download()