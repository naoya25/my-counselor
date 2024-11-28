from notion_client.helpers import collect_paginated_api


def blocks_to_md(blocks, notion_client):
    md_text = ""

    for block in blocks:
        block_type = block["type"]
        block_id = block["id"]

        if block_type == "paragraph":
            text = extract_text(block["paragraph"]["rich_text"])
            md_text += f"{text}\n\n"

        elif block_type == "heading_1":
            text = extract_text(block["heading_1"]["rich_text"])
            md_text += f"# {text}\n\n"

        elif block_type == "heading_2":
            text = extract_text(block["heading_2"]["rich_text"])
            md_text += f"## {text}\n\n"

        elif block_type == "heading_3":
            text = extract_text(block["heading_3"]["rich_text"])
            md_text += f"### {text}\n\n"

        elif block_type == "bulleted_list_item":
            text = extract_text(block["bulleted_list_item"]["rich_text"])
            md_text += f"- {text}\n"

            # 子ブロックの処理（ネストされたリスト）
            if block["has_children"]:
                child_blocks = collect_paginated_api(
                    notion_client.blocks.children.list, block_id=block_id
                )
                child_md = blocks_to_md(child_blocks, notion_client)
                md_text += indent_md(child_md)

        elif block_type == "numbered_list_item":
            text = extract_text(block["numbered_list_item"]["rich_text"])
            md_text += f"1. {text}\n"

            # 子ブロックの処理（ネストされたリスト）
            if block["has_children"]:
                child_blocks = collect_paginated_api(
                    notion_client.blocks.children.list, block_id=block_id
                )
                child_md = blocks_to_md(child_blocks, notion_client)
                md_text += indent_md(child_md)

        elif block_type == "quote":
            text = extract_text(block["quote"]["rich_text"])
            md_text += f"> {text}\n\n"

        elif block_type == "code":
            language = block["code"].get("language", "")
            text = extract_text(block["code"]["rich_text"])
            md_text += f"```{language}\n{text}\n```\n\n"

        elif block_type == "to_do":
            checked = block["to_do"]["checked"]
            text = extract_text(block["to_do"]["rich_text"])
            checkbox = "[x]" if checked else "[ ]"
            md_text += f"- {checkbox} {text}\n"

        elif block_type == "toggle":
            text = extract_text(block["toggle"]["rich_text"])
            md_text += f"<details><summary>{text}</summary>\n"

            if block["has_children"]:
                child_blocks = collect_paginated_api(
                    notion_client.blocks.children.list, block_id=block_id
                )
                child_md = blocks_to_md(child_blocks, notion_client)
                md_text += f"{child_md}\n"

            md_text += "</details>\n\n"

        # 他のブロックタイプも必要に応じて追加可能

        # 子ブロックの再帰的処理（一般的な子ブロック）
        elif block["has_children"]:
            child_blocks = collect_paginated_api(
                notion_client.blocks.children.list, block_id=block_id
            )
            child_md = blocks_to_md(child_blocks, notion_client)
            md_text += f"{child_md}\n"

    return md_text


def extract_text(rich_text_array):
    text_content = ""
    for item in rich_text_array:
        plain_text = item["plain_text"]
        annotations = item.get("annotations", {})
        if annotations.get("bold"):
            plain_text = f"**{plain_text}**"
        if annotations.get("italic"):
            plain_text = f"*{plain_text}*"
        if annotations.get("underline"):
            plain_text = f"<u>{plain_text}</u>"
        if annotations.get("strikethrough"):
            plain_text = f"~~{plain_text}~~"
        if annotations.get("code"):
            plain_text = f"`{plain_text}`"
        href = item.get("href")
        if href:
            plain_text = f"[{plain_text}]({href})"
        text_content += plain_text
    return text_content


def indent_md(md_text, level=1):
    indented_text = ""
    for line in md_text.split("\n"):
        indented_text += "    " * level + line + "\n"
    return indented_text
