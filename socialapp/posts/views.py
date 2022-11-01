from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Like
from profiles.models import Profile
from django.views import View
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin


class PostCreateView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        profile = Profile.objects.get(user=request.user)
        post_form = PostForm()
        comment_form  = CommentForm()
        context = {
            'posts': posts,
            'profile' : profile,
            'post_form': post_form,
            'comment_form': comment_form,
        }
        return render(request, 'posts/main.html', context)

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(user = request.user)
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = profile
            instance.save()
            post_form = PostForm()
            messages.success(request, "Post added..")
            return redirect('posts:main-posts')
        
        return self.get(request)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/deletepost.html'
    success_url = reverse_lazy('posts:main-posts')
    
    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        
        if not obj.author.user == self.request.user:
            messages.error(self.request, 'You are not the author of the post.')
        return obj

class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'posts/updatepost.html'
    success_url = reverse_lazy('posts:main-posts')

    def form_valid(self,form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, 'You are not the author of the post.')
            return super().form_invalid(form)


class CommentCreateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(user = request.user)
        comment_form  = CommentForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            comment_form = CommentForm()
            return redirect('posts:main-posts')
        else:
            comment_form = CommentForm()
        return self.get(request)

class LikeDislikeView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=request.user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
            like=Like.objects.get(user=profile, post=post_obj)
            like.delete()

        else:
            post_obj.liked.add(profile)
            Like.objects.create(user=profile, post=post_obj, value='Like')

        return redirect('posts:main-posts')




        