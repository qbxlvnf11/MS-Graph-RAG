# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""The Indexing Engine text embed package root."""

from rag_lib.index.operations.embed_text.embed_text import (
    TextEmbedStrategyType,
    embed_text,
)

__all__ = ["TextEmbedStrategyType", "embed_text"]
