from pytest_factoryboy import register
from tests.factories import BoardFactory, UserFactory, CategoryFactory, BoardParticipantFactory, GoalFactory

pytest_plugins = "tests.fixtures"
register(BoardFactory)
register(UserFactory)
register(CategoryFactory)
register(BoardParticipantFactory)
register(GoalFactory)