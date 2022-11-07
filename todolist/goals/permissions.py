from rest_framework import permissions

from goals.models import BoardParticipant, GoalCategory, Goal, GoalComment


class BoardPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: GoalCategory):
        filters: dict = {'user': request.user, 'board': obj}
        if request.method not in permissions.SAFE_METHODS:
            filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**filters).exists()


class GoalCategoryPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: GoalCategory):
        filters: dict = {'user': request.user, 'board': obj.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**filters).exists()


class GoalPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Goal):
        filters: dict = {'user': request.user, 'board': obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class CommentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: GoalComment):
        return any((request.method in permissions.SAFE_METHODS,
                    obj.user_id == request.user.id,
                    ))