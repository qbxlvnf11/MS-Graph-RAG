import asyncio

from typing import TYPE_CHECKING, Any

from rag_lib.config.models.graph_rag_config import GraphRagConfig
from rag_lib.utils.api import create_storage_from_config
from rag_lib.utils.storage import load_table_from_storage, storage_has_table

async def resolve_output_files(
    config: GraphRagConfig,
    output_list: list[str],
    optional_list: list[str] | None = None,
    web_streaming=False
) -> dict[str, Any]:
    """Read indexing output files to a dataframe dict."""
    dataframe_dict = {}

    # Loading output files for multi-index search
    if config.outputs:
        dataframe_dict["multi-index"] = True
        dataframe_dict["num_indexes"] = len(config.outputs)
        dataframe_dict["index_names"] = config.outputs.keys()
        for output in config.outputs.values():
            storage_obj = create_storage_from_config(output)
            for name in output_list:
                if name not in dataframe_dict:
                    dataframe_dict[name] = []
                df_value = asyncio.run(
                    load_table_from_storage(name=name, storage=storage_obj)
                )
                dataframe_dict[name].append(df_value)

            # for optional output files, do not append if the dataframe does not exist
            if optional_list:
                for optional_file in optional_list:
                    if optional_file not in dataframe_dict:
                        dataframe_dict[optional_file] = []
                    file_exists = asyncio.run(
                        storage_has_table(optional_file, storage_obj)
                    )
                    if file_exists:
                        df_value = asyncio.run(
                            load_table_from_storage(
                                name=optional_file, storage=storage_obj
                            )
                        )
                        dataframe_dict[optional_file].append(df_value)
        return dataframe_dict
    
    # Loading output files for single-index search
    dataframe_dict["multi-index"] = False
    storage_obj = create_storage_from_config(config.output)
    for name in output_list:
        df_value = await load_table_from_storage(name=name, storage=storage_obj)
        # if web_streaming:
        #     df_value = await load_table_from_storage(name=name, storage=storage_obj)
        # else:
        #     df_value = asyncio.run(load_table_from_storage(name=name, storage=storage_obj))
            
        dataframe_dict[name] = df_value

    # for optional output files, set the dict entry to None instead of erroring out if it does not exist
    if optional_list:
        for optional_file in optional_list:
            file_exists = await storage_has_table(optional_file, storage_obj)
            # if web_streaming:
            #     file_exists = await storage_has_table(optional_file, storage_obj)
            # else:
            #     file_exists = asyncio.run(storage_has_table(optional_file, storage_obj))

            if file_exists:
                df_value = await load_table_from_storage(name=optional_file, storage=storage_obj)
                # if web_streaming:
                #     df_value = await load_table_from_storage(name=optional_file, storage=storage_obj)
                # else:
                #     df_value = asyncio.run(
                #         load_table_from_storage(name=optional_file, storage=storage_obj)
                #     )
                dataframe_dict[optional_file] = df_value
            else:
                dataframe_dict[optional_file] = None
    return dataframe_dict