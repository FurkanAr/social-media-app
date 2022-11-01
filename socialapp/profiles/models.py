from django.shortcuts import reverse
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Q
import random, string

GENDER_CHOICES = (
    ('Female', 'Female'),
    ('Male', 'Male'),
)

def slug_generator():
    return ''.join(random.choices(string.ascii_lowercase + string.digits + string.ascii_uppercase, k=5))

class ProfileManager(models.Manager):
    
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))

        accepted = set([])
        for rel in qs:
            if rel.status == 'Accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)

        available = [profile for profile in profiles if profile not in accepted]
        return available


    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name  = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=300, blank=True)
    email = models.EmailField()
    country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='avatars/')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("profiles:profile-detail", kwargs={"slug": self.slug})
    

    def save(self, *args, **kwargs):
        ex = False
        if self.first_name and self.last_name:
            to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
            ex = Profile.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(to_slug + " " +str(slug_generator()))
                ex = Profile.objects.filter(slug=to_slug).exists()
        else:
            to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)

    def get_friends(self):
        return self.friends.all()

    def get_friends_number(self):
        return self.friends.all().count()

    def get_all_posts(self):
        return self.posts.all()


STATUS_CHOICES = (
    ('Send', 'Send'),
    ('Accepted', 'Accepted')
)

class RelationshipManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='Send')
        return qs

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    objects = RelationshipManager()
    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"   