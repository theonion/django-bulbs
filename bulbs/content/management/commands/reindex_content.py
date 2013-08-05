from django.core.management.base import NoArgsCommand
from bulbs.content.models import Content, Tag


class Command(NoArgsCommand):
    help = 'Runs index on all Content and Tag instances.'

    def handle(self, **options):
        chunk_size = 100
        for klass in (Content, Tag):
            num_processed = 0
            instance_count = klass.objects.all().count()       
            while num_processed < instance_count:
                for instance in klass.objects.all().order_by('id')[num_processed:num_processed + chunk_size]:
                    instance.index()
                    num_processed += 1
                    if not num_processed % 100:
                        print 'Processed %d %s items' % (
                            num_processed, klass.__name__
                        )
