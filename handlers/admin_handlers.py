from aiogram import Bot, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import Command
from aiogram.types import Message

from config_data.config import load_config
from services.admin_service import AdminService

router = Router()
config = load_config()


def ensure_chat_context(message: Message):
    AdminService.ensure_chat(
        chat_id=message.chat.id,
        title=message.chat.title or getattr(message.chat, 'full_name', None),
        chat_type=message.chat.type,
        added_by_user_id=message.from_user.id if message.from_user else None,
    )


def get_target_user_id(message: Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return None

    raw_value = parts[1].strip()
    if raw_value.startswith("@"):
        return None

    try:
        return int(raw_value)
    except ValueError:
        return None


async def is_chat_manager(message: Message, bot: Bot) -> bool:
    user_id = message.from_user.id
    if user_id in config.tg_bot.admin_ids:
        return True

    if AdminService.is_chat_admin(message.chat.id, user_id):
        return True

    if message.chat.type == ChatType.PRIVATE:
        return True

    member = await bot.get_chat_member(message.chat.id, user_id)
    return member.status in {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR}


def is_group_chat(message: Message) -> bool:
    return AdminService.is_group_chat(message.chat.type)


async def ensure_group_manager(message: Message, bot: Bot) -> bool:
    ensure_chat_context(message)

    if not is_group_chat(message):
        await message.answer("Эта команда работает только в группе или супергруппе.")
        return False

    if not await is_chat_manager(message, bot):
        await message.answer("Эта команда доступна только администраторам группы или супер-админам бота.")
        return False

    return True


@router.message(Command(commands='setup_chat'))
async def setup_chat(message: Message, bot: Bot):
    if not await ensure_group_manager(message, bot):
        return

    AdminService.enable_chat(message.chat.id)
    AdminService.add_chat_admin(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        added_by_user_id=message.from_user.id,
        role='owner',
    )
    await message.answer(
        "Чат зарегистрирован и включён. Теперь бот ведёт учёт отдельно для этой группы, "
        "а ты добавлен как владелец админки этого чата."
    )


@router.message(Command(commands='disable_chat'))
async def disable_chat(message: Message, bot: Bot):
    if not await ensure_group_manager(message, bot):
        return

    AdminService.disable_chat(message.chat.id)
    await message.answer("Чат отключён. Учёт и команды в этой группе временно остановлены до /setup_chat.")


@router.message(Command(commands='chat_admins'))
async def list_chat_admins(message: Message, bot: Bot):
    if not await ensure_group_manager(message, bot):
        return

    admins = AdminService.list_chat_admins(message.chat.id)
    if not admins:
        await message.answer(
            "Для этого чата ещё не назначены админы бота. "
            "Используй /setup_chat или /add_admin в ответ на сообщение пользователя."
        )
        return

    lines = [f"- `{user_id}`: {role}" for user_id, role in admins]
    await message.answer("Админы этого чата:\n" + "\n".join(lines), parse_mode='Markdown')


@router.message(Command(commands='add_admin'))
async def add_admin(message: Message, bot: Bot):
    if not await ensure_group_manager(message, bot):
        return

    target_user_id = get_target_user_id(message)
    if target_user_id is None:
        await message.answer(
            "Используй /add_admin в ответ на сообщение пользователя или передай numeric Telegram user id: "
            "/add_admin 123456789"
        )
        return

    AdminService.add_chat_admin(
        chat_id=message.chat.id,
        user_id=target_user_id,
        added_by_user_id=message.from_user.id,
    )
    await message.answer(f"Пользователь `{target_user_id}` добавлен в админы чата.", parse_mode='Markdown')


@router.message(Command(commands='remove_admin'))
async def remove_admin(message: Message, bot: Bot):
    if not await ensure_group_manager(message, bot):
        return

    target_user_id = get_target_user_id(message)
    if target_user_id is None:
        await message.answer(
            "Используй /remove_admin в ответ на сообщение пользователя или передай numeric Telegram user id: "
            "/remove_admin 123456789"
        )
        return

    if target_user_id == message.from_user.id and message.from_user.id not in config.tg_bot.admin_ids:
        await message.answer("Снять с себя права этой командой нельзя. Сначала назначь другого админа чата.")
        return

    AdminService.remove_chat_admin(message.chat.id, target_user_id)
    await message.answer(f"Пользователь `{target_user_id}` удалён из админов чата.", parse_mode='Markdown')


@router.message(Command(commands='chat_info'))
async def chat_info(message: Message, bot: Bot):
    if not await ensure_group_manager(message, bot):
        return

    admins = AdminService.list_chat_admins(message.chat.id)
    is_enabled = AdminService.is_chat_enabled(message.chat.id)
    await message.answer(
        "\n".join(
            [
                f"chat_id: `{message.chat.id}`",
                f"type: `{message.chat.type}`",
                f"title: {message.chat.title or getattr(message.chat, 'full_name', None) or 'private'}",
                f"status: `{'enabled' if is_enabled else 'disabled'}`",
                f"bot_admins: `{len(admins)}`",
            ]
        ),
        parse_mode='Markdown',
    )
