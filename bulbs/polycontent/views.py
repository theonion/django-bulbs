from django.views.generic import DetailView, ListView
from .models import Content


class ContentDetailView(DetailView):
	model = Content


class ContentListView(ListView):
	model = Content


content_detail = ContentDetailView.as_view()
content_list = ContentListView.as_view()

