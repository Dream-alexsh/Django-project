import pytest
from django.urls import reverse
from django.utils import timezone
from goals.models import Board, BoardParticipant
from goals.serializers import BoardSerializer


@pytest.mark.django_db
def test_create_board_success(client, current_user):
    client.force_login(user=current_user)

    data = {
        "title": "test_board",
    }
    response = client.post(
        data=data,
        path=reverse('create-boards'),
        content_type='application/json',
    )
    board = Board.objects.last()

    assert response.status_code == 201
    assert response.data == {
        "id": board.id,
        "created": timezone.localtime(board.created).isoformat(),
        "updated": timezone.localtime(board.updated).isoformat(),
        "title": "test_board",
        "is_deleted": False,
    }


@pytest.mark.django_db
def test_board_detail_view(client, current_board_participant):
    client.force_login(user=current_board_participant.user)
    board = current_board_participant.board

    expected_response = BoardSerializer(board).data

    response = client.get(path=f"/goals/board/{board.id}")

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_board_list_deleted(client, board_participant):
    board = board_participant.board
    board.is_deleted = True
    board.save()

    client.force_login(user=board_participant.user)

    response = client.get(path=reverse('list-boards'))

    assert response.status_code == 200
    assert response.data == []
