# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""
Indexing API for GraphRAG.

WARNING: This API is under development and may undergo changes in future releases.
Backwards compatibility is not guaranteed at this time.
"""

import logging
import pandas as pd
import random

from rag_lib.callbacks.reporting import create_pipeline_reporter
from rag_lib.callbacks.workflow_callbacks import WorkflowCallbacks
from rag_lib.config.enums import IndexingMethod
from rag_lib.config.models.graph_rag_config import GraphRagConfig
from rag_lib.index.run.run_pipeline import run_pipeline
from rag_lib.index.run.utils import create_callback_chain
from rag_lib.index.typing.pipeline_run_result import PipelineRunResult
from rag_lib.index.typing.workflow import WorkflowFunction
from rag_lib.index.workflows.factory import PipelineFactory
from rag_lib.logger.base import ProgressLogger
from rag_lib.logger.null_progress import NullProgressLogger
from rag_lib.logger.print_progress import PrintProgressLogger

# print_logger = PrintProgressLogger("")
log = logging.getLogger(__name__)

async def build_index(
    config: GraphRagConfig,
    method: IndexingMethod = IndexingMethod.Standard,
    is_update_run: bool = False,
    memory_profile: bool = False,
    callbacks: list[WorkflowCallbacks] | None = None,
    progress_logger: ProgressLogger | None = None,
) -> list[PipelineRunResult]:
    """Run the pipeline with the given configuration.

    Parameters
    ----------
    config : GraphRagConfig
        The configuration.
    method : IndexingMethod default=IndexingMethod.Standard
        Styling of indexing to perform (full LLM, NLP + LLM, etc.).
    memory_profile : bool
        Whether to enable memory profiling.
    callbacks : list[WorkflowCallbacks] | None default=None
        A list of callbacks to register.
    progress_logger : ProgressLogger | None default=None
        The progress logger.

    Returns
    -------
    list[PipelineRunResult]
        The list of pipeline run results
    """

    logger = progress_logger or NullProgressLogger()
    # create a pipeline reporter and add to any additional callbacks
    callbacks = callbacks or []
    callbacks.append(create_pipeline_reporter(config.reporting, None))

    workflow_callbacks = create_callback_chain(callbacks, logger)

    outputs: list[PipelineRunResult] = []

    if memory_profile:
        log.warning("New pipeline does not yet support memory profiling.")

    pipeline = PipelineFactory.create_pipeline(config, method)

    workflow_callbacks.pipeline_start(pipeline.names())

    async for output in run_pipeline(
        pipeline,
        config,
        callbacks=workflow_callbacks,
        logger=logger,
        is_update_run=is_update_run,
    ):  
        if isinstance(output.result, pd.DataFrame):
            print(f'---- Results of \"{output.workflow}\" Pipeline ----')
            print('- Columns:', output.result.columns)
            print(output.result.head())
            print('-------------------------------------')
        elif isinstance(output.result, dict):
            print(f'---- Results of \"{output.workflow}\" Pipeline----')
            print('- Keys:', output.result.keys())
            print('-------------------------------------')

        outputs.append(output)
        if output.errors and len(output.errors) > 0:
            logger.error(output.workflow)
        else:
            logger.success(output.workflow)
        logger.info(str(output.result))

    workflow_callbacks.pipeline_end(outputs)
    return outputs


def register_workflow_function(name: str, workflow: WorkflowFunction):
    """Register a custom workflow function. You can then include the name in the settings.yaml workflows list."""
    PipelineFactory.register(name, workflow)
