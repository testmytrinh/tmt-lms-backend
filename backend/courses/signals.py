from openfga_sdk.client.models import ClientTuple, ClientWriteRequest
from django.db.models.signals import pre_save
from django.dispatch import receiver

from proxies.openfga.sync import client
from proxies.openfga.relations import CourseClass

from .models import Enrollment, EnrollmentRole


ENROLLMENT_ROLE_TO_COURSE_CLASS = {
    EnrollmentRole.TEACHER: CourseClass.TEACHER,
    EnrollmentRole.STUDENT: CourseClass.STUDENT,
    EnrollmentRole.GUEST: CourseClass.GUEST,
}


@receiver(pre_save, sender=Enrollment)
def sync_enrollment_to_openfga(sender, instance, **kwargs):
    # first creation
    if instance.pk is None:
        body = ClientWriteRequest(
            writes=[
                ClientTuple(
                    user_id=instance.user.id,
                    relation=ENROLLMENT_ROLE_TO_COURSE_CLASS[instance.role],
                    object_id=instance.course_class.id,
                )
            ]
        )
        return client.write(body)
