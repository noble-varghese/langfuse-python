# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations

import typing

from .create_chat_prompt_request import CreateChatPromptRequest
from .create_text_prompt_request import CreateTextPromptRequest


class CreatePromptRequest_Chat(CreateChatPromptRequest):
    type: typing.Literal["chat"] = "chat"

    class Config:
        frozen = True
        smart_union = True
        allow_population_by_field_name = True
        populate_by_name = True


class CreatePromptRequest_Text(CreateTextPromptRequest):
    type: typing.Literal["text"] = "text"

    class Config:
        frozen = True
        smart_union = True
        allow_population_by_field_name = True
        populate_by_name = True


CreatePromptRequest = typing.Union[CreatePromptRequest_Chat, CreatePromptRequest_Text]
