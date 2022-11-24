import pytest
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone

from goals.models import Goal, GoalCategory, Board, BoardParticipant

from core.models import User

from goals.serializers import GoalSerializer

from core.serializers import ProfileSerializer


@pytest.mark.django_db
def test_auth_required(client):
    response = client.post(reverse('create-goals'))
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_goal_success(client, current_board_participant, goal_category):
    user = current_board_participant.user
    client.force_login(user=user)

    data = {
        "title": "test_goal",
        "description": "test_goal",
        "category": goal_category.id,
    }
    response = client.post(
        path=reverse('create-goals'),
        data=data,
        content_type='application/json',
    )
    goal = Goal.objects.last()
    assert response.status_code == 201
    assert response.data == {
        "id": goal.id,
        "status": 1,
        "title": "test_goal",
        "description": "test_goal",
        "due_date": None,
        "category": goal_category.id,
        "priority": 2,
        "created": timezone.localtime(goal.created).isoformat(),
        "updated": timezone.localtime(goal.updated).isoformat(),
    }


@pytest.mark.django_db
def test_create_goal_reader_role(client, current_board_participant, goal_category):
    current_board_participant.user = User.objects.create(username='alex', password='qwerty123@')
    current_board_participant.role = BoardParticipant.Role.reader
    current_board_participant.save()

    client.force_login(user=current_board_participant.user)

    data = {
        "title": "test_goal",
        "description": "test_goal",
        "category": goal_category.id,
    }

    response = client.post(
        path=reverse('create-goals'),
        data=data,
        content_type='application/json',
    )

    assert response.status_code == 403
    assert response.data == {'detail': ErrorDetail(
        string='You do not have permission to perform this action.',
        code='permission_denied')
    }


@pytest.mark.django_db
def test_create_goal_writer_role(client, current_board_participant, goal_category):
    current_board_participant.role = BoardParticipant.Role.writer
    current_board_participant.save()

    client.force_login(user=current_board_participant.user)

    data = {
        "title": "test_goal",
        "description": "test_goal",
        "category": goal_category.id,
    }

    response = client.post(
        path=reverse('create-goals'),
        data=data,
        content_type='application/json',
    )

    goal = Goal.objects.last()

    assert response.status_code == 201
    assert response.data == {
        "id": goal.id,
        "status": 1,
        "title": "test_goal",
        "description": "test_goal",
        "due_date": None,
        "category": goal_category.id,
        "priority": 2,
        "created": timezone.localtime(goal.created).isoformat(),
        "updated": timezone.localtime(goal.updated).isoformat(),
    }


@pytest.mark.django_db
def test_goal_list_success(client, current_board_participant, current_user_goals):
    client.force_login(user=current_board_participant.user)
    goals = current_user_goals.order_by('title')

    goals = GoalSerializer(goals, many=True).data

    response = client.get(path=reverse('list-goals'))

    assert response.status_code == 200
    assert response.data == goals


@pytest.mark.django_db
def test_goal_list_reader(client, current_board_participant, current_user_goals):
    current_board_participant.role = BoardParticipant.Role.reader
    current_board_participant.save()

    user = current_board_participant.user
    client.force_login(user=user)

    response = client.get(path=reverse('list-goals'))
    goals = current_user_goals.order_by('title')

    goals = GoalSerializer(goals, many=True).data

    assert response.status_code == 200
    assert response.data == goals


@pytest.mark.django_db
def test_goal_list_writer(client, current_board_participant, current_user_goals):
    current_board_participant.role = BoardParticipant.Role.writer
    current_board_participant.save()

    client.force_login(user=current_board_participant.user)

    response = client.get(path=reverse('list-goals'))
    goals = current_user_goals.order_by('title')

    goals = GoalSerializer(goals, many=True).data

    assert response.status_code == 200
    assert response.data == goals


@pytest.mark.django_db
def test_goal_list_filter_by_status(client, current_board_participant, current_user_goals):
    client.force_login(user=current_board_participant.user)

    status_queries = ['1', '1,2', '1,2,3']

    for query in status_queries:
        response = client.get(path=f"/goals/goal/list?status__in={query}")
        all_goals = current_user_goals.filter(status__in=query.split(',')).order_by('title')
        all_goals = GoalSerializer(all_goals, many=True).data
        assert response.status_code == 200
        assert response.data == all_goals


@pytest.mark.django_db
def test_goal_retrieve_view(client, current_board_participant, current_user_goal):
    client.force_login(user=current_board_participant.user)

    expected_response = GoalSerializer(current_user_goal).data

    response = client.get(path=f"/goals/goal/{current_user_goal.id}")

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_goal_destroy_view(client, current_board_participant, current_user_goal):
    client.force_login(user=current_board_participant.user)

    response = client.delete(
        path=f"/goals/goal/{current_user_goal.id}",
    )

    goal = Goal.objects.get(id=current_user_goal.id)

    assert response.status_code == 204
    assert goal.status == Goal.Status.archived
