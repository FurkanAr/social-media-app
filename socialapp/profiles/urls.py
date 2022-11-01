from django.urls import path
from .views import(
 my_profile_view, 
 invites_received_view, 
 ProfileListView,
 ProfileDetailView,           
 send_invitation,
 remove_from_friends,
 accept_invitation,
 reject_invitation,
)
app_name = 'profiles'

urlpatterns = [
    path('', ProfileListView.as_view(), name='profiles-list'),
    path('myprofile/', my_profile_view, name='my-profile'),
    path('myinvites/', invites_received_view, name='my-invites'),
    path('sendinvite/', send_invitation, name='send-invite'),
    path('removefriend/', remove_from_friends, name='remove-friend'),
    path('<slug>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('myinvites/accept', accept_invitation, name='accept-invite'),
    path('myinvites/reject', reject_invitation, name='reject-invite'),


]