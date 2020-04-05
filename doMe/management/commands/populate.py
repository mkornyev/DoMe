from django.core.management.base import BaseCommand
from doMe.models import *

# POPULATE SCRIPT

class Command(BaseCommand):
    args = '<this func takes no args>'
    help = 'Run this script to create a sample user.'

    def _create_users(self):
        user = User.objects.create_user(username='bj', password='bj', first_name='Bob', last_name='Jones', email='bj@bj.com')
        user.save() 

        homeList = List(isGlobal=True, title='Global List', description='See all your toDos here')
        homeList.save()

        item = Item(user=user, title='Add a new goal!', description='And a goal description...')
        item.save()
        homeList.items.add(item)

        workspace = Workspace(organization='Home', description='Your private workspace.', admin=user)
        workspace.save()
        workspace.members.add(user) 
        workspace.lists.all(homeList)

        print("\nBob Jones User, Workspace, and List created: (User: bj | Pass: bj)\n")

    def handle(self, *args, **options):
        self._create_users()