# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import json
import httplib2
import os
import sys
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from django.contrib.auth import authenticate, login
from django.template import loader
import datetime
from django.shortcuts import redirect
from .models import Credentials,User,Sales_person_freetimes,Calendar_request

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'C:\\Users\\CC\\django-projects\\scribe\\myapp\\client_secret.json'
APPLICATION_NAME = 'Web client 1'


def login_view(request):
    template = loader.get_template('myapp/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def authorize_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user_type = request.POST.get('user_type','Employee')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        print(login(request, user))
        return redirect('/myapp/')
        # Redirect to a success page.
    else:
        return redirect('/myapp/login')
        # Return an 'invalid login' error message.

def get_flow():
    #returns flow object for our application
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES,redirect_uri='http://localhost:8080/')
    flow.user_agent = APPLICATION_NAME
    return flow


def get_auth_uri(flow):
    #returns oauth redirect URI to get access token
    auth_uri = flow.step1_get_authorize_url()
    return auth_uri

def create_event(event,credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return event


@login_required()
def process_customer_form(request):

    # event = {
    #   'summary': 'Google I/O 2015',
    #   'description': 'A chance to hear more about Google\'s developer products.',
    #   'start': {
    #     'dateTime': '2017-05-15T11:30:00',
    #     'timeZone': 'Asia/Kolkata',
    #   },
    #   'end': {
    #     'dateTime': '2017-05-15T12:00:00',
    #     'timeZone': 'Asia/Kolkata',
    #   },
    # }
    # Process Customer form and Create event object like above and call create_event api

    #Algorithm to select Sales Person in round robin fashion
    '''
     rows = fetch all rows from Sales_person_freetimes model where starttime is customer selected time slot
     #each row corresponds to one sales person who is free at that time
     get count of previously allotted Calendar_events for every sales guy who is free
     if count is same for all free sales rep:
         randomly select a sales rep
    else:
        find sales guy with lowest appointment count
    update Calendar_request model with that sales rep id
    fetch oauth access tokens from Credentials model for allotted sales rep
    '''
    if request.user.is_authenticated():
        username = request.user.username
    event = {}
    # get oauth credentials for selected sales rep
    credentials = Credentials.objects.filter(id__username=alloted_sales_guy_from_algorithm)
    credentials = credentials.credential
    credentials = client.OAuth2Credentials.from_json(credentials)

    # if access token expired
    if credentials.access_token_expired:
        return redirect('/myapp/oauth2callback')
    else:
        create_event(event,credentials)
    return HttpResponse('Success')


@login_required()
def get_customer_form(request):
    if request.user.is_authenticated():
        username = request.user.username
    template = loader.get_template('myapp/customer_form.html')
    # Fetching Previous Calendar Events scheduled by customer to display in customer page
    previous_calendar_events = Calendar_request.objects.filter(customer_id__name = username)
    context = {'prev_events':previous_calendar_events}
    return HttpResponse(template.render(context, request))


@login_required()
def get_customer_form(request):
    template = loader.get_template('myapp/sales.html')
    context = {}
    return HttpResponse(template.render(context, request))


@login_required()
def process_sales_form(request):
    if request.user.is_authenticated():
        username = request.user.username
    else:
        return redirect('/myapp/login')

    #update Sales_person_freetimes model with time slots the sales person selects
    # for example if sales person 'A' selects slots (9 to 11 and 4 to 5)
    # make one entry for every half an hour like below in Sales_person_freetimes table
    # A  Asia/Kolkata 9
    # A  Asia/Kolkata 9.30
    # A  Asia/Kolkata 10.00
    # A  Asia/Kolkata 10.30
    # A  Asia/Kolkata 4.00
    # A  Asia/Kolkata 4.30



@login_required()
def index(request):
    if request.user.is_authenticated():
        username = request.user.username
    else:
        return redirect('/myapp/login')
    credentials = Credentials.objects.filter(id__username=username)
    #if user has not authorized access to Google Calendar redirect to get acces token first
    if not credentials:
        return redirect('/myapp/oauth2callback')

    credentials = credentials.credential
    credentials = client.OAuth2Credentials.from_json(credentials)

    # if access token expired
    if credentials.access_token_expired:
        return redirect('/myapp/oauth2callback')

    return HttpResponse("test")
    #return HttpResponse("<a href='"+uri+"' target="'_blank'">Authorize calendar</a>")


@login_required()
def oauth2callback(request):
    if request.user.is_authenticated():
        username = request.user.username
    else:
        return redirect('/myapp/login')
    flow = get_flow()
    if 'code' not in request.GET:
        auth_uri = get_auth_uri(flow)
        return redirect(auth_uri)
    else:
        auth_code = request.GET.get('code','')
        credentials = flow.step2_exchange(auth_code)
        Credentials.objects.create({'id':User.objects.get(username=username).id,'credential':credentials.to_json()})
    return redirect('myapp/')