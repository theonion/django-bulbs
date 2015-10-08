from rest_framework_csv.renderers import CSVRenderer


class HeaderCSVRenderer(CSVRenderer):

    def tablize(self, data):
        """
        rest_framework_csv doesn't let us easily set headers.
        So this will by defining the header_fields attribute.
        """
        table = super(HeaderCSVRenderer, self).tablize(data)
        if self.header_fields:
            header_row = []
            for key in table[0]:
                header_row.append(self.header_fields.get(key, key))
            table[0] = header_row
        return table


class ContributionReportingRenderer(HeaderCSVRenderer):

    header_fields = {
        'content.content_type': 'Content Type',
        'content.feature_type': 'Feature Type',
        'content.id': 'Content Id',
        'content.published': 'Published',
        'content.title': 'Title',
        'content.url': 'URL',
        'id': 'Id',
        'notes': 'Notes',
        'pay': 'Pay',
        'rate': 'Rate',
        'role': 'Role',
        'user.full_name': 'Full Name',
        'user.id': 'User Id',
        'user.username': 'Username'
    }
