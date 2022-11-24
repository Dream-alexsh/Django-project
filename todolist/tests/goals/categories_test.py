import pytest
from django.urls import reverse
from django.utils import timezone

from goals.models import GoalCategory, BoardParticipant, Goal

from goals.serializers import GoalCategorySerializer
from rest_framework.exceptions import ErrorDetail

from core.serializers import ProfileSerializer


@pytest.mark.django_db
def test_category_auth_required(client):
    response = client.post(reverse('create-category'))
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_category_success(client, board_participant):
    user = board_participant.user
    board = board_participant.board
    client.force_login(user=user)

    data = {
        "title": "test_category",
        "board": board.id,
    }

    response = client.post(
        path=reverse('create-category'),
        data=data,
        content_type='application/json',
    )

    category = GoalCategory.objects.last()

    assert response.status_code == 201
    assert response.data == {
        "id": category.id,
        "created": timezone.localtime(category.created).isoformat(),
        "updated": timezone.localtime(category.updated).isoformat(),
        "title": "test_category",
        "is_deleted": False,
        "board": board.id,
    }


@pytest.mark.django_db
def test_category_list_success(client, current_board_participant, current_user_categories):
    user = current_board_participant.user
    client.force_login(user=user)

    response = client.get(path=reverse('list-category'))
    categories = current_user_categories.order_by('title')

    assert response.status_code == 200
    assert response.data == GoalCategorySerializer(categories, many=True).data


@pytest.mark.django_db
def test_category_list_unauthorised(client):
    response = client.get(path=reverse('list-category'))

    assert response.status_code == 403
    assert response.data == {'detail': ErrorDetail(
        string='Authentication credentials were not provided.',
        code='not_authenticated')}


@pytest.mark.django_db
def test_category_list_reader(client, current_board_participant, current_user_categories):
    current_board_participant.role = BoardParticipant.Role.reader
    current_board_participant.save()

    user = current_board_participant.user
    client.force_login(user=user)

    response = client.get(path=reverse('list-category'))
    goals = current_user_categories.order_by('title')

    assert response.status_code == 200
    assert response.data == GoalCategorySerializer(goals, many=True).data


@pytest.mark.django_db
def test_category_list_writer(client, current_board_participant, current_user_categories):
    current_board_participant.role = BoardParticipant.Role.writer
    current_board_participant.save()

    user = current_board_participant.user
    client.force_login(user=user)

    response = client.get(path=reverse('list-category'))
    goals = current_user_categories.order_by('title')

    assert response.status_code == 200
    assert response.data == GoalCategorySerializer(goals, many=True).data


@pytest.mark.django_db
def test_category_retrieve_view(client, current_board_participant, current_user_category):
    client.force_login(user=current_board_participant.user)

    expected_response = GoalCategorySerializer(current_user_category).data

    response = client.get(path=f"/goals/goal_category/{current_user_category.id}")

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_category_update_view(client, current_board_participant, current_user_category):
    client.force_login(user=current_board_participant.user)

    data = {'title': 'test'}

    response = client.patch(
        path=f"/goals/goal_category/{current_user_category.id}",
        data=data,
        content_type='application/json',
    )
    category = GoalCategory.objects.latest('updated')

    assert response.status_code == 200
    assert response.data == {
        "id": category.id,
        "user": ProfileSerializer(current_user_category.user).data,
        "created": timezone.localtime(category.created).isoformat(),
        "updated": timezone.localtime(category.updated).isoformat(),
        "title": "test",
        "is_deleted": current_user_category.is_deleted,
        "board": current_user_category.board.id
    }


@pytest.mark.django_db
def test_category_destroy_view(client, current_board_participant, current_user_category):
    client.force_login(user=current_board_participant.user)

    response = client.delete(
        path=f"/goals/goal_category/{current_user_category.id}",
    )

    category = GoalCategory.objects.latest('updated')
    goal = Goal.objects.get(category=category)

    assert response.status_code == 204
    assert category.is_deleted is True
    assert goal.status == Goal.Status.archived
