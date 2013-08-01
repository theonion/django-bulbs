from django.core.management.base import NoArgsCommand
from bulbs.content.models import Content


class Command(NoArgsCommand):
    help = 'Runs Content.index on all content.'

    def handle(self, **options):
        num_processed = 0
        content_count = Content.objects.all().count()
        chunk_size = 10
        while num_processed < content_count:
            for content in Content.objects.all()[num_processed:num_processed + chunk_size]:
                content.index()
                num_processed += 1
                if not num_processed % 100:
                    print 'Processed %d content items' % num_processed

