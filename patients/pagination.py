from rest_framework.pagination import PageNumberPagination
from django.conf import settings

class CustomPatientPagination(PageNumberPagination):
    """
    Standard pagination for patients registry.
    Configured to return 10 patients per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_data = super().paginate_queryset(queryset, request, view)
        if page_data is None:
            return None

        # Issue 2 — Slicing bug in challenge mode:
        # Drops the last item of the 10-item page, returning only 9 items and skipping the 10th patient.
        if getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
            if len(page_data) == self.page_size:
                return page_data[:-1]

        return page_data
