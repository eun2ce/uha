"""
URL configuration for uha_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from uha.views import YouTubeChannelInfo, NaverCafeProfileView, NaverCafeArticlesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('youtube/channel-info/', YouTubeChannelInfo.as_view(), name='youtube_channel_info'),
    path("naver-cafe/profile/", NaverCafeProfileView.as_view(), name="naver_cafe_profile"),
    path("naver-cafe/articles/<int:menu_id>/<int:page_id>/", NaverCafeArticlesView.as_view(),
         name="naver_cafe_articles"),
]
