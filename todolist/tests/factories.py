import factory.fuzzy
from django.utils import timezone
from datetime import datetime
from dateutil.tz import UTC

from goals.models import Board, GoalCategory, BoardParticipant, Goal, GoalComment

from core.models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    first_name = "Alexey"
    last_name = "Petrov"
    username = factory.Sequence(lambda n: 'user%d' % n)


class BoardFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Board

    title = factory.fuzzy.FuzzyText(length=15)
    is_deleted = False
    created = timezone.now()
    updated = timezone.now()


class CategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = GoalCategory

    title = factory.fuzzy.FuzzyText(length=15)
    is_deleted = False
    created = factory.fuzzy.FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC))
    updated = factory.fuzzy.FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC))
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)


class BoardParticipantFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = BoardParticipant

    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)
    role = BoardParticipant.Role.owner


class GoalFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Goal

    user = factory.SubFactory(UserFactory)
    title = factory.fuzzy.FuzzyText(length=15, prefix='test', suffix='goal')
    description = 'test'
    due_date = factory.fuzzy.FuzzyDateTime(datetime(2022, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC))
    status = factory.fuzzy.FuzzyChoice([Goal.Status.to_do, Goal.Status.in_progress, Goal.Status.done])
    priority = factory.fuzzy.FuzzyChoice([Goal.Priority.critical, Goal.Priority.low, Goal.Priority.medium, Goal.Priority.high])
    category = factory.SubFactory(CategoryFactory)
    created = factory.fuzzy.FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC))
    updated = factory.fuzzy.FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC))
