from bulbs.content.views import ContentListView


class AdminListView(ContentListView):

    template_name = "cms/list.html"

    def render_to_response(self, context, **response_kwargs):
        return super(AdminListView, self).render_to_response(context, **response_kwargs)
