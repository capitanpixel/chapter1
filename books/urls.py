from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
	path("", views.index, name="index"),
	path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addbook", views.addbook, name="addbook"),
    path("profile/<str:user>/", views.profile, name="profile"),
    path("inbox", views.inbox, name="inbox"),
    path("read/", views.read, name="read"),
    path("books/<int:id>", views.book, name="book"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("emails", views.compose, name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
    path("allbooks", views.allbooks, name="allbooks"),
]