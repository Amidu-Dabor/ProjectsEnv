from multiprocessing import context
import datetime
from typing import Any
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# from django.core.mail import send_mail
# from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from .models import User, Department, Ticket, Subject, Comment
from .forms import TicketForm, CommentForm, UserCreateForm, UserUpdateForm


# Views

def login_page(request):
    login_page = 'login'
    #welcomeMsgSuccess =  ""
    
    if request.user.is_authenticated:
        return redirect('home')
            

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if email == "" and password == "":
            return HttpResponse("Please fill in email and password field.")
            #usernameMsgWarning = messages.warning(request, 'Fill in username and password to login')
        elif email == "":
            return HttpResponse("Please fill in email field.")
            #userPassMsgWarning = messages.warning(request, 'Username field was empty')
        elif password == "":
            return HttpResponse("Please fill in password field.")
            #passwordMsgWarning = messages.warning(request, 'Password field empty')
        elif user is not None:
            login(request, user)
            return redirect('home')
            # return HttpResponse(f"Hello { request.user }, welcome to QSupport!")
            # welcomeMsgSuccess = messages.success(request, f'Hello { request.user }, welcome to QSupport!')
        else:
            return HttpResponse("Invalid username or password.")
            #loginMsgError = messages.error(request, 'Invalid username or password')

    context = {'form': login_page}
    return render(request, 'base/login_register.html', context)


# def admin_login(request):
#     return render(request, 'base/')


def logout_user(request):
    user =  request.user
    logout(request)
    user.is_logged_in = False

    return redirect('login')


def register_page(request):
    form = UserCreateForm()

    try:
        if request.method == 'POST':
            form = UserCreateForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.user_name = user.user_name.lower()
                user.save()
                login(request, user)
                return redirect('home')
    except Exception as e:
        return HttpResponse("Oops! An error occurred during registration.")
        #registrationMsgError = messages.error(request, 'Oops! An error occurred during registration')
    else:
        #return HttpResponse("Registration Successful.")
        #registrationMsgSuccess = messages.success(request, 'Registration successful')

        context = {'form': form}
        return render(request, 'base/login_register.html', context)


def home(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''

    tickets = Ticket.objects.filter(
        Q(subject__name__icontains=query) |
        Q(creator__user_name__icontains=query) |
        Q(creator__department__name__icontains=query)
    ).distinct()
    
    departments = Department.objects.filter(Q(name__icontains=query)).distinct()
    all_users = User.objects.all()
    subjects_sliced = Subject.objects.all()[0:5]
    subjects = Subject.objects.all()
    
    ticket_comments = Comment.objects.filter(Q(ticket__subject__name__icontains=query))
    ticket_count = tickets.count()
    
                        
    context = {'tickets': tickets, 'subjects': subjects, 'subjects_sliced': subjects_sliced,
               'ticket_comments': ticket_comments, 'departments': departments, 
               'ticket_count': ticket_count, 'all_users': all_users
               }
    
    return render(request, 'base/home.html', context)


def dashboard(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''
    
    tickets = Ticket.objects.filter(
        Q(subject__name__icontains=query) |
        Q(creator__user_name__icontains=query)
    )[:6]
    
    ticket_comments = Comment.objects.filter(
        Q(user__user_name__icontains=query) |
        Q(ticket__subject__name__icontains=query)
        )[:3]
    open_ticket_count = tickets.count()
    
    context = {'tickets': tickets, 'ticket_comments': ticket_comments, 'open_ticket_count': open_ticket_count}
    
    return render(request, 'base/dashboard.html', context)


def dashboard_with_pivot(request):
    return render(request, 'dashboard_with_pivot.html', {})


# def pivot_data(request):
#     dataset = Ticket.objects.all()
#     data = serializers.serialize('json', dataset)
#     return JsonResponse(data, safe=False)


@login_required(login_url='login')
def ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    ticket_comments = ticket.comment_set.all()
    contributors = ticket.contributors.all()
    comment_count = ticket_comments.count()
    
    # # Current Date
    # dateNow = datetime.datetime.now()
    # thisYear = dateNow.year
    # thisMonth = dateNow.month
    # thisDay = dateNow.day
    # thisHour = dateNow.hour
    # thisMinute = dateNow.minute
        
    # if len(str(thisMonth)) == 1:
    #     thisMonth = "0" + str(thisMonth)
    # if len(str(thisDay)) == 1:
    #     thisDay = "0" + str(thisDay)
    # if len(str(thisHour)) == 1:
    #     thisHour = "0" + str(thisHour)
    # if len(str(thisMinute)) == 1:
    #     thisMinute = "0" + str(thisMinute)
          
    # #dateNow =  datetime.datetime.strftime(currDate, "%a %d %b., %Y %H:%M %p") 
    # dateNow = str(thisYear) + "-" + str(thisMonth) + "-" + str(thisDay) + " " + str(thisHour) + ":" + str(thisMinute)
    
    # # Ticket Created Date
    # ticketCreatedDate = ticket.created
    # tkYear = ticketCreatedDate.year
    # tkMonth = ticketCreatedDate.month
    # tkDay = ticketCreatedDate.day
    # tkHour = ticketCreatedDate.hour
    # tkMinute = ticketCreatedDate.minute
    
    # if len(str(tkMonth)) == 1:
    #     tkMonth = "0" + str(tkMonth)
    # if len(str(tkDay)) == 1:
    #     tkDay = "0" + str(tkDay)
    # if len(str(tkHour)) == 1:
    #     tkHour = "0" + str(tkHour)
    # if len(str(tkMinute)) == 1:
    #     tkMinute = "0" + str(tkMinute)
        
    # ticketDate = str(tkYear) + "-" + str(tkMonth) + "-" + str(tkDay) + " " + str(tkHour) + ":" + str(tkMinute)
    
    # # Comment Created Date
    # for comment in ticket_comments:
    #         commentCreatedDate = comment.created
            
    # cmYear = commentCreatedDate.year
    # cmMonth = commentCreatedDate.month
    # cmDay = commentCreatedDate.day
    # cmHour = commentCreatedDate.hour
    # cmMinute = commentCreatedDate.minute
        
    # if len(str(cmMonth)) == 1:
    #     cmMonth = "0" + str(cmMonth)
    # if len(str(cmDay)) == 1:
    #     cmDay = "0" + str(cmDay)
    # if len(str(cmHour)) == 1:
    #     cmHour = "0" + str(cmHour)
    # if len(str(cmMinute)) == 1:
    #     cmMinute = "0" + str(cmMinute)
            
    # commentDate = str(cmYear) + "-" + str(cmMonth) + "-" + str(cmDay) + " " + str(cmHour) + ":" + str(cmMinute)

    if request.method == 'POST':
        user = request.user
        body=request.POST.get('comment_body')
        
        if body == "":
            return HttpResponse("Please fill in comment field to contribute.")
            #commentMsgWarning = messages.warning(request, 'Please fill in comment field.')
        else:
            comment = Comment.objects.create(
                user=request.user,
                ticket=ticket,
                body=request.POST.get('comment_body'),
            )
            
        ticket.contributors.add(user)
        
        return redirect('ticket', pk=ticket.id)

    context = {'ticket': ticket, 'ticket_comments': ticket_comments, 
               'comment_count': comment_count, 'contributors': contributors
               }
    
    return render(request, 'base/ticket.html', context)


@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    tickets = user.ticket_set.all()
    ticket_comments = user.comment_set.all()
    tickets_count = tickets.count()
    subjects = Subject.objects.all()

    context = {'user': user, 'tickets': tickets, 
               'ticket_comments': ticket_comments, 
               'tickets_count': tickets_count, 'subjects': subjects}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_ticket(request):
    form = TicketForm()
    subjects = Subject.objects.all()

    if request.method == 'POST':
        subject = request.POST.get('subject')
        subject, created = Subject.objects.get_or_create(name=subject)
        
        Ticket.objects.create(
            creator=request.user,
            subject=subject,
            description=request.POST.get('description')
        )
        
        # if form.is_valid():
        #     ticket = form.save(commit=False)
        #     ticket.creator = request.user
        #     ticket.save()
        
        return redirect('home')

    context = {'form': form, 'subjects':subjects}
    
    return render(request, 'base/ticket_creation_form.html', context)


@login_required(login_url='login')
def update_ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    form = TicketForm(instance=ticket)
    subjects = Subject.objects.all()

    if request.user != ticket.creator:
        return HttpResponse("You have no permission to modify this ticket.")
        #ticketPermitMsgModifyWarning = messages.warning(request, 'You have no permission to modify this ticket.')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        subject, created = Subject.objects.get_or_create(name=subject)
        ticket.subject = subject
        ticket.description = request.POST.get('description')
        ticket.save()
        
        # form = TicketForm(request.POST, instance=ticket)
        # if form.is_valid():
        #     form.save()
        
        return redirect('home')

    context = {'form': form, 'subjects': subjects, 'ticket': ticket}
    
    return render(request, 'base/ticket_update_form.html', context)


@login_required(login_url='login')
def delete_ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)

    if request.user != ticket.creator:
        return HttpResponse("You have no permission to delete this ticket.")
        #ticketPermitMsgDeleteWarning = messages.warning(request, 'You have no permission to delete this ticket.')

    if request.method == 'POST':
        ticket.delete()
        return redirect('home')

    context = {'obj_to_delete': ticket}
    
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def delete_comment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse("You have no permission to delete this comment.")
        #commentPermitMsgDeleteWarning = messages.warning(request, 'You have no permission to delete this comment.')

    if request.method == 'POST':
        comment.delete()
        return redirect('ticket')

    context = {'obj_to_delete': comment}
    
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def edit_comment(request, pk):
    comment = Comment.objects.get(id=pk)
    form = CommentForm(instance=comment)
    
    if request.user != comment.user:
        return HttpResponse("You have no permission to modify this comment.")
        #commentPermitMsgModifyWarning = messages.warning(request, 'You have no permission to modify this comment.')

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('ticket', pk=comment.ticket.id)

    context = {'form': form}
    
    return render(request, 'base/comment_form.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserUpdateForm(instance=user)
    
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    
    context = {'form': form}
    
    return render(request, 'base/update_user.html',context )


def subjects_page(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''
    subjects = Subject.objects.filter(name__icontains=query)
    
    context = {'subjects': subjects}
    
    return render(request, 'base/subjects.html', context )


def request_page(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''
    tickets = Ticket.objects.filter(
        Q(creator__id__icontains=query) |
        Q(creator__user_name__icontains=query) |
        Q(subject__name__icontains=query) |
        Q(description__icontains=query)
    ).distinct()
    
    context = {'tickets': tickets}
    
    return render(request, 'base/request.html', context)


def requests_table(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''
    tickets = Ticket.objects.filter(
        Q(creator__id__icontains=query) |
        Q(creator__user_name__icontains=query) |
        Q(subject__name__icontains=query) |
        Q(description__icontains=query)
    ).distinct()
    
    context = {'tickets': tickets}
    
    return render(request, 'base/requests.html', context)


def activity_page(request):
    ticket_comments = Comment.objects.all()
    
    context = {'ticket_comments': ticket_comments}
    
    return render(request, 'base/activity.html', context)
