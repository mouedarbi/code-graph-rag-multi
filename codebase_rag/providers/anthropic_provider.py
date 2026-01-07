from __future__ import annotations

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider as PydanticAnthropicProvider

from .. import constants as cs
from .. import exceptions as ex
from .base import ModelProvider


class AnthropicProvider(ModelProvider):
    def __init__(
        self,
        api_key: str | None = None,
        **kwargs: str | int | None,
    ) -> None:
        super().__init__(**kwargs)
        self.api_key = api_key

    @property
    def provider_name(self) -> cs.Provider:
        return cs.Provider.ANTHROPIC

    def validate_config(self) -> None:
        if not self.api_key:
            raise ValueError(ex.ANTHROPIC_NO_KEY)

    def create_model(
        self, model_id: str, **kwargs: str | int | None
    ) -> AnthropicModel:
        self.validate_config()
        
        provider = PydanticAnthropicProvider(api_key=self.api_key)
        return AnthropicModel(model_id, provider=provider)
