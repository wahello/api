import os
import channels.asgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'pashinin.settings'
channel_layer = channels.asgi.get_channel_layer()
