from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print the given string'

    def add_arguments(self, parser):
        parser.add_argument('string', nargs='+', type=str)

    def handle(self, *args, **options):
        for string in options['string']:
            self.stdout.write(self.style.SUCCESS('Successfully printing "%s"' % string))
