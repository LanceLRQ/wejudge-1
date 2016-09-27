from django.shortcuts import render

import wejudge.kernel.oauth2 as Oauth2


def authorize(request):
    viewer = Oauth2.Oauth2Service(request)
    viewer.authorize()
    return viewer.render()


def access_token(request):
    viewer = Oauth2.Oauth2Service(request)
    viewer.access_token()
    return viewer.render()


def valid_token(request):
    viewer = Oauth2.Oauth2Service(request)
    viewer.valid_token()
    return viewer.render()


def refresh_token(request):
    viewer = Oauth2.Oauth2Service(request)
    viewer.refresh_token()
    return viewer.render()