import os
import sys
import asyncio
from pathlib import Path

import rag_lib.api as api
from rag_lib.config.enums import CacheType, IndexingMethod
from rag_lib.config.logging import enable_logging_with_config
from rag_lib.index.validate_config import validate_config_names
from rag_lib.logger.factory import LoggerFactory, LoggerType
from rag_lib.utils.cli import redact
from rag_lib.logger.factory import ProgressLogger, LoggerFactory, PrintProgressLogger, LoggerType
from rag_lib.utils.storage import (
    delete_table_from_storage,
    load_table_from_storage,
    write_table_to_storage,
)
from rag_lib.storage.factory import StorageFactory

from utils import _logger

logger = PrintProgressLogger("")

def _register_signal_handlers(logger: ProgressLogger):
    import signal

    def handle_signal(signum, _):
        # Handle the signal here
        logger.info(f"Received signal {signum}, exiting...")  # noqa: G004
        logger.dispose()
        for task in asyncio.all_tasks():
            task.cancel()
        logger.info("All tasks cancelled. Exiting...")

    # Register signal handlers for SIGINT and SIGHUP
    signal.signal(signal.SIGINT, handle_signal)

    if sys.platform != "win32":
        signal.signal(signal.SIGHUP, handle_signal)


def indexing(
    config,
    method,
    is_update_run,
    verbose,
    memprofile,
    cache,
    logger,
    dry_run,
    skip_validation,
):
    
    progress_logger = LoggerFactory().create_logger(logger)
    info, error, success = _logger(progress_logger)

    if not cache:
        config.cache.type = CacheType.none

    enabled_logging, log_path = enable_logging_with_config(config, verbose)
    if enabled_logging:
        info(f"Logging enabled at {log_path}", True)
    else:
        info(
            f"Logging not enabled for config {redact(config.model_dump())}",
            True,
        )

    if not skip_validation:
        validate_config_names(progress_logger, config)

    info(f"Starting pipeline run. {dry_run=}", verbose)
    info(
        f"Using default configuration: {redact(config.model_dump())}",
        verbose,
    )

    if dry_run:
        info("Dry run complete, exiting...", True)
        sys.exit(0)

    _register_signal_handlers(progress_logger)

    outputs = asyncio.run(
        api.build_index(
            config=config,
            method=method,
            is_update_run=is_update_run,
            memory_profile=memprofile,
            progress_logger=progress_logger,
        )
    )
    encountered_errors = any(
        output.errors and len(output.errors) > 0 for output in outputs
    )

    progress_logger.stop()
    if encountered_errors:
        error(
            "Errors occurred during the pipeline run, see logs for more details.", True
        )
    else:
        success("All workflows completed successfully.", True)

    sys.exit(1 if encountered_errors else 0)

# async def indexing(config):

#     storage_config = config.output.model_dump()
#     logger.info(f'Storage config: {storage_config}')

#     storage = StorageFactory().create_storage(
#         storage_type=storage_config["type"],
#         kwargs=storage_config,
#     )

#     final_documents = await load_table_from_storage("create_final_documents", storage)
#     final_text_units = await load_table_from_storage("create_final_text_units", storage)
#     final_entities = await load_table_from_storage("create_final_entities", storage)
#     final_covariates = await load_table_from_storage("create_final_covariates", storage)
#     final_nodes = await load_table_from_storage("create_final_nodes", storage)
#     final_relationships = await load_table_from_storage(
#         "create_final_relationships", storage
#     )
#     final_communities = await load_table_from_storage("create_final_communities", storage)
#     final_community_reports = await load_table_from_storage(
#         "create_final_community_reports", storage
#     )

#     # we've renamed document attributes as metadata
#     if "attributes" in final_documents.columns:
#         final_documents.rename(columns={"attributes": "metadata"}, inplace=True)

#     # we're removing the nodes table, so we need to copy the graph columns into entities
#     graph_props = (
#         final_nodes.loc[:, ["id", "degree", "x", "y"]].groupby("id").first().reset_index()
#     )
#     final_entities = final_entities.merge(graph_props, on="id", how="left")
#     # we're also persisting the frequency column
#     final_entities["frequency"] = final_entities["text_unit_ids"].count()


#     # we added children to communities to eliminate query-time reconstruction
#     parent_grouped = final_communities.groupby("parent").agg(
#         children=("community", "unique")
#     )
#     final_communities = final_communities.merge(
#         parent_grouped,
#         left_on="community",
#         right_on="parent",
#         how="left",
#     )
#     # replace NaN children with empty list
#     final_communities["children"] = final_communities["children"].apply(
#         lambda x: x if isinstance(x, np.ndarray) else []  # type: ignore
#     )

#     # add children to the reports as well
#     final_community_reports = final_community_reports.merge(
#         parent_grouped,
#         left_on="community",
#         right_on="parent",
#         how="left",
#     )

#     # we renamed all the output files for better clarity now that we don't have workflow naming constraints from DataShaper
#     await write_table_to_storage(final_documents, "documents", storage)
#     await write_table_to_storage(final_text_units, "text_units", storage)
#     await write_table_to_storage(final_entities, "entities", storage)
#     await write_table_to_storage(final_relationships, "relationships", storage)
#     await write_table_to_storage(final_covariates, "covariates", storage)
#     await write_table_to_storage(final_communities, "communities", storage)
#     await write_table_to_storage(final_community_reports, "community_reports", storage)

#     # delete all the old versions
#     await delete_table_from_storage("create_final_documents", storage)
#     await delete_table_from_storage("create_final_text_units", storage)
#     await delete_table_from_storage("create_final_entities", storage)
#     await delete_table_from_storage("create_final_nodes", storage)
#     await delete_table_from_storage("create_final_relationships", storage)
#     await delete_table_from_storage("create_final_covariates", storage)
#     await delete_table_from_storage("create_final_communities", storage)
#     await delete_table_from_storage("create_final_community_reports", storage)