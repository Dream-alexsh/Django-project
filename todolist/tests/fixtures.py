import pytest
from goals.models import Goal, BoardParticipant, Board, GoalCategory

from tests.factories import UserFactory, CategoryFactory, BoardParticipantFactory, GoalFactory, \
    BoardFactory


@pytest.fixture()
def current_user(user):
    return user


@pytest.fixture()
def current_board_participant(board_participant):
    return board_participant


@pytest.fixture()
def current_user_board(current_board_participant):
    board = current_board_participant.board
    return board


@pytest.fixture()
def current_user_category(current_board_participant):
    user_category = CategoryFactory(board=current_board_participant.board, user=current_board_participant.user)
    goal = GoalFactory(category=user_category, user=current_board_participant.user)

    return user_category


@pytest.fixture()
def current_user_goal(current_user_category, current_board_participant):
    goal = GoalFactory(category=current_user_category, user=current_board_participant.user)
    return goal


@pytest.fixture()
def current_user_goals(current_board_participant, current_user_category):
    user = current_board_participant.user
    GoalFactory.create_batch(size=4, user=user, category=current_user_category)

    return Goal.objects.all()


@pytest.fixture()
def current_user_categories(board_participant):
    CategoryFactory.create_batch(
        size=4,
        user=board_participant.user,
        board=board_participant.board,
    )
    return GoalCategory.objects.all()


@pytest.fixture()
def current_user_boards(current_board_participant):
    current_user = current_board_participant.user
    boards = BoardFactory.create_batch(size=4)

    for board in boards:
        BoardParticipantFactory(user=current_user, board=board)

    return Board.objects.all()
