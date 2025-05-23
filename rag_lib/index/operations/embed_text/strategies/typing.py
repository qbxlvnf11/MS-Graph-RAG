# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'TextEmbeddingResult' model."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from rag_lib.cache.pipeline_cache import PipelineCache
from rag_lib.callbacks.workflow_callbacks import WorkflowCallbacks


@dataclass
class TextEmbeddingResult:
    """Text embedding result class definition."""

    embeddings: list[list[float] | None] | None


TextEmbeddingStrategy = Callable[
    [
        list[str],
        WorkflowCallbacks,
        PipelineCache,
        dict,
    ],
    Awaitable[TextEmbeddingResult],
]
