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
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'title': 'Title',
        'feature_type': 'Feature Type',
        'published': 'Publish Date',
        'rate': 'Rate',
        'full_name': 'Payroll Name'
    }
