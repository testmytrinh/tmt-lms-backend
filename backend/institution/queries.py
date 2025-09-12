from .models import Department, Term


def get_all_departments():
    return Department.objects.all()


def get_all_terms():
    return Term.objects.all()
