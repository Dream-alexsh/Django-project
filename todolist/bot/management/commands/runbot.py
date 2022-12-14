import logging
import os
from datetime import datetime
from enum import IntEnum, auto

from django.core.management import BaseCommand

from bot.tg.client import TgClient
from pydantic import BaseModel

from todolist import settings
from bot.tg.models import Message
from bot.models import TgUser

from bot.tg.fsm.memory_storage import MemoryStorage

from goals.models import Goal, GoalCategory, BoardParticipant


logger = logging.getLogger(__name__)


class NewGoal(BaseModel):
    cat_id: int | None = None
    goal_title: str | None = None

    @property
    def is_completed(self) -> bool:
        return None not in (self.cat_id, self.goal_title)


class StateEnum(IntEnum):
    CREATE_CATEGORY_SELECT = auto()
    CHOSEN_CATEGORY = auto()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)
        self.storage = MemoryStorage()

    @staticmethod
    def _generate_verification_code() -> str:
        return os.urandom(12).hex()

    def handle_unverified_user(self, message: Message, tg_user: TgUser):
        code: str = self._generate_verification_code()
        tg_user.verification_code = code
        tg_user.save(update_fields=('verification_code',))
        self.tg_client.send_message(
            chat_id=message.chat.id,
            text=f'[verification_code] {tg_user.verification_code}'
        )

    def handle_goals_list(self, message: Message, tg_user: TgUser):
        resp_goals: list[str] = [
            f'#{goal.id} {goal.title}'
            for goal in Goal.objects.filter(user_id=tg_user.user_id).order_by('created')
        ]
        if resp_goals:
            self.tg_client.send_message(message.chat.id, '\n'.join(resp_goals))
        else:
            self.tg_client.send_message(message.chat.id, '[you have not any goals]')

    def handle_goal_categories_list(self, message: Message, tg_user: TgUser):
        resp_categories: list[str] = [
            f'#{cat.id}{cat.title}'
            for cat in GoalCategory.objects.filter(
                board__participants__user_id=tg_user.user_id,
                is_deleted=False
            )
        ]
        if resp_categories:
            self.tg_client.send_message(message.chat.id, 'Select Category \n' + '\n'.join(resp_categories))
        else:
            self.tg_client.send_message(message.chat.id, '[you have not any categories]')

    def handle_save_selected_category(self, message: Message, tg_user: TgUser):
        if message.text.isdigit():
            cat_id = int(message.text)
            if GoalCategory.objects.filter(
                board__participants__user_id=tg_user.user_id,
                board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                is_deleted=False,
                id=cat_id
            ).exists():
                self.storage.update_data(chat_id=message.chat.id, cat_id=cat_id)
                self.tg_client.send_message(message.chat.id, '[set title]')
                self.storage.set_state(message.chat.id, state=StateEnum.CHOSEN_CATEGORY)
            else:
                self.tg_client.send_message(message.chat.id, '[Category does not exist]')
        else:
            self.tg_client.send_message(message.chat.id, '[Invalid category id]')

    def handle_save_new_cat(self, message: Message, tg_user: TgUser):
        goal = NewGoal(**self.storage.get_data(tg_user.chat_id))
        goal.goal_title = message.text
        if goal.is_completed:
            Goal.objects.create(
                title=goal.goal_title,
                category_id=goal.cat_id,
                user_id=tg_user.user_id,
                due_date=datetime.now()
            )
            self.tg_client.send_message(message.chat.id, '[Goal is created]')
        else:
            logger.warning('Invalid state: %s')
            self.tg_client.send_message(message.chat.id, '[Something went wrong]')
        self.storage.reset(tg_user.chat_id)

    def handle_verified_user(self, message: Message, tg_user: TgUser):
        if message.text == '/goals':
            self.handle_goals_list(message, tg_user)

        elif message.text == '/create':
            self.handle_goal_categories_list(message, tg_user)
            self.storage.set_state(message.chat.id, state=StateEnum.CREATE_CATEGORY_SELECT)
            self.storage.set_data(message.chat.id, data=NewGoal().dict())

        elif message.text == '/cancel' and self.storage.get_state(tg_user.chat_id):
            self.storage.reset(tg_user.chat_id)
            self.tg_client.send_message(message.chat.id, '[canceled]')

        elif state := self.storage.get_state(tg_user.chat_id):
            match state:
                case StateEnum.CREATE_CATEGORY_SELECT:
                    self.handle_save_selected_category(message, tg_user)
                case StateEnum.CHOSEN_CATEGORY:
                    self.handle_save_new_cat(message, tg_user)
                case _:
                    logger.warning('Invalid state: %s', state)

        elif message.text.startswith('/'):
            self.tg_client.send_message(message.chat.id, '[unknown command]')

    def handle_message(self, message: Message):
        tg_user, _ = TgUser.objects.select_related('user').get_or_create(
            chat_id=message.chat.id,
            defaults={
                'username': message.from_.username
            }
        )
        if tg_user.user:
            self.handle_verified_user(message=message, tg_user=tg_user)
        else:
            self.handle_unverified_user(message=message, tg_user=tg_user)

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(message=item.message)

                # self.tg_client.send_message(chat_id=item.message.chat.id, text=item.message.text) echobot
                # print(item.message)
