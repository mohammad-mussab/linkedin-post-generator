from few_shots import FewShotPosts
import openai
import os
from dotenv import load_dotenv
load_dotenv()

few_shot = FewShotPosts()


def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"


def generate_post(length, language, tag):
    openai.api_key =  os.getenv("OPENAI_API_KEY")
    prompt = get_prompt(length, language, tag)
    
            
    response = openai.ChatCompletion.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
                model="gpt-4o",
                temperature=0.5,  # Very low temperature for consistent categorization
                max_tokens=2000
            )
            
    return response.choices[0].message.content.strip()

def get_prompt(length, language, tag, tone="storytelling", persona="Hamza Bhatti"):

    length_str = get_length_str(length)

    prompt = f'''
You are a professional content creator trained to write like {persona}, a popular influencer known for deep, relatable, and emotionally-driven storytelling on LinkedIn.

== Objective ==
Generate a new original LinkedIn post in the voice of {persona}, using the writing tone and rhythm consistent with the following inputs and examples. Do not output anything extra — just the post text.

== Inputs ==
1) Topic: {tag}
2) Post Length: {length_str}
3) Language: {language}
   - If "Urduish", write in Roman Urdu blended with English naturally.
   - If "English", keep it clean, modern, and simple.

== Style Guide (Critical) ==
- Use the **storytelling** tone. Start with a relatable hook or personal truth.
- Write in a reflective, conversational style — as if speaking to a friend.
- Use **short sentences**, whitespace, and **line breaks** generously.
- Avoid generic advice. Every sentence should **feel personal and grounded**.
- Keep a **raw, human** voice. Emotion is more important than perfection.
- No emojis. No hashtags.
- You can use a line that Hamza Bhatti used sometimes "Dedo Mazo Ayo"

== Output ==
- The final output must **look and feel like** it was written by {persona}.
- Don't copy or reuse the example lines. Just use their style as inspiration.

== Writing Examples ==
(Below are 1-2 real examples of {persona}'s writing style. Match this tone.)
'''

    examples = few_shot.get_filtered_posts(length, language, tag)

    if len(examples) > 0:
        for i, post in enumerate(examples):
            prompt += f'\n\nExample {i+1}:\n\n{post["text"]}'
            if i == 1:
                break

    return prompt

if __name__ == "__main__":
    print(generate_post("Medium", "English", "Productivity"))