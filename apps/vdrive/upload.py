# import http.client
# import httplib2
# import os
# import random
# import time
#
#
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaFileUpload
# from google_auth_oauthlib.flow import InstalledAppFlow
#
#
# httplib2.RETRIES = 1
#
# MAX_RETRIES = 10
#
# RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected, http.client.IncompleteRead,
#                         http.client.ImproperConnectionState, http.client.CannotSendRequest,
#                         http.client.CannotSendHeader, http.client.ResponseNotReady, http.client.BadStatusLine)
#
# RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
#
# CLIENT_SECRETS_FILE = "client_secret.json"
#
# SCOPES = "https://www.googleapis.com/auth/youtube.upload"
# YOUTUBE_API_SERVICE_NAME = "youtube"
# YOUTUBE_API_VERSION = "v3"
#
# MISSING_CLIENT_SECRETS_MESSAGE = """
# WARNING: Please configure OAuth 2.0
#
# To make this sample run you will need to populate the client_secrets.json file
# found at:
#
#    %s
#
# with information from the API Console
# https://console.developers.google.com/
#
# For more information about the client_secrets.json file format, please visit:
# https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
# """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                    CLIENT_SECRETS_FILE))
#
# VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
#
#
# def initialize_upload(youtube):
#     body = dict(
#         snippet=dict(
#             title="title",
#             description="desc",
#             categoryId="22"
#         ),
#         status=dict(
#             privacyStatus="unlisted"
#         )
#     )
#
#     insert_request = youtube.videos().insert(
#         part=",".join(body.keys()),
#         body=body,
#         media_body=MediaFileUpload(media_file, chunksize=-1, resumable=True)
#     )
#
#     response = None
#     error = None
#     retry = 0
#     while response is None:
#         try:
#             print("Uploading file...")
#             status, response = insert_request.next_chunk()
#             if response is not None:
#                 if 'id' in response:
#                     print("Video id '%s' was successfully uploaded." % response['id'])
#                 else:
#                     exit("The upload failed with an unexpected response: %s" % response)
#         except HttpError as er:
#             if er.resp.status in RETRIABLE_STATUS_CODES:
#                 error = "A retriable HTTP error %d occurred:\n%s" % (er.resp.status, er.content)
#             else:
#                 raise
#         except RETRIABLE_EXCEPTIONS as er:
#             error = "A retriable error occurred: %s" % er
#
#         if error is not None:
#             print(error)
#             retry += 1
#             if retry > MAX_RETRIES:
#                 exit("No longer attempting to retry.")
#
#             max_sleep = 2 ** retry
#             sleep_seconds = random.random() * max_sleep
#             print("Sleeping %f seconds and then retrying..." % sleep_seconds)
#             time.sleep(sleep_seconds)
#
#
# if __name__ == '__main__':
#     media_file = 'tmp/video2.mp4'
#     if not os.path.exists(media_file):
#         exit('Please specify the complete valid file location.')
#
#     flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)
#     credentials = flow.run_console()
#     youtube = build("youtube", "v3", credentials=credentials)
#     try:
#         initialize_upload(youtube)
#     except HttpError as er:
#         print("An HTTP error %d occurred:\n%s" % (er.resp.status, er.content))