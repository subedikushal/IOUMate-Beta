"""myFinance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    ############### Dashboard ########################
    path('dashboard/', views.dashboard, name='dashboard'),

    ############### Auth ################################
    path('register/', views.register_api, name='register'),
    path('login/', views.login_api, name='login'),
    path('profile/<str:username>/', views.get_profile, name='profile'),
    path('profile/', views.get_profile, name='profile'),
    path('verify-email/<str:email>/<uuid:token>/',
         views.verify_email, name='verify_email'),
    path('send-verification-email/', views.send_verification_email,
         name='send_verification_email'),
    path('search/', views.search, name='search'),



    ################ Transactions ######################################
    path('addtransaction/', views.add_transaction, name='add_transaction'),
    path('gettransactions/', views.get_transactions, name='get_transactions'),
    path('verifytransaction/', views.verify_transaction, name='verify_transaction'),


    ####### Friend #############################
    path('unfriend/', views.unfriend, name='unfriend'),
    path('friends/', views.get_friend_list, name='get_friend_list'),
    path('sendrequest/', views.send_friend_request, name='send_request'),
    path('acceptrequest/', views.accept_friend_request, name='accept_request'),
    path('friendrequests/', views.get_friend_req_list, name='get_friend_req_list'),
    path('sentrequests/', views.get_sent_friend_req_list,
         name='get_sent_friend_req_list'),
    path('deleterequest/', views.delete_request,
         name='delete_request'),


    ########## Personal Expense Tracker #################
    path('addexpense/', views.add_expense, name='add_expense'),
    path('updateexpense/<int:pk>/', views.update_expense, name='update_expense'),
    path('getexpense/<int:pk>/', views.get_expense, name='get_expense'),
    path('getexpenses/', views.get_expenses, name='get_expenses'),
    path('deleteexpense/<int:pk>/', views.delete_expense, name='delete_expenses'),


    path('addincome/', views.add_income, name='add_income'),
    path('updateincome/<int:pk>/', views.update_income, name='update_income'),
    path('getincome/<int:pk>/', views.get_income, name='get_income'),
    path('getincomes/', views.get_incomes, name='get_incomes'),
    path('deleteincome/<int:pk>/', views.delete_income, name='delete_incomes'),

    path('allincomeexpenses/', views.get_income_plus_expenses,
         name='all_income_expenses'),

    path('allincomeexpensesbyday/', views.get_income_plus_expenses_by_day,
         name='all_income_expenses_by_day'),

    path('hi/', views.get_hi, name='hi'),



]
if (settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
