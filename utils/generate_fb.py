from openai import OpenAI


def generate_fb(openai_client: OpenAI, content: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはカウンセラーです。"},
            {"role": "system", "content": "可能な限り最大限褒めてください。"},
            {
                "role": "system",
                "content": "簡潔に200文字程度でフィードバックをお願いします。",
            },
            {
                "role": "user",
                "content": f"以下の日記に対してカウンセラーからのフィードバックを日本語で書いてください。\n\n日記:\n{content}",
            },
        ],
        temperature=0.7,
    )
    feedback: str = response.choices[0].message.content
    return feedback
