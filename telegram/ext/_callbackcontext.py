#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
# pylint: disable=no-self-use
"""This module contains the CallbackContext class."""
from asyncio import Queue
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Match,
    NoReturn,
    Optional,
    Tuple,
    Generic,
    Type,
    Coroutine,
)

from telegram import Update, CallbackQuery
from telegram.ext import ExtBot
from telegram.ext._utils.types import UD, CD, BD, BT, JQ  # pylint: disable=unused-import

if TYPE_CHECKING:
    from telegram.ext import Application, Job, JobQueue
    from telegram.ext._utils.types import CCT

_STORING_DATA_WIKI = (
    "https://github.com/python-telegram-bot/python-telegram-bot"
    "/wiki/Storing-bot%2C-user-and-chat-related-data"
)


class CallbackContext(Generic[BT, UD, CD, BD]):
    """
    This is a context object passed to the callback called by :class:`telegram.ext.Handler`
    or by the :class:`telegram.ext.Application` in an error handler added by
    :attr:`telegram.ext.Application.add_error_handler` or to the callback of a
    :class:`telegram.ext.Job`.

    Note:
        :class:`telegram.ext.Application` will create a single context for an entire update. This
        means that if you got 2 handlers in different groups and they both get called, they will
        get passed the same `CallbackContext` object (of course with proper attributes like
        `.matches` differing). This allows you to add custom attributes in a lower handler group
        callback, and then subsequently access those attributes in a higher handler group callback.
        Note that the attributes on `CallbackContext` might change in the future, so make sure to
        use a fairly unique name for the attributes.

    Warning:
         Do not combine custom attributes with :paramref:`telegram.ext.Handler.block` set to
         :obj:`False` or :paramref:`telegram.ext.Application.concurrent_updates` set to
         :obj:`True`. Due to how those work, it will almost certainly execute the callbacks for an
         update out of order, and the attributes that you think you added will not be present.

    Args:
        application (:class:`telegram.ext.Application`): The application associated with this
            context.

    Attributes:
        matches (List[:meth:`re.Match <re.Match.expand>`]): Optional. If the associated update
            originated from
            a :class:`filters.Regex`, this will contain a list of match objects for every pattern
            where ``re.search(pattern, string)`` returned a match. Note that filters short circuit,
            so combined regex filters will not always be evaluated.
        args (List[:obj:`str`]): Optional. Arguments passed to a command if the associated update
            is handled by :class:`telegram.ext.CommandHandler`, :class:`telegram.ext.PrefixHandler`
            or :class:`telegram.ext.StringCommandHandler`. It contains a list of the words in the
            text after the command, using any whitespace string as a delimiter.
        error (:obj:`Exception`): Optional. The error that was raised. Only present when passed
            to a error handler registered with :attr:`telegram.ext.Application.add_error_handler`.
        job (:class:`telegram.ext.Job`): Optional. The job which originated this callback.
            Only present when passed to the callback of :class:`telegram.ext.Job` or in error
            handlers if the error is caused by a job.

            .. versionchanged:: 14.0
                :attr:`job` is now also present in error handlers if the error is caused by a job.

    """

    if TYPE_CHECKING:
        DEFAULT_TYPE = CallbackContext[  # type: ignore[misc]  # noqa: F821
            ExtBot, Dict, Dict, Dict
        ]
    else:
        # Somewhat silly workaround so that accessing the attribute
        # doesn't only work while type checking
        DEFAULT_TYPE = 'CallbackContext[ExtBot, Dict, Dict, Dict]'  # pylint: disable-all
        """Shortcut for the type annotation for the `context` argument that's correct for the
        default settings, i.e. if :class:`telegram.ext.ContextTypes` is not used.

        Example:
            .. code:: python

                def callback(update: Update, context: CallbackContext.DEFAULT_TYPE):
                    ...

        .. versionadded: 14.0
        """

    __slots__ = (
        '_application',
        '_chat_id_and_data',
        '_user_id_and_data',
        'args',
        'matches',
        'error',
        'job',
        'coroutine',
        '__dict__',
    )

    def __init__(self: 'CCT', application: 'Application[BT, CCT, UD, CD, BD, JQ]'):
        """
        Args:
            application (:class:`telegram.ext.Application`):
        """
        self._application = application
        self._chat_id_and_data: Optional[Tuple[int, CD]] = None
        self._user_id_and_data: Optional[Tuple[int, UD]] = None
        self.args: Optional[List[str]] = None
        self.matches: Optional[List[Match]] = None
        self.error: Optional[Exception] = None
        self.job: Optional['Job'] = None
        self.coroutine: Optional[Coroutine] = None

    @property
    def application(self) -> 'Application[BT, CCT, UD, CD, BD, JQ]':
        """:class:`telegram.ext.Application`: The application associated with this context."""
        return self._application

    @property
    def bot_data(self) -> BD:
        """:obj:`dict`: Optional. A dict that can be used to keep any data in. For each
        update it will be the same ``dict``.
        """
        return self.application.bot_data

    @bot_data.setter
    def bot_data(self, value: object) -> NoReturn:
        raise AttributeError(
            f"You can not assign a new value to bot_data, see {_STORING_DATA_WIKI}"
        )

    @property
    def chat_data(self) -> Optional[CD]:
        """:obj:`dict`: Optional. A dict that can be used to keep any data in. For each
        update from the same chat id it will be the same ``dict``.

        Warning:
            When a group chat migrates to a supergroup, its chat id will change and the
            ``chat_data`` needs to be transferred. For details see our `wiki page
            <https://github.com/python-telegram-bot/python-telegram-bot/wiki/
            Storing-bot,-user-and-chat-related-data#chat-migration>`_.
        """
        if self._chat_id_and_data:
            return self._chat_id_and_data[1]
        return None

    @chat_data.setter
    def chat_data(self, value: object) -> NoReturn:
        raise AttributeError(
            f"You can not assign a new value to chat_data, see {_STORING_DATA_WIKI}"
        )

    @property
    def user_data(self) -> Optional[UD]:
        """:obj:`dict`: Optional. A dict that can be used to keep any data in. For each
        update from the same user it will be the same ``dict``.
        """
        if self._user_id_and_data:
            return self._user_id_and_data[1]
        return None

    @user_data.setter
    def user_data(self, value: object) -> NoReturn:
        raise AttributeError(
            f"You can not assign a new value to user_data, see {_STORING_DATA_WIKI}"
        )

    async def refresh_data(self) -> None:
        """If :attr:`application` uses persistence, calls
        :meth:`telegram.ext.BasePersistence.refresh_bot_data` on :attr:`bot_data`,
        :meth:`telegram.ext.BasePersistence.refresh_chat_data` on :attr:`chat_data` and
        :meth:`telegram.ext.BasePersistence.refresh_user_data` on :attr:`user_data`, if
        appropriate.

        Will be called by :meth:`telegram.ext.Application.process_update` and
        :meth:`telegram.ext.Job.run`.

        .. versionadded:: 13.6
        """
        if self.application.persistence:
            if self.application.persistence.store_data.bot_data:
                await self.application.persistence.refresh_bot_data(self.bot_data)
            if (
                self.application.persistence.store_data.chat_data
                and self._chat_id_and_data is not None
            ):
                await self.application.persistence.refresh_chat_data(*self._chat_id_and_data)
            if (
                self.application.persistence.store_data.user_data
                and self._user_id_and_data is not None
            ):
                await self.application.persistence.refresh_user_data(*self._user_id_and_data)

    def drop_callback_data(self, callback_query: CallbackQuery) -> None:
        """
        Deletes the cached data for the specified callback query.

        .. versionadded:: 13.6

        Note:
            Will *not* raise exceptions in case the data is not found in the cache.
            *Will* raise :class:`KeyError` in case the callback query can not be found in the
            cache.

        Args:
            callback_query (:class:`telegram.CallbackQuery`): The callback query.

        Raises:
            KeyError | RuntimeError: :class:`KeyError`, if the callback query can not be found in
                the cache and :class:`RuntimeError`, if the bot doesn't allow for arbitrary
                callback data.
        """
        if isinstance(self.bot, ExtBot):
            if not self.bot.arbitrary_callback_data:
                raise RuntimeError(
                    'This telegram.ext.ExtBot instance does not use arbitrary callback data.'
                )
            self.bot.callback_data_cache.drop_data(callback_query)
        else:
            raise RuntimeError('telegram.Bot does not allow for arbitrary callback data.')

    @classmethod
    def from_error(
        cls: Type['CCT'],
        update: object,
        error: Exception,
        application: 'Application[BT, CCT, UD, CD, BD, JQ]',
        job: 'Job' = None,
        coroutine: Coroutine = None,
    ) -> 'CCT':
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to the error
        handlers.

        .. seealso:: :meth:`telegram.ext.Application.add_error_handler`

        .. versionchanged:: 14.0
            Removed arguments ``async_args`` and ``async_kwargs``.

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update associated with the
                error. May be :obj:`None`, e.g. for errors in job callbacks.
            error (:obj:`Exception`): The error.
            application (:class:`telegram.ext.Application`): The application associated with this
                context.
            job (:class:`telegram.ext.Job`, optional): The job associated with the error.

                .. versionadded:: 14.0

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls.from_update(update, application)
        self.error = error
        self.coroutine = coroutine
        self.job = job
        return self

    @classmethod
    def from_update(
        cls: Type['CCT'],
        update: object,
        application: 'Application[BT, CCT, UD, CD, BD, JQ]',
    ) -> 'CCT':
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to the
        handlers.

        .. seealso:: :meth:`telegram.ext.Application.add_handler`

        Args:
            update (:obj:`object` | :class:`telegram.Update`): The update.
            application (:class:`telegram.ext.Application`): The application associated with this
                context.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls(application)  # type: ignore[arg-type]

        if update is not None and isinstance(update, Update):
            chat = update.effective_chat
            user = update.effective_user

            if chat:
                self._chat_id_and_data = (
                    chat.id,
                    application.chat_data[chat.id],  # pylint: disable=protected-access
                )
            if user:
                self._user_id_and_data = (
                    user.id,
                    application.user_data[user.id],  # pylint: disable=protected-access
                )
        return self

    @classmethod
    def from_job(
        cls: Type['CCT'],
        job: 'Job',
        application: 'Application[BT, CCT, UD, CD, BD, JQ]',
    ) -> 'CCT':
        """
        Constructs an instance of :class:`telegram.ext.CallbackContext` to be passed to a
        job callback.

        .. seealso:: :meth:`telegram.ext.JobQueue`

        Args:
            job (:class:`telegram.ext.Job`): The job.
            application (:class:`telegram.ext.Application`): The application associated with this
                context.

        Returns:
            :class:`telegram.ext.CallbackContext`
        """
        self = cls(application)  # type: ignore[arg-type]
        self.job = job

        if job.chat_id:
            self._chat_id_and_data = (
                job.chat_id,
                application.chat_data[job.chat_id],  # pylint: disable=protected-access
            )
        if job.user_id:
            self._user_id_and_data = (
                job.user_id,
                application.user_data[job.user_id],  # pylint: disable=protected-access
            )
        return self

    def update(self, data: Dict[str, object]) -> None:
        """Updates ``self.__slots__`` with the passed data.

        Args:
            data (Dict[:obj:`str`, :obj:`object`]): The data.
        """
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def bot(self) -> BT:
        """:class:`telegram.Bot`: The bot associated with this context."""
        return self._application.bot

    @property
    def job_queue(self) -> Optional['JobQueue']:
        """
        :class:`telegram.ext.JobQueue`: The ``JobQueue`` used by the
            :class:`telegram.ext.Application` and (usually) the :class:`telegram.ext.Updater`
            associated with this context.

        """
        return self._application.job_queue

    @property
    def update_queue(self) -> 'Queue[object]':
        """
        :class:`asyncio.Queue`: The ``Queue`` instance used by the
            :class:`telegram.ext.Application` and (usually) the :class:`telegram.ext.Updater`
            associated with this context.

        """
        return self._application.update_queue

    @property
    def match(self) -> Optional[Match[str]]:
        """
        `Regex match type`: The first match from :attr:`matches`.
            Useful if you are only filtering using a single regex filter.
            Returns `None` if :attr:`matches` is empty.
        """
        try:
            return self.matches[0]  # type: ignore[index] # pylint: disable=unsubscriptable-object
        except (IndexError, TypeError):
            return None
