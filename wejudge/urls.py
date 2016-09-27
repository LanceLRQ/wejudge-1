"""wejudge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

import apps.bnuzoj.urls
import apps.problem.urls
import apps.account.urls
import apps.education.urls
import apps.asgn.urls
import apps.cpanel.urls
import apps.contest.urls
import apps.datacenter.urls
import apps.oauth2.urls
import apps.helper.urls
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'', include(apps.bnuzoj.urls)),                    # Index APP BnuzOJ
    url(r'^account/', include(apps.account.urls)),          # APP Account
    url(r'^asgn/', include(apps.asgn.urls)),                # APP Asgn
    url(r'^problem/', include(apps.problem.urls)),          # APP Problem Archive
    url(r'^education/', include(apps.education.urls)),      # APP Education Center
    url(r'^cpanel/', include(apps.cpanel.urls)),            # APP Control Panel
    url(r'^contest/', include(apps.contest.urls)),          # APP Contest
    url(r'^datacenter/', include(apps.datacenter.urls)),    # APP DataCenter
    url(r'^oauth2/', include(apps.oauth2.urls)),            # APP Oauth2
    url(r'^helper/', include(apps.helper.urls)),            # APP Helper
    url(r'^admin/', admin.site.urls),
]
