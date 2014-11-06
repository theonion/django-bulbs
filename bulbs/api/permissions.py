from rest_framework import permissions


class HasPermissionOrIsAuthor(permissions.BasePermission):
    authors_field = "authors"
    require_staff = True
    permissions = []  # permissions which would permit a non-author to do this
    author_permissions = []  # permissions the author needs in order to be permitted
    protected_methods = []

    def has_object_permission(self, request, view, obj):
        """determines if requesting user has permissions for the object

        :param request: WSGI request object - where we get the user from
        :param view: the view calling for permission
        :param obj: the object in question
        :return: `bool`
        """
        # Give permission if we're not protecting this method
        if self.protected_methods and not request.method in self.protected_methods:
            return True

        user = getattr(request, "user", None)

        if not user or user.is_anonymous():
            return False

        if self.require_staff and not user.is_staff:
            return False

        # if they have higher-level privileges we can return true right now
        if user.has_perms(self.permissions):
            return True

        # no? ok maybe they're the author and have appropriate author permissions.
        authors_field = getattr(obj, self.authors_field, None)

        if not authors_field:
            return False

        if self.author_permissions and not user.has_perms(self.author_permissions):
            return False

        return user in authors_field.all()


class CanEditContent(HasPermissionOrIsAuthor):
    """
    extends `HasPermissionOrIsAuthor` and protects PUT method
    """

    permissions = ["content.change_content"]
    protected_methods = ["PUT"]


class CanPromoteContent(HasPermissionOrIsAuthor):
    """
    extends `HasPermissionOrIsAuthor` and ensures user has promotion rights
    """

    permissions = ["content.promote_content"]


class CanPublishContent(HasPermissionOrIsAuthor):
    """
    extends `HasPermissionOrIsAuthor` and ensures user has publishing rights
    """

    permissions = ["content.publish_content"]
    author_permissions = ["content.publish_own_content"]


class CanEditCmsNotifications(permissions.BasePermission):
    """
    permission class to handle CMS rights
    """

    def has_permission(self, request, view):
        """If method is GET, user can access, if method is PUT or POST user must be a superuser.
        """
        has_permission = False
        if request.method == "GET" \
                or request.method in ["PUT", "POST", "DELETE"] \
                and request.user and request.user.is_superuser:
            has_permission = True
        return has_permission
