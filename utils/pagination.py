from rest_framework.pagination import CursorPagination

class GlobalIdCursorPagination(CursorPagination):
    page_size = 10  
    ordering = '-id'  
    cursor_query_param = 'cursor'  ##query parameter name for cursor

class RideSearchPagination(CursorPagination):
    page_size = 7
    ordering = '-id'
    cursor_query_param = 'cursor'