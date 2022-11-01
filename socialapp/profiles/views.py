from django.shortcuts import get_object_or_404, redirect, render
from .models import Profile, Relationship 
from .forms import ProfileModelForm
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required()
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileModelForm(request.POST,request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile details updated.')
            return redirect('/profiles/myprofile/')

    else:
        form = ProfileModelForm(instance=profile)
        
    context= {
        'profile' : profile,
        'form' : form,
    }
    return render(request, 'profiles/myprofile.html', context)

class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profilelist.html'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact = self.request.user.username)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []

        for rel in rel_r:
            rel_receiver.append(rel.receiver.user)

        for rel in rel_s:
            rel_sender.append(rel.sender.user)


        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context["is_empty"] = False

        if len(self.get_queryset()) == 0:
            context['is_empty'] = True 

        return context

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/profiledetail.html'

    def get_object(self, slug=None):
        slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=slug)
        print(profile)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact = self.request.user.username)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []

        for rel in rel_r:
            rel_receiver.append(rel.receiver.user)

        for rel in rel_s:
            rel_sender.append(rel.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_posts()
        context['len_posts'] = True if len(self.get_object().get_all_posts()) > 0 else False
        return context

@login_required()
def send_invitation(request):
    if request.method =='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        if sender.user != receiver.user:
            Relationship.objects.create(sender=sender, receiver=receiver, status='Send')
            return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile')

@login_required()
def accept_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'Send':
            rel.status = 'Accepted'
            rel.save()
    return redirect('profiles:my-invites')

@login_required()
def reject_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('profiles:my-invites')

@login_required()
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitations_received(profile)
    results = [s.sender for s in qs ]
    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'is_empty' : is_empty,
    }
    return render(request, 'profiles/myinvites.html', context)


@login_required()
def remove_from_friends(request):
    if request.method =='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
            )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile')

# def profiles_list_view(request):
#     user = request.user
#     qs = Profile.objects.get_all_profiles(user)
#     context = {
#         'qs': qs,
#     }
#     return render(request, 'profiles/profilelist.html', context)
