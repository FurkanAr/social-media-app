from django.urls import path
from .views import PostCreateView, LikeDislikeView, CommentCreateView, PostDeleteView, PostUpdateView

app_name = 'posts'

urlpatterns = [
    path('', PostCreateView.as_view(), name='main-posts'),
    path('<pk>/delete/', PostDeleteView.as_view(), name="delete-post"),
    path('<pk>/update/', PostUpdateView.as_view(), name="update-post"),
    path('comment/', CommentCreateView.as_view(), name='comment-post'),   
    path('liked/', LikeDislikeView.as_view(), name="like-dislike-post"),




]