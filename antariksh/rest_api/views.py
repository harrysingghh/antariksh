from cryptography.fernet import Fernet
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_api.config import globalvariable
from youtubesearchpython import Search
from pytube import YouTube
from rest_api.tasks import send_song,tele_api,log_message,getTextData,getUserData,sendCSV
import sys
import json
import requests
import os
import datetime
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import traceback
import time

def get_url():
    return globalvariable.hfuosk4g+':'+ globalvariable.hdygr9586

def log_file():

    current_date = datetime.datetime.today().strftime('%d_%m_%Y')
    current = datetime.datetime.today().strftime('20_20_23_%d_%m_%Y')
    file = '/tmp/'+'file_processing'+current_date+'.log'

    if not os.path.exists(file):
        os.mknod(file)
        with open(file,'a') as logging :
            logging.write("'timestamp','username','user_id','uniq_id','text','status',song\n")
            eta = datetime.datetime.strptime(current, '%S_%M_%H_%d_%m_%Y')
            sendCSV.apply_async(('sendDocument',get_url(),globalvariable.nbjdkgghjkf,file,),eta = eta)

def custom_500(request):

    if request.body:
        req = json.loads(request.body)
        class_type,error,obj= sys.exc_info()
        trace_back = traceback.extract_tb(obj)
        stack_trace = list()
        for trace in trace_back:
            if str(trace[0]).endswith(('views.py','task.py')):
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))


        data,kwags = {},{}
        data['chat_id'] = globalvariable.nbjdkgghjkf
#new add
        text = getTextData(req)
        uData = getUserData(req)
        data['text'] = ''
        if uData:
            if uData.get('first_name'):log_data['text'] += f"Name : {uData['first_name']}"
            if uData.get('user_name'):log_data['text'] += f"<a href='tg://user?id={uData['id']}'>({uData['user_name']})</a>"
        if text: data['text'] += f"\nText : {text}\n"
        data['text'] += f"Error : {error}\n\n"+str(class_type)+" : "+str(stack_trace)

        if req.get('message'):
            kwags['chat_id'] = req['message']['chat']['id']
        elif req.get('callback_query'):
            kwags['chat_id'] = req['callback_query']['message']['chat']['id']
        kwags['text'] = 'there is some technical issue,\nPlease try after some time later'

        tele_api('sendMessage', **kwags,url=get_url())
        tele_api('sendMessage', **data,url=get_url())
        return JsonResponse({})
    return JsonResponse({'status': 403, 'msg':'bad request'})

def update_token():

    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    client_id = globalvariable.zscfdok
    client_secret = globalvariable.nbhdj45ds
    encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
    token_headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_data = {
        "grant_type": "client_credentials",
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
    resp = json.loads(response._content)

    globalvariable.token = resp.get('access_token')

    if response.status_code == 200 :return True
    else: return False



def track_list(track_search,page=None):
    token = globalvariable.token
    link = 'https://api.spotify.com/v1/search'
    data = {
                'q':track_search,
                'type':'track',
                'offset' : 0 if not page else page*7,
                'limit':7,
                'market':'IN'
            }
    header = {
                'Accept':'application/json',
                'Content-Type':'application/json',
                'Authorization':'Bearer '+token
            }
    ser_headers = {
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/json"
                }
    response = requests.get(link, params = data,headers = ser_headers)
    resp = json.loads(response._content)
    if response.status_code == 200 :
        return resp
    else:
        return resp

def inline_list(track_search,page=None):
    i=0
    resp, inline_data,track_raw,navigation = [],[],[],None
    resp = track_list(track_search,page)

    if resp.get('error') and resp['error']['status'] in [401,400]:
        update_token()
        resp = track_list(track_search,page)

    if resp.get('tracks') and resp['tracks'].get('items'):
        for track  in resp['tracks']['items']:
            if '(' in track['name']:
                track['name'] = track['name'].split('(')[0]
            track_title = track['name']+ ' - ' +track['artists'][0]['name']

            for artist in range(1,len(track['artists'])):
                track_title += " | "+track['artists'][artist]['name']
                if len(track_title)>35:break

            if track_title.lower().replace(" ","") not in track_raw:
                img_url = ''
                song_dur = int(track['duration_ms'])//1000
                if track.get('album') and track['album'].get('images'):
                    len_img = len(track['album']['images'])
                    selective_img = len_img-2 if  len_img >2 else 1
                    img_url = track['album']['images'][selective_img]['url']
                    img_url = img_url.split('/')[-1]

                inline_data.append([{'text':track_title,'callback_data':'sng_'+str(i)+'_'+img_url+'_'+str(song_dur)}])
                track_raw.append(track_title.lower().replace(" ",""))
                i+=1

    # pagination Block
    if page and page !=1 :
        navigation = [{'text':'⬅️ Prev','callback_data':'page_'+str(page-1)+'_'+track_search}]
        if page<8 and resp['tracks'].get('total') > page*7:
            navigation.append({'text':'Next ➡️','callback_data':'page_'+str(page+1)+'_'+track_search})
    elif (not page or page ==1 ) and  resp.get('tracks') and  resp['tracks'].get('total') >0  :
        if resp['tracks'].get('total') > 7:navigation = [{'text':'➡️','callback_data':'page_2_'+track_search}]

    if navigation : inline_data.append(navigation)
    return inline_data


@csrf_exempt
def mgb_cycle(request):
    if not get_url():
        return JsonResponse({'status': 200, 'msg':'Variable not set yet'})

    if request.body:
        data = json.loads(request.body)

        if data.get('message') and data['message'].get('entities') and data['message'].get('text') != '/start':
            pass

        elif data.get('message'):
            inline = []
            chat_id = data['message']['chat']['id']
            inline = inline_list(data['message']['text'])
            d = {}
            if inline:
                d = {'chat_id': chat_id,'text':'select your song','reply_markup':{'inline_keyboard' : inline}}
            else:
                d = {'chat_id': chat_id,'text':'did not found anything'}

            if data['message']['text'] == '/start': d = {'chat_id': chat_id,'text':"Hi,\nI can help you to download any music.\nJust give me any song name and I'll give you the song"}

            tele_api('sendMessage', **d,url=get_url())

            #new add
            log_message.delay(data,globalvariable.nbjdkgghjkf,"New Req",url=get_url())

        elif data.get('callback_query'):
            chat_id = data['callback_query']['message']['chat']['id']
            message_id = data['callback_query']['message']['message_id']
            callback_raw = data['callback_query']['data'].split('_')

            if data['callback_query']['data'].startswith('page'):
                inline = inline_list(callback_raw[-1],int(callback_raw[1]))

                if inline:
                    d = {'chat_id': chat_id,'text':'select your song','reply_markup':{'inline_keyboard' : inline}}
                else:
                    d = {'chat_id': chat_id,'text':'Result not found'}

                tele_api('deleteMessage',chat_id=chat_id,message_id=message_id,url=get_url())
                tele_api('sendMessage',**d,url=get_url())


            elif data['callback_query']['data'].startswith('sng'):
                print("hello")
                song_raw = data['callback_query']['message']['reply_markup']['inline_keyboard'][int(callback_raw[1])][0]
                song_title = song_raw['text']
                song_img = callback_raw[2]
                song_dura = callback_raw[3]
                tele_api('deleteMessage',chat_id=chat_id,message_id=message_id,url=get_url())
                resp = tele_api('sendMessage',chat_id=chat_id,text='Wait for a while,\nWe are sending your music',url=get_url()).json()
                send_song.delay(data,resp['result']['chat']['id'],globalvariable.nbjdkgghjkf,   resp['result']['message_id'],song_title,song_img,song_dura,url=get_url())
            else:
                return JsonResponse({})
        return JsonResponse({})
    else:
        return JsonResponse({'status': 403, 'msg':'bad request'})

def data_oper(request):

    if request.method == "GET":
        data = request.GET
        for k,v in data.items():
            if hasattr(globalvariable, k):
                setattr(globalvariable, k, v)


        if 'shutll' in data:
            setattr(globalvariable, 'shutll', data.get('shutll').encode('ascii') )
        if 'chat_id' in data:
            setattr(globalvariable, 'chat_id', int(data.get('chat_id')) )

        return JsonResponse({'status': 200, 'msg':'operation completed succesfully'})
    else:
        return JsonResponse({'status': 403, 'msg':'bad request'})
