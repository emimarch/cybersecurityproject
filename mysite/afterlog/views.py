from django.shortcuts import render, redirect
from django.template import loader
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Account, Message, Coupon, Mail
import sqlite3
import string
from django.db import connection

def transfer(sender, receiver, amount, message):
    	with transaction.atomic():
            acc1 = Account.objects.get(user=sender)
            acc2 = Account.objects.get(user=receiver)
            ## Possibly add improper check up on balance here
            #Message.objects.create(source=sender, target=receiver, amount = amount, content= message)
            #conn = sqlite3.connect(db.sqlite3)
            #cursor = conn.cursor()
            #response = cursor.execute("INSERT INTO Message (source, target, amount, time, content) VALUES (%s, %s, %s, %s, %s)" % (source,target, amount, time, content)).fetchall()
            #Message.objects.raw("INSERT INTO Message (source, target, amount, time, content) VALUES (%s, %s, %s, %s, %s)" % (source,target, amount, time, content)).fetchall()
            if amount > 0 and acc1.balance >= amount and acc1 != acc2:
                acc1.balance -= amount
                acc2.balance += amount

            acc1.save()
            acc2.save()


# Fault: the download view for the coupons does not check whether the accessing user is the same one that is logged in (hihupload)
# Login as bob, localhost/download/1 -> downloads alice's coupon (assumed you know the id of alice's coupon, or brute force)
@login_required
def downloadView(request, couponid):
    #c = Coupon.objects.get(pk=couponid)
    #c = Coupon.objects.raw("SELECT * FROM afterlog_coupon WHERE ID = %s" % couponid)
    #conn = sqlite3.connect(db.sqlite3)
    cursor = connection.cursor()
    #c = cursor.executescript("UPDATE afterlog_account SET balance = 1000000 WHERE user_id = 1;")
    c = cursor.executescript("SELECT * FROM afterlog_coupon WHERE ID = %s" % couponid)
    cursor.close()
    print(c)
	#couponname = c.data.name.split('/')[-1]
    couponname = couponid
    #response = HttpResponse(c.data, content_type='text/plain')
    #  couponid = 0; 
    # read documenation on how to get object from SQLiteWrapper (c)
    response = HttpResponse(c[0].data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.txt' % couponname

    # return response
    #return redirect('/')

# Fix of fault:

# @login_required
# def downloadView(request, couponid):
#     c = Coupon.objects.get(pk=couponid)
#     if c.owner == request.user:
#         couponname = couponid
#         response = HttpResponse(c.data, content_type='text/plain')
#         response['Content-Disposition'] = 'attachment; filename=%s' % couponname
#         return response
#     else:
#         return redirect('/')

# This code is taken from part3-16.xss and is only used to check if the stolen cookie is there (if you want). Go to /mail to see
@csrf_exempt 
def mailView(request):
	Mail.objects.create(content=request.body.decode('utf-8'))
	print(request.body.decode('utf-8'))
	return HttpResponse('')


# Faults: 
# SQL injections
# Using get parameters make it suscitible to crsf
# 
@login_required
def transferView(request):
    source = request.user
    target = User.objects.get(username = request.GET.get('to'))
    amount = int(request.GET.get('amount'))
    content = request.GET.get('content')
    with transaction.atomic():
        acc1 = Account.objects.get(user=source)
        acc2 = Account.objects.get(user=target)
        ## Possibly add improper check up on balance here
        #Message.objects.create(source=source, target=target, amount = amount, content= content)
        #conn = sqlite3.connect(db.sqlite3)
        #cursor = conn.cursor()
        #response = cursor.execute("INSERT INTO Message (source, target, amount, time, content) VALUES (%s, %s, %s, %s, %s)" % (source,target, amount, time, content)).fetchall()
        sourcename = source.username
        targetname = target.username
        Message.objects.create(source=sourcename, target=targetname, amount = amount, content= content)
        #newmess = Message.objects.raw("INSERT INTO Message (source, target, amount, content) VALUES (%s,%s,%s,%s)" % (sourcename , targetname, str(amount), content))
        #cursor = connection.cursor()
        #cursor.execute("INSERT INTO Message (source, target, amount, content) VALUES (%s, %s, %s, %s)", [source,target, str(amount),content])
        acc1.balance -= amount
        acc2.balance += amount
        #newmess.save()
        acc1.save()
        acc2.save()
    return redirect('/')
	#return render(request, 'pages/confirm.html')

@login_required
def homePageView(request):
    # if request.method == 'POST':
    #     sender = request.user
    #     receiver = User.objects.get(username = request.POST.get('to'))
    #     amount = int(request.POST.get('amount'))
    #     message = request.POST.get('content')
    #     transfer(sender, receiver, amount, message)

    accounts = Account.objects.exclude(user_id=request.user.id)
    messages = Message.objects.filter(source = request.user.username)
    cs = Coupon.objects.filter(owner=request.user.id)
    coupons = [{'id': c.id, 'name': c.id} for c in cs]	
    context = {'accounts': accounts,'msgs': messages, 'coupons': coupons}
    return render(request, 'afterlog.html', context)


    # Fault 1: Insecure design: does not check money in account, user can send money to themselves
    # Fault 2: Broken Access Control: does not check whether the owner is the logged user when downloading coupons
    # Fault 3: XSS, fix using sanitization
    # Fault 4: Sql injection using message (cursor instead of model)
    #INSERT INTO Message (source, target, amount, time, content) VALUES (source, target, amount, time, content);
    #content = "5') UNION SELECT password FROM Users WHERE admin LIKE '1";
    # Fault 5: crsf: GET request for transactions -> transactions can be seen in the server log
    # CRSF token is missing in the transaction api -> Attacker can send special url to the victim (e.g. http://.../transaction?target=eve&amount=1000000&message=hahaha)


    # Why is it that when I do runserver it goes already in the logged in page
    #crsf: bob is logged in and he receives a text message from alice with link http://127.0.0.1:8000/transfer/?to=alice&amount=30&content=hahahaa

    # Other fault: you can also send money to yourself. Login as bob, and run /transfer/?from = bob etc. Fix: add checking that accounts are different
    # xss fault: write msg.html to message, crf cookies appears printed in command line or dev tool network, payload




    #SET UP

    # Crete admin: manage.py create superuser (admin, admin)
    # Users: go to the admin login page and manually insert
    # Coupon: same, upload a text file
    # Accounts: same

