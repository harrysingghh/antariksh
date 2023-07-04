from celery import shared_task
import requests
from youtubesearchpython import Search
from pytube import YouTube
import os
from .config import globalvariable
import datetime
import json
import yt_dlp as youtube_dl
import youtube_dl



def getUserData(data):

    resp = {}
    if data and data.get('message') and data['message'].get('from'):
        if data['message']['from'].get('first_name'): resp['first_name'] = data['message']['from']['first_name']
        if data['message']['from'].get('username'):   resp['user_name'] = data['message']['from']['username']
        if data['message']['from'].get('id'): resp['id'] = data['message']['from']['id']

    elif data and data.get('callback_query') and data['callback_query'].get('from'):
        if data['callback_query']['from'].get('first_name'): resp['first_name'] = data['callback_query']['from']['first_name']
        if data['callback_query']['from'].get('username'): resp['user_name'] =  data['callback_query']['from']['username']
        if data['callback_query']['from'].get('id'): resp['id'] = data['callback_query']['from']['id']
    return resp if resp else None

def getTextData(data):

    chat_text = data['message']['text'] if data and data.get('message') and data['message'].get('text') else ''
    if data.get('callback_query') and data['callback_query'].get('message') and data['callback_query']['message'].get('reply_markup') and data['callback_query']['message']['reply_markup'].get('inline_keyboard'):
        song_raw = data['callback_query']['message']['reply_markup']['inline_keyboard'][-1][0]
        chat_text = song_raw['callback_data'].split('_')[-1]
    return chat_text if chat_text else None

@shared_task
def log_message(data,chat_id,status=None,url=None,song=None):
    text = getTextData(data)
    uData = getUserData(data)
    log_data= {}

    current_date = datetime.datetime.today().strftime('%d_%m_%Y')
    current_eod = datetime.datetime.today().strftime('20_20_23_%d_%m_%Y')
    current = datetime.datetime.today().strftime('%S_%M_%H_%d_%m_%Y')
    file = '/tmp/'+'file_processing'+current_date+'.log'
    log_data['text'] = ''


    if uData:
        if uData.get('first_name'):
            log_data['text'] += f"Name : {uData['first_name']}"
        if uData.get('user_name'):
            log_data['text'] += f"<a href='tg://user?id={uData['id']}'>({uData['user_name']})</a>\n"

    if text:
        log_data['text'] += f"Text : {text}\n"
    if status:
        log_data['text'] += f"Song: {song or ''}\n"
    if status:
        log_data['text'] += f"Status : {status}\n"


    log_data['chat_id'] =  chat_id

    tele_api('sendMessage', **log_data,url=url)
    if  os.path.exists(file):

        with open(file,'a') as logging :
            logging.write(f"{current},{uData.get('first_name','')},{uData.get('user_name','')},{uData.get('id','')},{text or ''},{status or ''},{song or ''}\n")
    else:
        os.mknod(file)
        with open(file,'a') as logging :
            logging.write("'timestamp','username','user_id','uniq_id','text','status',song\n")
            logging.write(f"{current},{uData.get('first_name','')},{uData.get('user_name','')},{uData.get('id','')},{text or ''},{status or ''},{song or ''}\n")
        eta = datetime.datetime.strptime(current_eod, '%S_%M_%H_%d_%m_%Y')
        sendCSV.apply_async(('sendDocument',globalvariable.hfuosk4g+':'+ globalvariable.hdygr9586,globalvariable.nbjdkgghjkf,file,),eta = eta)

def tele_api(type,url=None,**kwags):
    if url:
        url = 'https://api.telegram.org/bot'+url+type
        kwags['parse_mode'] = "HTML"
        x = requests.post(url, json = kwags)
        return x
    else:raise Exception("telegram api not found")



@shared_task
def sendCSV(type,url,chat_id,file):

    if os.path.exists(file):
        url = 'https://api.telegram.org/bot'+url+type
        payload = {
            'chat_id': chat_id,
        }
        files = {
            "document": open(file, 'rb'),
        }
        resp = requests.post(url,data=payload,files=files)
        os.remove(file)


def yt_download(video_url,filename):
    video_info = youtube_dl.YoutubeDL().extract_info(url = video_url,download=False)
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filename,
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    print("Download complete... {}".format(filename))

def pytub_download(link,song_title):
    yt= YouTube(link)
    try:
        stream = yt.streams.filter(only_audio=True)
        itag = None
        abr = 0
        for i in stream:
            if int(i.abr.replace('kbps', ''))>abr:
                itag = i.itag
                abr = int(i.abr.replace('kbps', ''))
        stream = yt.streams.get_by_itag(itag)
        stream.download(output_path='/tmp',filename=song_title+'.mp3')
    except Exception as e:
        tele_api('deleteMessage',chat_id=chat_id,message_id=msg_id,url=url)
        song = song_title.split('-')
        log_message.delay(data,global_chat,f"Error : {e}",song=song[0],url=url)


@shared_task
def send_song(data,chat_id,global_chat,msg_id,song_title,song_img,song_dura,url=None):

    allSearch = Search(song_title.replace('| ',''))
    link,name,audio=(None,)*3
    link =  allSearch.result()['result'][0]['link']
    title =  allSearch.result()['result'][0]['title']

    try:
        yt_download(link,'/tmp/'+song_title+'.mp3')
    except Exception as e:
        tele_api('deleteMessage',chat_id=chat_id,message_id=msg_id,url=url)
        song = song_title.split('-')
        log_message.delay(data,global_chat,f"Error : {e}",song=song[0],url=url)

    if os.path.exists('/tmp/'+song_title+'.mp3'):
        audio = open('/tmp/'+song_title+'.mp3','rb')

    if audio:
        tele_api('deleteMessage',chat_id=chat_id,message_id=msg_id,url=url)
        song = song_title.split('-')
        payload = {
            'chat_id': chat_id,
            'title': song[0],
            'performer' : song[1],
            'duration' :song_dura,
            'parse_mode': 'HTML'
        }
        files = {
            'audio': audio.read(),
        }
        resp = requests.post(
            "https://api.telegram.org/bot5971061598:AAG1z4WkdXjvSeq2GFxzqZqDuzbC72Az4Cc/sendAudio",
            data=payload,
            files=files)
        audio.close()
        os.remove('/tmp/'+song_title+'.mp3')

        if resp.ok != True:
            tele_api('sendMessage',chat_id=chat_id,text=resp.reason,url=url)
            log_message.delay(data,global_chat,"Error",song=song[0],url=url)
        else:
            log_message.delay(data,global_chat,f"Sent",song=song[0],url=url)

    else:
        log_message.delay(data,global_chat,f"Error : Audio not found\nSong : {song[0]}",url=url)
        tele_api('sendMessage',chat_id=chat_id,text="There is some technical issue, Please try after some later",url=url)

