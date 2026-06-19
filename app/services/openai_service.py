import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv(
        "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"
    )
)


def get_llm_analysis(
    prompt
):

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {
                "role": "system",
                "content":
                "You are an expert data analyst."
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.3
    )

    return (
        response
        .choices[0]
        .message
        .content
    )