from bulbs.content.views import ContentListView


content_list = ContentListView.as_view(template_name='testapp/content_list.html')

