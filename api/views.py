import datetime
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
import itertools
from .models import User, Transaction, Expense, Income
from .utils import message
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import permissions
from .serializers import UserSerializer, TransactionSerializer, TransactionSerializer2, ExpenseSerializer, IncomeSerializer
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import EmailVerificationToken
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Sum


# fine

from django.conf import settings


@api_view(['POST'])
def register_api(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        new_user = serializer.save()
        request.user = new_user
        try:
            send_verification_email(request)
        except Exception:
            new_user.delete()
            return Response(message("Error occurred while sending mail.", True))
        return Response(message("A verification link has been sent to your email for verification.", True))
        # res = message(
        #     f"{account.username} successfully registered as a new user", True)
    else:
        msg_val = serializer.errors.values()
        res = message(list(itertools.chain(*msg_val)), False)
    return Response(res)

# fine


@api_view(['POST'])
def login_api(request):
    """ Payload
    {
        'email' : '',
        'password':'',
    }
    """
    res = {}
    email = request.data['email']
    password = request.data['password']
    user = authenticate(
        email=email, password=password)
    if user is not None and user.is_email_verified == True:
        refresh = RefreshToken.for_user(user)
        res = message(
            'Logged in successfully',
            True,
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        )
    elif user is not None and user.is_email_verified == False:
        res = message('Email verification required.', False)
    else:
        res = message('No matching credentials found', False)
    return Response(res)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_hi(request):
    res = message('Hi', True)
    return Response(res)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_friend_list(request):
    friends = request.user.friends
    res = []
    for friend in friends:
        friend_obj = User.objects.get(username=friend)
        try:
            avatar_url = friend_obj.avatar.url
        except Exception:
            avatar_url = ''
        data = {
            'first_name': friend_obj.first_name,
            'last_name': friend_obj.last_name,
            'username': friend_obj.username,
            'email': friend_obj.email,
            'avatar': avatar_url
        }
        res.append(data)
    return Response(message("", True, res))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_friend_req_list(request):
    friends = request.user.friend_requests
    print(friends)
    res = []
    for friend in friends:
        print(friend)
        print(User.objects.all())
        friend_obj = User.objects.get(username=friend)
        try:
            avatar_url = friend_obj.avatar.url
        except Exception:
            avatar_url = ''
        data = {
            'first_name': friend_obj.first_name,
            'last_name': friend_obj.last_name,
            'username': friend_obj.username,
            'email': friend_obj.email,
            'avatar': avatar_url
        }
        res.append(data)
    return Response(message("", True, res))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_sent_friend_req_list(request):
    friends = request.user.sent_friend_requests
    res = []
    for friend in friends:
        friend_obj = User.objects.get(username=friend)
        try:
            avatar_url = friend_obj.avatar.url
        except Exception:
            avatar_url = ''
        data = {
            'first_name': friend_obj.first_name,
            'last_name': friend_obj.last_name,
            'username': friend_obj.username,
            'email': friend_obj.email,
            'avatar': avatar_url
        }
        res.append(data)
    return Response(message("", True, res))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_request(request):
    username = request.data['username']
    user = User.objects.get(username=username)
    sent = request.data['sent']
    if sent:
        request.user.sent_friend_requests.remove(username)
        user.friend_requests.remove(request.user.username)
    else:
        user.sent_friend_requests.remove(request.user.username)
        request.user.friend_requests.remove(user.username)
    user.save()
    request.user.save()
    return Response(message("Deleted successfully.", True))
# post enabled


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def search(request):
    username = request.data['username']
    if (username == request.user.username):
        return Response(message('Why are you searching yourself?', False))
    try:
        friends = User.objects.filter(
            username__istartswith=username, is_email_verified=True)
        if (len(friends) == 0):
            return Response(message('No user exist with the given username.', False))

        all_data = []
        for friend in friends:
            try:
                avatar_url = friend.avatar.url
            except Exception:
                avatar_url = ''
            data = {
                'first_name': friend.first_name,
                'last_name': friend.last_name,
                'username': friend.username,
                'email': friend.email,
                'avatar': avatar_url,
            }
            all_data.append(data)
        return Response(message("User found.", True, all_data))
    except User.DoesNotExist:
        return Response(message('No user exist with the given username.', False))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def send_friend_request(request):
    sender = request.user.username
    reciever = request.data['username']
    if (sender == reciever):
        return Response(message("Sender and accepter cannot be same person.", False))
    try:
        reciever_obj = User.objects.get(username=reciever)
        sender_obj = User.objects.get(username=sender)

        if (sender_obj.friends is not None and reciever in sender_obj.friends):
            return Response(message("Already friend!", False))
        if (sender_obj.sent_friend_requests is not None and reciever in sender_obj.sent_friend_requests):
            return Response(message("Friend request pending.", False))
        if (reciever_obj.friend_requests is not None and sender in reciever_obj.friend_requests):
            return Response(message("Friend request pending.", False))

        if (sender_obj.sent_friend_requests is None):
            sender_obj.sent_friend_requests = [reciever]
        else:
            sender_obj.sent_friend_requests.append(reciever)
        if (reciever_obj.friend_requests is None):
            reciever_obj.friend_requests = [sender]
        else:
            reciever_obj.friend_requests.append(sender)
        sender_obj.save()
        reciever_obj.save()
        return Response(message('Friend request send successfully.', True))
    except User.DoesNotExist:
        return Response(message('No user exist with the given username.', False))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def accept_friend_request(request):
    accepter = request.user.username
    to_be_accepted = request.data['username']
    if (accepter == to_be_accepted):
        return Response(message("Sender and accepter cannot be same person.", False))
    accepter_obj = User.objects.get(username=accepter)
    try:
        to_be_accepted_obj = User.objects.get(username=to_be_accepted)
        if accepter_obj.friend_requests is None or to_be_accepted not in accepter_obj.friend_requests:
            return Response(message('No such friend requests.', False))
        accepter_obj.friend_requests.remove(to_be_accepted)
        if (accepter_obj.friends is None):
            accepter_obj.friends = [to_be_accepted]
        else:
            accepter_obj.friends.append(to_be_accepted)

        if to_be_accepted_obj.sent_friend_requests is None or accepter not in to_be_accepted_obj.sent_friend_requests:
            return Response(message('No such friend requests.', False))

        if (to_be_accepted_obj.friends is None):
            to_be_accepted_obj.friends = [accepter]
        else:
            to_be_accepted_obj.friends.append(accepter)
        to_be_accepted_obj.sent_friend_requests.remove(accepter)
        accepter_obj.save()
        to_be_accepted_obj.save()
        return Response(message('Friend request accepted.', True))
    except User.DoesNotExist:
        return Response(message('No user exist with the given username.', False))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_transaction(request):
    transaction_serializer = TransactionSerializer(data=request.data)
    res = {}
    if transaction_serializer.is_valid():
        instance = transaction_serializer.save(user=request.user)
        t = TransactionSerializer2(instance)
        res = message("Transaction added successfullly.", True, t.data)
    else:
        msg_val = transaction_serializer.errors.values()
        res = message(list(itertools.chain(*msg_val)), False)
    return Response(res)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_profile(request, username=None):
    if username is None:
        try:
            avatar_url = request.user.avatar.url
        except Exception:
            avatar_url = ''

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'username': request.user.username,
            'email': request.user.email,
            'avatar': avatar_url,
        }
    else:
        user = User.objects.get(username=username)
        friend_requests = request.user.friend_requests
        sent_requests = request.user.sent_friend_requests
        friends = request.user.friends

        relation = 'N'
        if (username in friend_requests):
            relation = 'I'
        elif (username in sent_requests):
            relation = 'S'
        elif (username in friends):
            relation = 'F'
        try:
            avatar_url = user.avatar.url
        except Exception:
            avatar_url = ''

        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'avatar': avatar_url,
            'relation': relation
        }

    return Response(message("", True, [data]))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_transactions(request):
    friend = request.data['username']
    transactions = Transaction.objects.filter(
        Q(liney=request.user, diney=User.objects.get(username=friend)) | Q(diney=request.user, liney=User.objects.get(username=friend))).order_by('-date_of_transaction')
    serializer = TransactionSerializer2(transactions, many=True)
    return Response(message("", True, serializer.data))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def verify_transaction(request):
    transaction_id = request.data['transaction_id']
    transaction = Transaction.objects.get(id=transaction_id)
    if transaction.to_be_verified_by.username != request.user.username:
        return Response(message("Couldn't verify transaction.", False))
    transaction.is_verified = True
    transaction.date_of_verification = datetime.datetime.now()
    transaction.save()
    return Response(message('Transaction verified.', True))


def send_verification_email(request):
    token, created = EmailVerificationToken.objects.get_or_create(
        user=request.user)
    email = request.user.email
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token.token, 'email': email}))
    send_mail(
        'Verify your email address',
        f'Click this link to verify your email address: {verification_link}',
        'noreply@example.com',
        [email],
        fail_silently=False,
    )
    return Response(message("A verification link has been sent to your email for verification.", True))


def verify_email(request, email, token):
    request.user = User.objects.get(email=email)
    email_verification_token = get_object_or_404(
        EmailVerificationToken, token=token)
    email_verification_token.delete()
    usr = User.objects.get(email=request.user.email)
    usr.is_email_verified = True
    usr.save()
    html = '<p>Email Verified.</p>'
    return HttpResponse(html, content_type='text/html')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def unfriend(request):
    username = request.data['username']
    friend = User.objects.get(username=username)
    request.user.friends.remove(username)
    request.user.save()
    friend.friends.remove(request.user.username)
    friend.save()
    return Response(message('Friend removed successfully!', True))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dashboard(request):  # sourcery skip: avoid-builtin-shadow
    res_data = []
    friends = request.user.friends
    for f in friends:
        friend = User.objects.get(username=f)

        transactions = Transaction.objects.filter(
            Q(liney=request.user, diney=User.objects.get(username=friend)) | Q(diney=request.user, liney=User.objects.get(username=friend))).order_by('-date_of_transaction')
        net_total = 0
        for t in transactions:
            if t.is_verified:
                type = t.transaction_type
                amount = t.amount
                added_by = t.added_by
                if (type == 'C' and added_by == request.user):
                    net_total += amount
                elif type == 'C':
                    net_total -= amount
                elif (type == 'D' and added_by == request.user):
                    net_total -= amount
                elif type == 'D':
                    net_total += amount
        try:
            avatar_url = friend.avatar.url
        except Exception:
            avatar_url = ''
        data = {'username': friend.username, 'first_name': friend.first_name, 'email': friend.email,
                'last_name': friend.last_name, 'avatar': avatar_url, 'amount': net_total}
        res_data.append(data)
    return Response(message('', True, res_data))


# Personal Expense Tracking

# add expense

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_expense(request):
    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(message('Expense added.', True, serializer.validated_data))
    else:
        msg_val = serializer.errors.values()
        return Response(message(list(itertools.chain(*msg_val)), False))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_expenses(request):
    expenses = Expense.objects.filter(user=request.user)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(message('', True, serializer.data))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_expense(request, pk):
    expense = Expense.objects.get(pk=pk)
    serializer = ExpenseSerializer(expense)
    return Response(message('', True, serializer.data))


@api_view(['PUT', 'PATCH'])
@permission_classes((IsAuthenticated,))
def update_expense(request, pk):
    expense = Expense.objects.get(pk=pk)
    serializer = ExpenseSerializer(expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(message('Updated successfully.', True))
    else:
        return Response(message("Couldn't update.", False))


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_expense(request, pk):
    if expense := Expense.objects.get(pk=pk):
        expense.delete()
        return Response(message("Deleted successfully.", True))
    else:
        return Response(message("Record not found.", False))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_income(request):
    serializer = IncomeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(message('Income added.', True, serializer.validated_data))
    else:
        msg_val = serializer.errors.values()
        return Response(message(list(itertools.chain(*msg_val)), False))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_income(request, pk):
    income = Income.objects.get(pk=pk)
    serializer = IncomeSerializer(income)
    return Response(message('', True, serializer.data))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_incomes(request):
    expenses = Income.objects.filter(user=request.user)
    serializer = IncomeSerializer(expenses, many=True)
    return Response(message('', True, serializer.data))


@api_view(['PUT', 'PATCH'])
@permission_classes((IsAuthenticated,))
def update_income(request, pk):
    income = Income.objects.get(pk=pk)
    serializer = IncomeSerializer(income, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(message('Updated successfully.', True))
    else:
        return Response(message("Couldn't update.", False))


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_income(request, pk):
    if income := Income.objects.get(pk=pk):
        income.delete()
        return Response(message("Deleted successfully.", True))
    else:
        return Response(message("Record not found.", False))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_income_plus_expenses(request):
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    income_serializer = IncomeSerializer(incomes, many=True)
    expense_serializer = ExpenseSerializer(expenses, many=True)
    merged_data = income_serializer.data + expense_serializer.data
    sorted_data = sorted(
        merged_data, key=lambda x: x['created_at'], reverse=True)
    return Response(message('', True, sorted_data))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_income_plus_expenses_by_day(request):
    # last 7 days
    e_c = ['Food', 'Beverage', 'Lend/Borrow', 'Utility', 'Other']
    i_c = ['Salary', 'Bonus', 'Commission', 'Other']
    e_data = {}
    total_income = Income.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=7)).aggregate(Sum('amount'))['amount__sum']
    total_expense = Expense.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=7)).aggregate(Sum('amount'))['amount__sum']
    for c in e_c:
        expenses = Expense.objects.filter(
            user=request.user, category=c, created_at__gte=datetime.datetime.now() - timedelta(days=7)).aggregate(Sum('amount'))
        if expenses['amount__sum'] is None:
            expenses['amount__sum'] = 0
        e_data[c] = float(expenses['amount__sum'])
    total_expense = 0 if total_expense is None else float(total_expense)
    i_data = {}
    for c in i_c:
        incomes = Income.objects.filter(
            user=request.user, category=c, created_at__gte=datetime.datetime.now() - timedelta(days=7)).aggregate(Sum('amount'))
        if incomes['amount__sum'] is None:
            incomes['amount__sum'] = 0
        i_data[c] = float(incomes['amount__sum'])
    total_income = 0 if total_income is None else float(total_income)
    day7_data = {'expense': e_data, 'income': i_data,
                 'total_expense': total_expense, 'total_income': total_income}

    e_data = {}
    total_income = Income.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=15)).aggregate(Sum('amount'))['amount__sum']
    total_expense = Expense.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=15)).aggregate(Sum('amount'))['amount__sum']
    for c in e_c:
        expenses = Expense.objects.filter(
            user=request.user, category=c, created_at__gte=datetime.datetime.now() - timedelta(days=15)).aggregate(Sum('amount'))
        if expenses['amount__sum'] is None:
            expenses['amount__sum'] = 0
        e_data[c] = float(expenses['amount__sum'])
    total_expense = 0 if total_expense is None else float(total_expense)
    i_data = {}
    for c in i_c:
        incomes = Income.objects.filter(
            user=request.user, category=c, created_at__gte=datetime.datetime.now() - timedelta(days=15)).aggregate(Sum('amount'))
        if incomes['amount__sum'] is None:
            incomes['amount__sum'] = 0
        i_data[c] = float(expenses['amount__sum'])
    total_income = 0 if total_income is None else float(total_income)
    day15_data = {'expense': e_data, 'income': i_data,
                  'total_expense': total_expense, 'total_income': total_income}
    e_data = {}
    for c in e_c:
        expenses = Expense.objects.filter(
            user=request.user, category=c, created_at__gte=datetime.datetime.now() - timedelta(days=30)).aggregate(Sum('amount'))
        if expenses['amount__sum'] is None:
            expenses['amount__sum'] = 0
        e_data[c] = float(expenses['amount__sum'])
    total_income = Income.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=30)).aggregate(Sum('amount'))['amount__sum']
    total_expense = Expense.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=30)).aggregate(Sum('amount'))['amount__sum']
    total_expense = 0 if total_expense is None else float(total_expense)
    i_data = {}
    for c in i_c:
        incomes = Income.objects.filter(
            user=request.user, category=c, created_at__gte=datetime.datetime.now() - timedelta(days=30)).aggregate(Sum('amount'))
        if incomes['amount__sum'] is None:
            incomes['amount__sum'] = 0
        i_data[c] = float(incomes['amount__sum'])
    total_income = Income.objects.filter(
        user=request.user, created_at__gte=datetime.datetime.now() - timedelta(days=30)).aggregate(Sum('amount'))['amount__sum']
    total_income = 0 if total_income is None else float(total_income)
    day30_data = {'expense': e_data, 'income': i_data,
                  'total_expense': total_expense, 'total_income': total_income}
    data = {
        "day7": day7_data,
        "day15": day15_data,
        "day30": day30_data
    }
    return Response(message('', True, data))
