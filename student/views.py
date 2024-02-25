from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
# Create your views here.

# @login_required
def checkout(request):

    if request.method !="POST":
        return HttpResponse("invalid method")

    data = json.loads(request.body)
    user_id = data.get("member_id", None)
    book_id = data.get("book_id", None)
    if not book_id or not user_id:
        return HttpResponse("invalid book", status = 200)
    else:
        try:
            book = Book.objects.get(id = book_id)
            if Circulation.objects.filter(member_id = user_id, book_id = book_id).count()%2==1: # same book already checkout by user
                return HttpResponse("book already checkout by you", status = 200)
            if book.copies_left >0: # book avaialble so simply checkout
                book.copies_left = book.copies_left - 1
                book.save()
                Circulation.objects.create(member_id = user_id, book_id = book_id, eventtype = "CHECK OUT")
                return HttpResponse("book succesfully checkout", status = 200)
            else: # book unavailable so reservation needed
                Reservation.objects.create(member_id = user_id, book_id = book_id, eventtype = "RESERVE")
                return HttpResponse("book succesfully reserved", status = 200)
        except:
            return HttpResponse("book not found", status = 200)


# @login_required
def return_book(request):

    if request.method !="POST":
        return HttpResponse("invalid method")
    
    data = json.loads(request.body)
    user_id = data.get("member_id", None)
    book_id = data.get("book_id", None)
    if not book_id or not user_id:
        return HttpResponse({"error" : "invalid book"}, status = 200)
    else:
        try:
            book = Book.objects.get(id = book_id)
            Circulation.objects.create(member_id = user_id, book_id = book_id, eventtype = "RETURN")

            book_reservation = Reservation.objects.filter(book_id = book_id).order_by("pk")

            if book_reservation.count() == 0: # no reservation for this book
                book.copies_left += 1
                book.save()
            
            else: # reservation exists for this book
                book_reservation = book_reservation[0]
                user_id = book_reservation.member_id
                Circulation.objects.create(member_id = user_id, book_id = book_id, eventtype = "FULFILL")
                # Circulation.objects.create(member_id = user_id, book_id = book_id, eventtype = "CHECK OUT")
                book_reservation.delete()
            
            return JsonResponse({"message" : "succesfully returned"}, status = 200)
        
        except:
            return JsonResponse({"error" : "book not found"}, status = 200)

@csrf_exempt
def loginview(request):

    if request.method != "POST":
        return HttpResponse("login falied", status = 400)
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    print(username, password)
    user = authenticate(username = username, password = password)
    if user is not None:
        login(request, user)
        return HttpResponse("login success", status = 200)
    else:
        return HttpResponse("login falied", status = 400)


# @login_required
def overdue_books(request):

    data = json.loads(request.body)
    member_id = data.get("member_id", None)
    circulation = Circulation.objects.filter(member_id = member_id).order_by("pk")
    fine_per_day = 50
    today = datetime.date(2024,3,5)
    days = datetime.timedelta(days = 7)
    dic = {}
    fine = 0
    for book in circulation:
        if book.eventtype in ("CHECK OUT", "FULFILL") and book.date < today - days:
            dic[book.book_id] = book.date
        else:
            dic.pop(book.book_id, None)
    for book in dic:
        fine = fine + fine_per_day*(today - days- dic[book]).days
    return JsonResponse({"fine" : fine, "overdue_books" : dic})

                



