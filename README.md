# TalentScout Hiring Assistant 🤖

## Project Overview
TalentScout is an intelligent Hiring Assistant chatbot designed to streamline the technical screening process for candidates. It collects candidate information, understands their tech stack, and generates tailored technical interview questions using LLMs.

## Installation Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Internship_project
   ```

2. **Install Dependencies:**
   Ensure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Alternatively, you can enter the API key in the application sidebar.

## Usage Guide
Run the application using Streamlit:
```bash
streamlit run app.py
```

1. **Information Gathering:** Fill out the form with your details and tech stack.
2. **Interview:** The chatbot will generate questions based on your stack. Answer them in the chat interface.
3. **Conclusion:** Type "exit" or "bye" to end the session.

## Technical Details
- **Frontend:** Streamlit for a responsive and interactive UI.
- **Backend:** Python.
- **LLM Integration:** LangChain framework for managing prompts and OpenAI API interactions.
- **Architecture:**
    - `app.py`: Main application logic and UI.
    - `utils.py`: Helper functions for LLM calls.
    - `prompts.py`: Centralized prompt templates.

## Challenges & Solutions
- **Context Management:** Ensuring the bot remembers the candidate's name and tech stack. *Solution*: We inject a system message with the summary of the candidate's profile right before the Q&A phase.
- **Prompt Engineering:** Getting relevant questions. *Solution*: We use a dedicated "Question Generation" prompt first, then feed the questions to the chat bot as context.

## License
MIT
