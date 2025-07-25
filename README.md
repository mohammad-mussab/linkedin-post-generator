# LinkedIn Post Generator (Hamza Bhatti Style)

This project generates original LinkedIn posts in the style of Hamza Bhatti, using real post examples, topic tags, and AI models. It features a Streamlit web UI for easy post generation and includes data cleaning and preprocessing scripts.

---

## Workflow

1. **Data Scraping:**  
   First, I scraped 40 LinkedIn posts using an [Apify](https://apify.com/) actor.

2. **Preprocessing:**  
   The raw posts were then cleaned, tagged, and normalized using `pre_processing.py`. This script detects language, extracts and merges professional tags, and outputs a structured dataset.

---

## Project Structure

```
.
├── main.py                        # Streamlit web app for post generation
├── post_generator.py              # Prompt construction and OpenAI API call
├── few_shots.py                   # Few-shot example selection and tag cleaning
├── pre_processing.py              # Data cleaning, tag extraction, and normalization
├── data/
│   ├── cleaned_linkedin_posts.json   # Cleaned, structured post data
│   └── linkedin_posts.json           # Raw LinkedIn post data (scraped)
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

---

## Setup Instructions

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   - Create a `.env` file in the root directory with:
     ```
     OPENAI_API_KEY=your_openai_api_key
     GROQ_API_KEY=your_groq_api_key
     ```
   - (You can get OpenAI API keys from https://platform.openai.com/)

4. **Prepare data**
   - Place your raw LinkedIn posts in `data/linkedin_posts.json`.
   - Run `pre_processing.py` to generate `data/cleaned_linkedin_posts.json`:
     ```bash
     python pre_processing.py
     ```
   - This will clean, tag, and structure your data for use in the app.

5. **Run the Streamlit app**
   ```bash
   streamlit run main.py
   ```

---

## Usage

- Select a topic (tag), post length, and language in the web UI.
- Click "Generate" to create a new post in Hamza Bhatti's style.
- Example tags and post examples are drawn from your dataset.

---

## File Descriptions

- **pre_processing.py**  
  Cleans and processes raw LinkedIn posts, detects language, counts lines, extracts and normalizes tags (using Groq LLM or fallback rules), and saves the cleaned data.

- **few_shots.py**  
  Loads cleaned posts, categorizes by length, extracts unique tags, and provides filtered examples for few-shot prompting.

- **post_generator.py**  
  Constructs prompts for OpenAI's GPT models, including style guides and real examples, and calls the OpenAI API to generate new posts.

- **main.py**  
  Streamlit web app for user interaction. Lets users select topic, length, and language, and displays the generated post.

- **data/cleaned_linkedin_posts.json**  
  Cleaned, structured post data (used by the app).

- **data/linkedin_posts.json**  
  Raw LinkedIn post data (used for preprocessing).

---

## Requirements

See `requirements.txt` for all dependencies.

---

## Notes

- **API Keys:** Never share your `.env` file or API keys publicly.
- **Data:** Ensure your data files are in the correct format (see `data/cleaned_linkedin_posts.json` for structure).
- **Model:** The app uses OpenAI's `gpt-4o` model by default, but you can change this in `post_generator.py`.

---

