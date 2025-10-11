from .models import Folder, File


def get_all_folders():
    return Folder.objects.all()


def get_all_files():
    return File.objects.all()


def get_folders_by_owner(user):
    return Folder.objects.filter(owner=user)


def get_files_by_owner(user):
    return File.objects.filter(owner=user)


def get_root_files_by_owner(user):
    return File.objects.filter(owner=user, folder__isnull=True)


def get_root_folders_by_owner(user):
    return Folder.objects.filter(owner=user, parent__isnull=True)
