from rest_framework import serializers

class YouTubeChannelSerializer(serializers.Serializer):
    channel_id = serializers.CharField(source="id")
    channel_name = serializers.CharField(source="snippet.title")
    description = serializers.CharField(source="snippet.description")
    custom_url = serializers.CharField(source="snippet.customUrl")
    thumbnail_url = serializers.CharField(source="snippet.thumbnails.high.url")
    published_at = serializers.DateTimeField(source="snippet.publishedAt")
    view_count = serializers.CharField(source="statistics.viewCount")
    subscriber_count = serializers.CharField(source="statistics.subscriberCount")
    video_count = serializers.CharField(source="statistics.videoCount")
    country = serializers.CharField(source="snippet.country")