from django.shortcuts import render, redirect
from .models import Slider, Team
from pytube import *
from django.contrib import messages
from django.views.generic import View
import requests
from bs4 import BeautifulSoup
# Create your views here.


def home(request):
    sliders = Slider.objects.all()
    teams = Team.objects.all()
    data = {
        'sliders': sliders,
        'teams': teams,

    }
    return render(request, 'webpages/home.html', data)


def about(request):
    return render(request, 'webpages/about.html')


def services(request):
    return render(request, 'webpages/services.html')


def contact(request):

    return render(request, 'webpages/contact.html')


class YoutubeDownload(View):
    def get(self, request):
        return render(request, 'includes/youtubedownload.html')

    def post(self, request):
        # for fetching the video
        if request.POST.get('fetch-vid'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)
            vidTitle, vidThumbnail = video.title, video.thumbnail_url
            qual, stream = [], []
            for vid in video.streams.filter(progressive=True):
                qual.append(vid.resolution)
                stream.append(vid)
            context = {'vidTitle': vidTitle, 'vidThumbnail': vidThumbnail,
                       'qual': qual, 'stream': stream,
                       'url': self.url}

            return render(request, 'includes/youtubedownload.html', context)

        # for downloading the video
        elif request.POST.get('download-vid'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)
            stream = [x for x in video.streams.filter(progressive=True)]
            video_qual = video.streams[int(
                request.POST.get('download-vid')) - 1]

            video_qual.download(output_path='../../Downloads')
            messages.success(request, 'Video Downloaded Successfully')
            return redirect('home')

        return render(request, 'includes/youtubedownload.html')


def youtubeVideoDetails(request):

    if request.method == 'POST':
        url = request.POST.get('videoUrl')
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        thumbnail = soup.find('meta', property='og:image')
        likes = soup.find(
            'span', class_='like-button-renderer-like-button-unclicked')
        dislikes = soup.find(
            'span', class_='like-button-renderer-dislike-button-unclicked')
        views = soup.find('div', class_='watch-view-count')
        comments = soup.find('h2', class_='comment-section-header-renderer')
        channel_subscribers = soup.find(
            'span', class_='yt-subscription-button-subscriber-count-branded-horizontal yt-subscriber-count')
        channel_name = soup.find(
            'yt-formatted-string', class_='ytd-channel-name')

        context = {
            'title': title['content'],
            'description': description['content'],
            'thumbnail': thumbnail['content'],
           
            'dislikes': dislikes.text,
            'views': views.text,
            'comments': comments.text,
            'channel_subscribers': channel_subscribers.text,
            'channel_name': channel_name.text,
        }
        messages.success(request, 'Video Details Fetched Successfully')
        return render(request, 'includes/youtubeVideoDetails.html', context)

    return render(request, 'includes/youtubeVideoDetails.html')
