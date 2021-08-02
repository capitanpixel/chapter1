from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from datetime import datetime
from .models import *
import json
import random


def index(request):
    return render(request, "books/index.html")


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "books/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "books/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "books/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "books/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "books/register.html")


def profile(request, user):
    profileuser = get_object_or_404(User, username=user)
    books = Book.objects.filter(user=profileuser)
    book_1 = books[:len(books)//2]
    book_2 = books[len(books)//2:]
    context = {
    "book1": book_1,
    "book2": book_2
    }
    return render(request, "books/profile.html", context)
    
    
@csrf_exempt
def addbook(request):
    if request.method == "POST":
        newbook = Book()
        newbook.title = request.POST["title"]
        newbook.author = request.POST["author"]
        newbook.year = request.POST["year"]
        newbook.province = request.POST["province"]
        newbook.img = request.POST["img"]
        newbook.description = request.POST["description"]
        newbook.chapter_1 = request.POST["chapter_1"]
        newbook.user = request.user
        newbook.save()
        return redirect('profile', user=request.user)
    return render(request, "books/addbook.html")


def inbox(request):
    return render(request, "books/inbox.html")


@csrf_exempt
def read(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        is_read = request.POST.get('is_read')
        try:
            post = Book.objects.get(id=post_id)
            if is_read == 'no':
                post.read.add(request.user)
                is_read = 'yes'
            elif is_read == 'yes':
                post.read.remove(request.user)
                is_read = 'no'
            post.save()

            return JsonResponse({'like_count': post.read.count(), 'is_read': is_read, "status": 201})
        except:
            return JsonResponse({'error': "Post not found", "status": 404})
    books = Book.objects.filter(read=request.user)
    book_1 = books[:len(books)//2]
    book_2 = books[len(books)//2:]
    context = {
    "book1": book_1,
    "book2": book_2
    }
    return render(request, "books/read.html", context)


def book(request, id):
    context = {
    "book": Book.objects.get(pk=id),
    "comments": Comment.objects.filter(book_id=id)
    }
    return render(request, "books/book.html", context)


def comment(request, id):
    if request.user.username:
        if request.method == "POST":
            now = datetime.now()
            date = now.strftime(" %d %B %Y %X ")
            c = Comment()
            c.username = request.user.username
            c.book_id = id
            c.time = date 
            c.comment = request.POST["comment"]
            c.save()
            return redirect('book',id=id)            
        else:
            return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))


@csrf_exempt
@login_required
def compose(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    emails = [email.strip() for email in data.get("recipients").split(",")]
    if emails == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)
    recipients = []
    for email in emails:
        try:
            user = User.objects.get(email=email)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with email {email} does not exist."
            }, status=400)
    body = data.get("body", "")

    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        email = Email(
            user=user,
            sender=request.user,
            body=body,
            read=user == request.user
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()
    return JsonResponse({"message": "Email sent successfully."}, status=201)


@login_required
def mailbox(request, mailbox):
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(
            user=request.user, sender=request.user
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)
    emails = emails.order_by("-timestamp").all()
    return JsonResponse([email.serialize() for email in emails], safe=False)


@csrf_exempt
@login_required
def email(request, email_id):
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(email.serialize())
    elif request.method == "PUT":
        data = json.loads(request.body)
        #if data.get("read") is not None:
        #    email.read = data["read"]
        #if data.get("archived") is not None:
        #    email.archived = data["archived"]
        email.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def allbooks(request):
    books = Book.objects.all()
    book_1 = books[:len(books)//2]
    book_2 = books[len(books)//2:]
    context = {
    "book1": book_1,
    "book2": book_2
    }
    return render(request, "books/allbooks.html", context)
