"""
Views.py
*****************
This file contains all of the views for the site.
These are called by urls.py et all when appropriate
"""

from django.shortcuts import render, HttpResponse, redirect
import json
from .models import Element, Connection, EmbedLink, NodeBlogPage, ActivOut, UserAttributes, UserInterest
from .models import StarBlogPage as ElementBlogPage
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from home.forms import EditProfileForm, UserInterestForm
from django.contrib.auth import update_session_auth_hash
from slugify import slugify


# Index request
def index(request):
    return render(request, 'home/index.html')


@login_required()
def kumu(request):
    toTemplate = {}

    if EmbedLink.objects.filter(id=request.GET.get('view')):
        view = request.GET.get('view')
    elif (not EmbedLink.objects.all().first()):
        # EmbedLink is empty!
        return redirect('index')
    else:
        view = EmbedLink.objects.first().id

    url = EmbedLink.objects.filter(id=view).first().embedURL
    bare = EmbedLink.objects.filter(id=view).first().bare
    simple = EmbedLink.objects.filter(id=view).first().simple
    scroll = EmbedLink.objects.filter(id=view).first().scroll

    toTemplate["link"] = urlFlagsHelper(url, bare, scroll, simple)

    return render(request, 'home/kumuMapPage.html', toTemplate)


# Simple helper when converting embedlink model to an actual link
def urlFlagsHelper(url, bare, scroll, simple):
    # (1/0 not T/F)
    if bare:
        bare = '1'
    else:
        bare = '0'
    if simple:
        simple = '1'
    else:
        simple = '0'
    if scroll:
        scroll = '1'
    else:
        scroll = '0'
    # kumu embed links take a variety of paramaters (0/1 not T/F). bare, simple and scroll are the only ones relevant to this application for the moment
    return url + "?bare=" + bare + "&simple=" + simple + "&scroll=" + scroll


def blueprint(request):
    """
    Function that processes map elements in the db and returns a json string 
    That represents the map in a form that kumu can understand.
    """
    blueprint = {}
    # This code below will build elements from db
    elements = []
    for eachElement in Element.objects.all():
        # poor name due to conflicting variable scope from model (blogpage)
        temp = {}
        temp['id'] = eachElement.id
        temp['label'] = eachElement.label
        temp['description'] = eachElement.description
        blogPage = ElementBlogPage.objects.filter(element=eachElement).first()
        nBlogPage = NodeBlogPage.objects.filter(element=eachElement).first()
        if (eachElement.child):
            if (not blogPage and not nBlogPage and eachElement.child.type == 'S'):
                blogPage = ElementBlogPage.objects.filter(element=eachElement.child).first()
            elif (not blogPage and not nBlogPage):
                blogPage = NodeBlogPage.objects.filter(element=eachElement.child)

        embedLink = EmbedLink.objects.filter(relatedElement=eachElement).first()
        if (blogPage):
            temp['description'] += \
                "\r\n <a href=\"" + (request.build_absolute_uri(blogPage.get_url())) + "\">Tell me more</a> "
        elif (nBlogPage):
            temp['description'] += \
                "\r\n <a href=\"" + (request.build_absolute_uri(nBlogPage.get_url())) + "\">Tell me more</a> "
        if (embedLink):
            temp['description'] += " [Explore further](#" + embedLink.mapSlug + "/" + embedLink.viewSlug + ") "

        # not element.type because that would be the 4 letter code we use
        temp['element type'] = eachElement.get_type_display()

        temp['tags'] = []
        for tag in eachElement.tags.all():
            # slugs for kumu, keep it pretty!
            temp['tags'].append(slugify(tag.__str__()))

        elements.append(temp)
    blueprint["elements"] = elements
    # This code below will build connections from db
    connections = []
    if (Connection.objects.all().count() > 0):
        for connection in Connection.objects.all():
            temp = {}
            temp["from"] = connection.a.id
            temp["to"] = connection.b.id
            # as above. Not .direction, .get_...
            temp["direction"] = connection.get_direction_display()
            connections.append(temp)

    blueprint["connections"] = connections

    data = json.dumps(blueprint)
    return HttpResponse(data, content_type='application/json')


@staff_member_required()
def mapIndex(request):
    toTemplate = {}
    toTemplate["galaxies"] = []
    toTemplate["constellations"] = []
    toTemplate["stars"] = []

    # for every galaxy element
    for g in Element.objects.filter(type="G").all():
        # if we have a URL related to it
        if EmbedLink.objects.filter(relatedElement=g):
            # send it to the template with url as (label,url)
            toTemplate["galaxies"].append((g.label, EmbedLink.objects.filter(relatedElement=g).first().id))
        # we may not have one link for every galaxy (db in dev, missing views because bad user)
        else:
            toTemplate["galaxies"].append((g.label, "#"))

    # for every constellation element
    for c in Element.objects.filter(type="C").all():
        # if we have a URL related to it
        if EmbedLink.objects.filter(relatedElement=c):
            # send it to the template with url as (label,url)
            toTemplate["constellations"].append((c.label, EmbedLink.objects.filter(relatedElement=c).first().id))
        # we may not have one link for every galaxy (db in dev, missing views because bad user)
        else:
            toTemplate["constellations"].append((c.label, "#"))

    # for every star element
    for s in Element.objects.filter(type="S").all():
        # if we have a URL related to it
        if EmbedLink.objects.filter(relatedElement=s):
            # send it to the template with url as (label,url)
            toTemplate["stars"].append((s.label, EmbedLink.objects.filter(relatedElement=s).first().id))
        # we may not have one link for every galaxy (db in dev, missing views because bad user)
        else:
            toTemplate["stars"].append((s.label, "#"))
    return render(request, 'home/insightMapindex.html', toTemplate)


def register(request):
    """
    Registration view
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
        else:
            dict = {
                'form': form,
                'fail': True,
            }
            return render(request, 'home/register.html', dict)
    else:
        form = UserCreationForm()
        dict = {'form': form}
        return render(request, 'home/register.html', dict)


@login_required()
def profileChange(request):
    """
    View for when a user is editing their profile information
    """
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
        else:
            dict = {
                'form': form,
                'fail': True,
            }
            return render(request, 'home/profile.html', dict)
    else:
        form = EditProfileForm(instance=request.user)
        dict = {'form': form}
        return render(request, 'home/profile.html', dict)


@login_required()
def passwordChange(request):
    """
    View for changing a user's password
    """
    if request.method == "POST":
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request.POST, form.user)
            return redirect('/profile/')
        else:
            dict = {
                'form': form,
                'fail': True,
            }
            return render(request, 'home/passwordChange.html', dict)
    else:
        form = PasswordChangeForm(user=request.user)
        dict = {'form': form}
        return render(request, 'home/passwordChange.html', dict)


@login_required()
def userReport(request):
    """
    View to generate users' reports.
    """
    stars = []
    interests = request.user.userattributes.interests.all()
    if not interests:
        return redirect('index')
    dict = {}
    # Iterate through user interests
    for interest in interests:
        if not interest.element in stars:
            stars.append(interest.element)
    allStarInterests = []
    # Iterate through user stars
    for star in stars:
        starsInterests = []
        for interest in interests:
            if interest.element == star:
                # interest.interest is the activOut :)
                starsInterests.append(interest.activOut)
        allStarInterests.append((star, starsInterests))
    data = {"stars": allStarInterests}
    return render(request, 'home/userReport.html', data)


@login_required()
def interestsChange(request):
    """
    View for adding new interests from star blog pages.
    The info is sent to this view from blog page, then
    redirects to user reporting page, or home on fail
    """
    if request.method == "POST":
        data = request.POST
        user = request.user
        star = Element.objects.get(id=data.get('element'))
        activOuts = []
        for datum in data:
            if datum == 'element' or datum == 'csrfmiddlewaretoken':
                continue
            else:
                activOuts.append(datum)
        for activOutid in activOuts:
            if ActivOut.objects.filter(id=activOutid):
                model = ActivOut.objects.get(id=activOutid)
                if not UserInterest.objects.filter(activOut=model).filter(element=star).exists():
                    interest = UserInterest.objects.create(activOut=model, element=star)
                else:
                    interest = UserInterest.objects.filter(activOut=model).get(element=star)
                # if not user.userattributes.interests.filter(interest=interest).exists():
                user.userattributes.interests.add(interest)

        return redirect('userReport')
    else:
        return redirect('index')
