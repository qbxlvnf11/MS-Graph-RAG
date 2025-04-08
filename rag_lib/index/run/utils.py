# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Utility functions for the GraphRAG run module."""

from rag_lib.cache.memory_pipeline_cache import InMemoryCache
from rag_lib.cache.pipeline_cache import PipelineCache
from rag_lib.callbacks.noop_workflow_callbacks import NoopWorkflowCallbacks
from rag_lib.callbacks.progress_workflow_callbacks import ProgressWorkflowCallbacks
from rag_lib.callbacks.workflow_callbacks import WorkflowCallbacks
from rag_lib.callbacks.workflow_callbacks_manager import WorkflowCallbacksManager
from rag_lib.index.typing.context import PipelineRunContext
from rag_lib.index.typing.state import PipelineState
from rag_lib.index.typing.stats import PipelineRunStats
from rag_lib.logger.base import ProgressLogger
from rag_lib.storage.memory_pipeline_storage import MemoryPipelineStorage
from rag_lib.storage.pipeline_storage import PipelineStorage


def create_run_context(
    storage: PipelineStorage | None = None,
    cache: PipelineCache | None = None,
    callbacks: WorkflowCallbacks | None = None,
    stats: PipelineRunStats | None = None,
    state: PipelineState | None = None,
) -> PipelineRunContext:
    """Create the run context for the pipeline."""
    return PipelineRunContext(
        stats=stats or PipelineRunStats(),
        cache=cache or InMemoryCache(),
        storage=storage or MemoryPipelineStorage(),
        callbacks=callbacks or NoopWorkflowCallbacks(),
        state=state or {},
    )


def create_callback_chain(
    callbacks: list[WorkflowCallbacks] | None, progress: ProgressLogger | None
) -> WorkflowCallbacks:
    """Create a callback manager that encompasses multiple callbacks."""
    manager = WorkflowCallbacksManager()
    for callback in callbacks or []:
        manager.register(callback)
    if progress is not None:
        manager.register(ProgressWorkflowCallbacks(progress))
    return manager
