# import pika.exceptions
# import logging
#
# logger = logging.getLogger(__name__)
#
# def connect_to_rabbitmq_server():
#     try:
#         connection_params = pika.PlainCredentials(username='test_user', password='test_password')
#         connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(credentials=connection_params,
#         host='localhost', port=5671, virtual_host='test_vhost'))
#         channel = connection.channel()
#         return channel
#
#     except pika.exceptions.AMQPChannelError:
#         logger.warning('rabbitmq server is not running... RUN THE SERVER!')
#
#
# #
# class StopStreamError(BaseException): # this exception is used to stop streaming video...
#     # need to get thread id somehow....
#
#     def __call__(self, *args, **kwargs):
#         logger.debug('exception for stoping video has been raised....')
#         raise self
#
# def raise_stop_exception():
#     raise StopStreamError()

# @decorators.api_view(['POST'])
# @csrf.csrf_exempt
# def continue_streaming_video(request):
#
#     logger.debug('continue video streaming....')
#     range_header = request.HEADERS.get('Range')
#     file = request.FILES.get('video_file').file
#
#     return django.http.StreamingHttpResponse(
#     streaming_content=stream_video_file(range_header=range_header,
#     file_content=file), content_type='video/%s' % file.name.split('.')[1])
#
# def stream_video_file(range_header, file_content):
#     """This method going to stream file depends on request RANGE Header"""
#     start, end_byte = range_header.split('/')[1].split('-')
#     with open(file_content, mode='rb') as video_file:
#         content = video_file.seek(start)
#         yield content.read(end_byte)

# @decorators.api_view(['GET', 'HEAD'])
# def edit_playing_video(request):
#
#     bytes_length = request.HEADERS.get('Video-Bytes-Length')
#     video = models.Video.objects.filter(id=request.query_params.get('video_id'))
#     timecode = request.query_params.get('timecode')
#     byte = get_video_byte_by_timecode(timecode=timecode, length=bytes_length,
#     video=video, format=video.name.split('.')[1])
#     return django.http.HttpResponse(json.dumps({'start_byte': byte}))
#
# def get_video_byte_by_timecode(timecode, video, length, format: typing.Literal['mp4', 'mp3']) -> int:
#     # if basically it spends 1 byte per second...
#     import cv2
#     video_file = cv2.VideoCapture(video, format=format)
#     duration = video_file.get(cv2.CAP_PROP_POS_MSEC)
#     bytes_speed = round(length / duration)
#     return timecode * bytes_speed

# class StreamVideoAPIView(views.APIView):
#
#     permission_classes = (api_perms.CheckIsBlockedOrNotMemberUser,)
#
#     def set_response_headers(self, response):
#         """Sets Response necessary headers..."""
#         response.headers['Cache-Control'] = 'no-cache'
#         response.headers['Content-Disposition'] = 'file-attachment; charset=utf-8'
#         return response
#
#     @never_cache
#     def get(self, request):
#         try:
#             self.check_object_permissions(request=request, obj=request.user)
#             _video_url = models.Video.objects.filter(name__iexact=request.query_params.get('video_name')).file_link
#
#             file = files_api._get_file_aws_file(file_link=_video_url,
#             bucket_name=settings.AWS_IMAGES_BUCKET_NAME)
#
#             logger.debug('file has been parsed....')
#             response = django.http.StreamingHttpResponse(self.stream_video_file(request, file), content_type=
#             'video/%s' % file.name.split('.')[1])
#
#             response = self.set_response_headers(response)
#             return response
#
#         except exceptions.AwsFileNotFoundError as _aws_err:
#
#             logger.debug('file is not found...')
#             return django.http.HttpResponse(content=json.dumps(_aws_err.message),
#             status=status.HTTP_404_NOT_FOUND)
#
#         except botocore.exceptions.ConfigNotFound:
#             logger.error('no such bucket has been found...')
#             return django.http.HttpResponseNotFound()
#
#         except django.core.exceptions.PermissionDenied:
#             logger.debug('user is blocked... %s :' % request.user.username)
#             return django.http.HttpResponseForbidden()
