from django.urls import path
from . import apis

urlpatterns = [
    path('', apis.ProductListApi.as_view(), name='list'),
    path('start-parsing/', apis.ProductStartParsingApi.as_view(), name='start-parsing'),
]