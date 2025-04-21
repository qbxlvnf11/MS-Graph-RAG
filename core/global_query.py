import asyncio
import sys
import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING, Any

import rag_lib.api as api
from rag_lib.callbacks.noop_query_callbacks import NoopQueryCallbacks
from rag_lib.config.load_config import load_config
from rag_lib.config.models.graph_rag_config import GraphRagConfig
from rag_lib.logger.print_progress import PrintProgressLogger
from rag_lib.utils.api import create_storage_from_config
from rag_lib.utils.storage import load_table_from_storage, storage_has_table

from core.utils import resolve_output_files

logger = PrintProgressLogger("")
    
async def run_global_search(
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    community_level: int | None,
    dynamic_community_selection: bool,
    response_type: str,
    streaming: bool,
    web_streaming: bool,
    query: str,
):
    """Perform a global search with a given query.

    Loads index files required for global search and calls the Query API.
    """
    root = root_dir.resolve()
    cli_overrides = {}
    if data_dir:
        cli_overrides["output.base_dir"] = str(data_dir)
    config = load_config(root, config_filepath, cli_overrides)

    # if web_streaming:
    dataframe_dict = await resolve_output_files(
        config=config,
        output_list=[
            "communities",
            "community_reports",
            "text_units",
            "relationships",
            "entities",
        ],
        optional_list=[
            "covariates",
        ],
        web_streaming=web_streaming
    )

    # Call the Multi-Index Global Search API
    if dataframe_dict["multi-index"]:
        final_entities_list = dataframe_dict["entities"]
        final_communities_list = dataframe_dict["communities"]
        final_community_reports_list = dataframe_dict["community_reports"]
        index_names = dataframe_dict["index_names"]

        logger.success(
            f"Running Multi-index Global Search: {dataframe_dict['index_names']}"
        )

        response, context_data = asyncio.run(
            api.multi_index_global_search(
                config=config,
                entities_list=final_entities_list,
                communities_list=final_communities_list,
                community_reports_list=final_community_reports_list,
                index_names=index_names,
                community_level=community_level,
                dynamic_community_selection=dynamic_community_selection,
                response_type=response_type,
                streaming=streaming,
                query=query,
            )
        )
        logger.success(f"Global Search Response:\n{response}")
        # NOTE: we return the response and context data here purely as a complete demonstration of the API.
        # External users should use the API directly to get the response and context data.
        return response, context_data

    # Otherwise, call the Single-Index Global Search API
    final_entities: pd.DataFrame = dataframe_dict["entities"]
    final_communities: pd.DataFrame = dataframe_dict["communities"]
    final_community_reports: pd.DataFrame = dataframe_dict["community_reports"]

    if streaming:

        async def run_streaming_search():
            full_response = ""
            context_data = {}

            def on_context(context: Any) -> None:
                nonlocal context_data
                context_data = context

            callbacks = NoopQueryCallbacks()
            callbacks.on_context = on_context

            async for stream_chunk in api.global_search_streaming(
                config=config,
                entities=final_entities,
                communities=final_communities,
                community_reports=final_community_reports,
                community_level=community_level,
                dynamic_community_selection=dynamic_community_selection,
                response_type=response_type,
                query=query,
                callbacks=[callbacks],
            ):
                full_response += stream_chunk
                print(stream_chunk, end="")  # noqa: T201
                sys.stdout.flush()  # flush output buffer to display text immediately
            print()  # noqa: T201
            return full_response, context_data

        if web_streaming:
            return run_streaming_search()
        else:
            return asyncio.run(run_streaming_search())
        
    # not streaming
    # response, context_data = asyncio.run(
    #     api.global_search(
    #         config=config,
    #         entities=final_entities,
    #         communities=final_communities,
    #         community_reports=final_community_reports,
    #         community_level=community_level,
    #         dynamic_community_selection=dynamic_community_selection,
    #         response_type=response_type,
    #         query=query,
    #     )
    # )
    response, context_data = await api.global_search(
            config=config,
            entities=final_entities,
            communities=final_communities,
            community_reports=final_community_reports,
            community_level=community_level,
            dynamic_community_selection=dynamic_community_selection,
            response_type=response_type,
            query=query,
        )

    # logger.success(f"Local Search Response:\n{response}")
    # NOTE: we return the response and context data here purely as a complete demonstration of the API.
    # External users should use the API directly to get the response and context data.
    return response, context_data