import json

from django.core.management.base import BaseCommand

from user.models import User, Role


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        # parser.add_argument("poll_ids", nargs="+", type=int)
        pass

    def handle(self, *args, **options):
        with open("./seed/data/users.json", "r") as f:
            users = json.load(f)
        for user in users:
            User.objects.create(**user)