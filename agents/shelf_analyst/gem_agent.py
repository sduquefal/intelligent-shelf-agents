from google.genai import types

from common.gem_client import client, MODEL_NAME

from agents.shelf_analyst.tools import (
    resolve_store,
    get_store_summary,
    compare_store_daily,
    get_store_trend,
    get_store_ranking,
    get_latest_daily_summary,
)

SYSTEM_PROMPT = """
You are Shelf Analyst, part of the Intelligent Shelf AI Platform.

Your role is to help business users understand Intelligent Shelf performance.

Use SNSG, Bodega and Quiebre terminology.
Never invent metrics.
Always use tools when data is required.
"""

chat = client.chats.create(
    model=MODEL_NAME,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[
            resolve_store,
            get_store_summary,
            compare_store_daily,
            get_store_trend,
            get_store_ranking,
            get_latest_daily_summary,
        ],
    ),
)