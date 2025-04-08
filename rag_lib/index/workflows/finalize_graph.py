# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing run_workflow method definition."""

import pandas as pd

from rag_lib.callbacks.workflow_callbacks import WorkflowCallbacks
from rag_lib.config.models.embed_graph_config import EmbedGraphConfig
from rag_lib.config.models.graph_rag_config import GraphRagConfig
from rag_lib.index.operations.create_graph import create_graph
from rag_lib.index.operations.finalize_entities import finalize_entities
from rag_lib.index.operations.finalize_relationships import finalize_relationships
from rag_lib.index.operations.snapshot_graphml import snapshot_graphml
from rag_lib.index.typing.context import PipelineRunContext
from rag_lib.index.typing.workflow import WorkflowFunctionOutput
from rag_lib.utils.storage import load_table_from_storage, write_table_to_storage


async def run_workflow(
    config: GraphRagConfig,
    context: PipelineRunContext,
) -> WorkflowFunctionOutput:
    """All the steps to create the base entity graph."""
    entities = await load_table_from_storage("entities", context.storage)
    relationships = await load_table_from_storage("relationships", context.storage)

    final_entities, final_relationships = finalize_graph(
        entities,
        relationships,
        callbacks=context.callbacks,
        embed_config=config.embed_graph,
        layout_enabled=config.umap.enabled,
    )

    await write_table_to_storage(final_entities, "entities", context.storage)
    await write_table_to_storage(final_relationships, "relationships", context.storage)

    if config.snapshots.graphml:
        # todo: extract graphs at each level, and add in meta like descriptions
        graph = create_graph(relationships)
        await snapshot_graphml(
            graph,
            name="graph",
            storage=context.storage,
        )

    return WorkflowFunctionOutput(
        result={
            "entities": entities,
            "relationships": relationships,
        }
    )


def finalize_graph(
    entities: pd.DataFrame,
    relationships: pd.DataFrame,
    callbacks: WorkflowCallbacks,
    embed_config: EmbedGraphConfig | None = None,
    layout_enabled: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """All the steps to finalize the entity and relationship formats."""
    final_entities = finalize_entities(
        entities, relationships, callbacks, embed_config, layout_enabled
    )
    final_relationships = finalize_relationships(relationships)
    return (final_entities, final_relationships)
