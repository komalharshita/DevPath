from google import genai

client = genai.Client(api_key="AIzaSyCk-GdXq8a6pFhQcRSqeCO1oBS-0WKN8Cs")  # paste your actual key here

for model in client.models.list():
    print(model.name)