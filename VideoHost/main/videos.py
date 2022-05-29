from __future__ import annotations

import django.http
import rest_framework.reverse
from django.shortcuts import render
from django.template.response import TemplateResponse

from django.views.decorators.cache import never_cache
from .aws_s3 import files_api

from django.conf import settings
from rest_framework.decorators import action

from rest_framework import status, permissions, views, decorators, viewsets
import logging, botocore.exceptions

from . import serializers, exceptions, models, permissions as api_perms
import os, django.core.exceptions


class GroupVideoAPIView(viewsets.ModelViewSet):

    serializer_class = serializers.VideoSerializer
    queryset = models.ChatGroup.objects.all()
    # bucket_name = getattr(settings, 'AWS_VIDEOS_BUCKET_NAME')

    def check_permissions(self, request):

        group = models.ChatGroup.objects.filter(
        id=request.query_params.get('group_id')).first()
        if not request.user in group.members.all():
            return django.core.exceptions.PermissionDenied()
        return True

    @action(methods=['post'], detail=False)
    def create(self, request, **kwargs):

        # file = request.FILES.get('video_file')
        # group_id = request.query_params.get('group_id')
        # group = models.ChatGroup.objects.filter(id=group_id).first()
        # try:
        #     file_link = files_api._save_file_to_aws(file, bucket_name=getattr(settings, 'AWS_VIDEO_BUCKET_NAME'))
        #     group.videos_set.create(file_link=file_link)
        #     return django.http.HttpResponse(status=200)
        # except():
        #     logger.error('could not upload video...')
        pass

    @action(methods=['get'], detail=True)
    def retrieve(self, request):
        #
        # obj = (files_api._get_file_aws_file(bucket_name=self.bucket_name, file_link=obj.file_link)
        # for obj in self.get_queryset()(group_name=request.query_params.get('group_id')
        # ).videos.filter(id=request.query_params['file_id'])) # return file for the object of the specific group by the id
        #
        # serialized_data = self.serializer_class(obj, many=False).data
        # return django.http.FileResponse(data={'file': serialized_data})
        pass

    @action(methods=['get'], detail=False)
    def list(self, request):

        # group_videos = (files_api._get_file_aws_file(bucket_name=self.bucket_name, file_link=obj.file_link)
        # for obj in self.get_queryset()(group_name=request.query_params.get('group_id')
        # ).videos.all()) # return file for the object of the specific group by the id
        # return django.http.FileResponse({'videos': group_videos})
        pass

    @action(methods=['delete'], detail=False)
    def destroy(self, request, *args, **kwargs):
        # try:
        #     video = models.Video.objects.get(id=request.query_params.get('video_id'))
        #     if files_api._delete_from_aws_storage(bucket_name=settings.VIDEO_AWS_BUCKET_NAME, filelink=video.file_link):
        #         video.delete()
        #         logger.debug('video has been permanently deleted')
        #     return django.http.HttpResponse(status=status.HTTP_200_OK)
        #
        # except(django.core.exceptions.ObjectDoesNotExist, exceptions.AwsFileNotFoundError):
        #     return django.http.HttpResponseNotFound()
        #
        pass

