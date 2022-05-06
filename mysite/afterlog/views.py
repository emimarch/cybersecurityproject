from django.shortcuts import render, redirect
from django.template import loader
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Account, Message, Coupon, Mail
import sqlite3
import string
import zipfile
from io import StringIO
from django.db import connection



# F1: Broken Access Control: the download view for the coupon does not check whether the accessing user is the same of as the logged user
# Replicate F1: Login as bob, navigate to download/1 -> You are able to download Alice's coupon 
# (assuming you added a text file in Coupon account using the admin django website under Alice's name). This also assumes that bob knows alice's coupon id (1) (e.g. could have gotten it by brute force) 
@login_required
def downloadView(request, couponid):
    c = Coupon.objects.get(pk=couponid)
    couponname = couponid
    response = HttpResponse(c.data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.txt' % couponname

    return response

# F1 fix: Broken Access Control:
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


# Fault 2: Insecure design. The transactionView does not check whether there are enough money for the trasaction in the source account 
# Replicate F2: Log in as bob and send money to alice that is greater than bob's balance. The transaction should be allowed and bob's balance should now be negative

# Fault 4: XSS
# Replicate F4: log in a bob, and insert the message present in msg.html into the message box. Send the message to alice, you should see the crfs cookie appear
# printed in the command line (or navigate do dev tools -> network -> payload)

# Fault 5: crfs
# Replicate F5: bob is logged in in his account and receives a link from alice, for instance in the form of a fake image on which he clicks on like shown in file csrf.html. 
# The link is the following: http://127.0.0.1:8000/transfer/?to=alice&amount=30&content=hahahaa 
# (you can try and insert that when you are logged in as bob). This immediately transfers the money to alice, because no crfs token is asked. 

# Fix F5: crfs
# Uncomment crfs line in afterlog.html at line 68 and uncommed crfs required line at line 67 before transferView. Now you can try to insert the url http://127.0.0.1:8000/transfer/?to=alice&amount=30&content=hahahaa
# when you are logged in as bob and you will see nothing happens because you did not input the crfs token in the url (which is now required)


#@requires_csrf_token
@login_required
def transferView(request):
    s = request.user
    t = User.objects.get(username = request.GET.get('to'))
    amount = int(request.GET.get('amount'))
    content = request.GET.get('content')
    with transaction.atomic():
        acc1 = Account.objects.get(user=s)
        acc2 = Account.objects.get(user=t)
        
        sourcename = s.username
        targetname = t.username
        Message.objects.create(source=sourcename, target=targetname, amount = str(amount), content= content)

        acc1.balance -= amount
        acc2.balance += amount
        acc1.save()
        acc2.save()
    return redirect('/')

# Fix F2: Insercure design
# @login_required
# def transferView(request):
#     s = request.user
#     t = User.objects.get(username = request.GET.get('to'))
#     amount = int(request.GET.get('amount'))
#     content = request.GET.get('content')
#     with transaction.atomic():
#         acc1 = Account.objects.get(user=s)
#         acc2 = Account.objects.get(user=t)
#         if acc1.balance > amount:
#             sourcename = s.username
#             targetname = t.username
#             Message.objects.create(source=sourcename, target=targetname, amount = str(amount), content= content)

#             acc1.balance -= amount
#             acc2.balance += amount
#             acc1.save()
#             acc2.save()
#     return redirect('/')


# Fix F4: XSS
# Sanitize the message of all < > so that the javascript cannot be executed, or even better use some safe library that sanitizes the text for you, 
# for example urllib.parse.quote() function




def convertTuple(t):
    s = ''
    for item in t:
        s = s + " " + str(item)
    return s


# Fault 3: SQL injection, the user can insert a query that returns passowords 
# Replicate F3: login as bob, and go to aggregate/?from=0' UNION SELECT password FROM auth_user WHERE username LIKE 'admin
# You should be redirected to a new page where the admin passowrd shouls up
# Note that the malicious query is the following: ?from=0' UNION SELECT password FROM auth_user WHERE username LIKE 'admin
def aggregateView(request):
    sname = request.user.username
    tname = request.GET.get('from')
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    c = cursor.execute("SELECT amount from afterlog_message WHERE source = '%s' and target = '%s'" % (sname, tname)).fetchall()
    print(c)
    response = HttpResponse()
    for r in c: 
        r = convertTuple(r)
        response.write("<p>" + r + ".<p>")
    return response

# Fix F3: SQL injection
# This removes the ambigous c.execute() function that allows UNION script, and uses the default django models.get()
# def aggregateView(request):
#     sname = request.user.username
#     tname = request.GET.get('from')
#     messages = Message.objects.filter(source = sname, target = tname)
#     response = HttpResponse()
#     for message in messages: 
#         #print(message.content)
#         response.write("<p>" + message.content + ".<p>")
#     return response





@login_required
def homePageView(request):
    accounts = Account.objects.exclude(user_id=request.user.id)
    messages = Message.objects.filter(source = request.user.username)
    cs = Coupon.objects.filter(owner=request.user.id)
    coupons = [{'id': c.id, 'name': c.id} for c in cs]	
    context = {'accounts': accounts,'msgs': messages, 'coupons': coupons}
    return render(request, 'afterlog.html', context)




    #SET UP

    # Crete admin: manage.py create superuser (name: admin, password: admin)
    # Users: go to the admin login page (admin/login/?next=/admin/) and manually insert: 
    # 1) Users: 
    # - username: bob, password: squarepants
    # - username: alice, password: redqueen
    # 2) Accounts: 
    # - user: bob, balance: 50
    # - user: alice, balance: 300
    # 3) Coupon: 
    # - owner: alice
    # - data: insert file "coupon.txt" in repository (or create your own text file to upload)

    # Now exit the server, go to mysite directory and run: 
    # 1) python3 manage.py makemigrations
    # 2) python3 manage.py migrate
    # You can restart the server and proceed with testing the faults. 
