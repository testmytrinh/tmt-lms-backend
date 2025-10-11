from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenVerifyView


from user.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenBlacklistView,
    UserViewSet,
)
from institution.views import DepartmentViewSet, TermViewSet
from courses.views import (
    CourseViewSet,
    CourseCategoryViewSet,
    CourseClassViewSet,
)
from enrollment.views import (
    EnrollmentViewSet,
)
from courseware.views import ContentNodeViewSet
from storage.views import FolderViewSet, FileViewSet

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="user")
router.register(r"deps", DepartmentViewSet, basename="department")
router.register(r"terms", TermViewSet, basename="term")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"categories", CourseCategoryViewSet, basename="course-category")
router.register(r"classes", CourseClassViewSet, basename="course-class")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(
    r"classes/(?P<class_id>\d+)/nodes",
    ContentNodeViewSet,
    basename="content-node",
)
router.register(r"folders", FolderViewSet, basename="folder")
router.register(r"files", FileViewSet, basename="file")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "api/token/blacklist/",
        CookieTokenBlacklistView.as_view(),
        name="token_blacklist",
    ),
    path("api/", include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
