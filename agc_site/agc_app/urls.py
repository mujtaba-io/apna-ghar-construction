
from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static

#--- COMMENT: so this is where we map URLs to functions declared in /views.py
#--- BUT, remember that we need to register this url file in agc_site/urls.py file,
#--- because that file is a real file where we need to declare all urls.
#--- Django will first look at that file for URLs and from there it will
#--- be referred to this file for URLs.

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('user/<str:username>/', views.userpage, name='userpage'),
    path('contracts_between/<str:username>/', views.contracts_between, name='contracts_between'), # by|to=me|username
    path('contracts_to_me/', views.contracts_to_me, name='contracts_to_me'), # by=ANY, to=me (contractor perspective)
    path('contracts_by_me/', views.contracts_by_me, name='contracts_by_me'), # to=ANY, by=me (client perspective)
    path('contract/<int:pk>/', views.contract_page, name='contract'),
    path('transactions_to_me/', views.transactions_to_me, name='transactions_to_me'),
    path('user/<str:username>/reviews/', views.reviews_page, name='reviews'),
    # *****
    path('settings/', views.settings, name='settings'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    # *****

    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
