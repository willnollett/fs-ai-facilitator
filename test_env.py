# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 13:54:45 2025

@author: WillNollett
"""

from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = openai.AzureOpenAI(
    api_key=openai.api_key,
    api_version=openai.api_version,
    azure_endpoint=openai.api_base,
)

response = client.chat.completions.create(
    model=DEPLOYMENT_NAME,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello"}
    ]
)

print("Response:", response.choices[0].message.content)
