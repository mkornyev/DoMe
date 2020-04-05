from django.core.management.base import BaseCommand
from doMe.models import *

# DROP SCRIPT

class Command(BaseCommand):
    args = '<this func takes no args>'
    help = 'Run this script to drop the database.'

    def _destroy_users(self):
        users = User.objects.all()
        size = len(users)

        for u in users:
            u.delete() 

        print("\nAll users deleted: {}\n".format(size))

    def handle(self, *args, **options):
        self._destroy_users()