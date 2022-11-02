from rest_framework import serializers
from goals.models import GoalCategory, Goal, GoalComment

from core.serializers import ProfileSerializer
from rest_framework.exceptions import PermissionDenied


class GoalCreateCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")

    def validate_category(self, value):
        if self.context['request'].user != value.user:
            raise PermissionDenied
        return value


class GoalSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")

    def validate_category(self, value):
        if self.context['request'].user != value.user:
            raise PermissionDenied
        return value
    

class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")


class GoalCommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user", "goal")