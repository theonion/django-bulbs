from rest_framework_csv.renderers import CSVRenderer


class HeaderCSVRenderer(CSVRenderer):

    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super(HeaderCSVRenderer, self).render(
            data, media_type=media_type, renderer_context=renderer_context
        )

    def tablize(self, data):
        """
        rest_framework_csv doesn't let us easily set headers.
        So this will by defining the header_fields attribute.
        """
        table = super(HeaderCSVRenderer, self).tablize(data)
        if self.header_fields and table:
            header_row = []
            for key in table[0]:
                header_row.append(self.header_fields.get(key, key))
            table[0] = header_row
        return table


class ContributionReportingRenderer(HeaderCSVRenderer):

    header_fields = {
        'id': 'Content ID',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'title': 'Title',
        'feature_type': 'Feature Type',
        'published': 'Publish Date',
        'rate': 'Rate',
        'full_name': 'Payroll Name'
    }
