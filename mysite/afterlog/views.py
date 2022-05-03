from django.shortcuts import render, redirect
from django.template import loader
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Account, Message, Coupon, Mail

def transfer(sender, receiver, amount, message):
    	with transaction.atomic():
            acc1 = Account.objects.get(user=sender)
            acc2 = Account.objects.get(user=receiver)
            ## Possibly add improper check up on balance here
            Message.objects.create(source=sender, target=receiver, amount = amount, content= message)
            if amount > 0 and acc1.balance >= amount and acc1 != acc2:
                acc1.balance -= amount
                acc2.balance += amount

            acc1.save()
            acc2.save()


# Fault: the download view for the coupons does not check whether the accessing user is the same one that is logged in (hihupload)
@login_required
def downloadView(request, couponid):
    c = Coupon.objects.get(pk=couponid)

	#couponname = c.data.name.split('/')[-1]
    couponname = couponid
    response = HttpResponse(c.data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % couponname

    return response

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

@login_required
def homePageView(request):
    if request.method == 'POST':
        sender = request.user
        receiver = User.objects.get(username = request.POST.get('to'))
        amount = int(request.POST.get('amount'))
        message = request.POST.get('content')
        transfer(sender, receiver, amount, message)

    accounts = Account.objects.exclude(user_id=request.user.id)
    messages = Message.objects.filter(source = request.user.id)
    cs = Coupon.objects.filter(owner=request.user.id)
    coupons = [{'id': c.id, 'name': c.id} for c in cs]	
    context = {'accounts': accounts,'msgs': messages, 'coupons': coupons}
    return render(request, 'afterlog.html', context)


    # Fault 1: Improper use of GET and POST in transfer and html
    # Fault 2: Broken Access Control: does not check whether the owner is the logged user when downloading coupons
    # Fault 3: XSS, fix using sanitization

