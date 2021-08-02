from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Book(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=64)
	description = models.TextField()
	img = models.CharField(max_length=164)
	author = models.CharField(max_length=64)
	year = models.IntegerField()
	province = models.CharField(max_length=64, null=True)
	chapter_1 = models.TextField()
	read = models.ManyToManyField(User, blank=True, related_name="liked_user")

	def __str__(self):
		return f"{self.title} {self.author}"

class Comment(models.Model):
	username = models.CharField(max_length=64)
	book_id = models.IntegerField()
	comment = models.TextField()
	time = models.CharField(max_length=64)

class Email(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField("User", related_name="emails_received")
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.email,
            "recipients": [user.email for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            "read": self.read,
            "archived": self.archived
        }
