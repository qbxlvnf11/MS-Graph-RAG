# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing run and _embed_text methods definitions."""

import random
from collections.abc import Iterable
from typing import Any

from rag_lib.cache.pipeline_cache import PipelineCache
from rag_lib.callbacks.workflow_callbacks import WorkflowCallbacks
from rag_lib.index.operations.embed_text.strategies.typing import TextEmbeddingResult
from rag_lib.logger.progress import ProgressTicker, progress_ticker


async def run(  # noqa RUF029 async is required for interface
    input: list[str],
    callbacks: WorkflowCallbacks,
    cache: PipelineCache,
    _args: dict[str, Any],
) -> TextEmbeddingResult:
    """Run the Claim extraction chain."""
    input = input if isinstance(input, Iterable) else [input]
    ticker = progress_ticker(callbacks.progress, len(input))
    return TextEmbeddingResult(
        embeddings=[_embed_text(cache, text, ticker) for text in input]
    )


def _embed_text(_cache: PipelineCache, _text: str, tick: ProgressTicker) -> list[float]:
    """Embed a single piece of text."""
    tick(1)
    return [random.random(), random.random(), random.random()]  # noqa S311
