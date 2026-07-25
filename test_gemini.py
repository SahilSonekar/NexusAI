from google import genai
from google.genai import types
from decouple import config

client = genai.Client(api_key=config("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="Give me 5 names of animals")]
        )
    ],
    config=types.GenerateContentConfig(
        max_output_tokens=1024,
    ),
)

print(response.text)