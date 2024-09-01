import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_content(pdf_content):
    prompt = f"Generate 3 TikTok scripts based on the following content. Each script should have a main content and a call-to-action:\n\n{pdf_content}\n\nProvide the output in the following format for each script:\nScript [number]:\nMain Content: [main content]\nCall-to-Action: [call-to-action]"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative TikTok script writer."},
            {"role": "user", "content": prompt}
        ]
    )
    
    scripts = response.choices[0].message.content.split("Script ")
    return [script.strip() for script in scripts if script.strip()]