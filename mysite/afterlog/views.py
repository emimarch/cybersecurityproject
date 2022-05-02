from django.shortcuts import render
from django.template import loader
from django.db import transaction
from django.contrib.auth.models import User
from .models import Account, Message

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

def homePageView(request):
    if request.method == 'POST':
        sender = request.user
        receiver = User.objects.get(username = request.POST.get('to'))
        amount = int(request.POST.get('amount'))
        message = request.POST.get('content')
        transfer(sender, receiver, amount, message)

    accounts = Account.objects.exclude(user_id=request.user.id)
    context = {'accounts': accounts}
    return render(request, 'afterlog.html', context)


    # Fault 1: Improper use of GET and POST in transfer and html
    # Fault 2: Lack of login required before functions ?

