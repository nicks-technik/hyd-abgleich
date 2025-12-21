from django.core.management.base import BaseCommand
from hyd_balancing.context7 import Context7

class Command(BaseCommand):
    help = 'Test Context7 initialization'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Context7...')
        Context7.initialize()
        
        api_key = Context7.get_api_key()
        if api_key:
             self.stdout.write(self.style.SUCCESS(f'Context7 initialized successfully. API Key found: {api_key[:4]}...'))
        else:
             self.stdout.write(self.style.WARNING('Context7 initialized, but API Key is missing.'))
