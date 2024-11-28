import os
import logging
from typing import List, Dict, Any
from openai import OpenAI
from notion_client import Client
from notion_client.helpers import collect_paginated_api
from dotenv import load_dotenv

from utils.blocks_to_md import blocks_to_md
from utils.generate_fb import generate_fb

load_dotenv()

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY: str = os.getenv("NOTION_API_KEY")
NOTION_DIARY_DB_ID: str = os.getenv("NOTION_DIARY_DB_ID")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    notion_client: Client = Client(auth=NOTION_API_KEY)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Notionから日記を取得
    diaries: List[Dict[str, Any]] = get_diaries_db(notion_client, NOTION_DIARY_DB_ID)

    # 各日記に対してフィードバックを生成
    for diary in diaries:
        content_md: str = get_diary_content_md(notion_client, diary["id"])
        feedback: str = generate_fb(openai_client, content_md)
        append_feedback_to_diary(notion_client, diary["id"], feedback)
        update_feedback_status(notion_client, diary["id"])
        print(f'id: {diary["id"]}, feedback: {feedback[:30]}')

    logger.info("スクリプトを終了しました。")


def get_diaries_db(notion_client: Client, database_id: str) -> List[Dict[str, Any]]:
    diaries = collect_paginated_api(
        notion_client.databases.query,
        database_id=database_id,
        filter={
            "and": [
                {"property": "AIFB", "checkbox": {"equals": False}},
                {"property": "記入済", "checkbox": {"equals": True}},
            ]
        },
    )
    return diaries


def get_diary_content_md(notion_client: Client, diary_id: str) -> str:
    blocks = collect_paginated_api(
        notion_client.blocks.children.list, block_id=diary_id
    )
    return blocks_to_md(blocks, notion_client)


def append_feedback_to_diary(
    notion_client: Client, diary_id: str, feedback: str
) -> None:
    new_blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "カウンセラーからのフィードバック"},
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": feedback},
                    }
                ]
            },
        },
    ]

    notion_client.blocks.children.append(block_id=diary_id, children=new_blocks)


def update_feedback_status(notion_client: Client, diary_id: str) -> None:
    notion_client.pages.update(
        page_id=diary_id, properties={"AIFB": {"checkbox": True}}
    )


if __name__ == "__main__":
    main()
