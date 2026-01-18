# TalentScout Hiring Assistant - Project Documentation

## 1. Executive Summary

**TalentScout** is an intelligent, AI-powered hiring assistant designed to revolutionize the technical screening process. It acts as a bridge between candidates and recruiters, conducting initial technical interviews, gathering candidate profiles, and effectively evaluating technical skills using Large Language Models (LLMs).

The system provides a dual-role interface:
1.  **Applicant View:** A conversational interface where candidates are interviewed by an AI.
2.  **Recruiter (Admin) View:** A dashboard for reviewing candidate transcripts, automated evaluations, and sentiment analysis.

---

## 2. Core Features

### 🚀 For Applicants (Candidate Flow)
-   **Interactive Interview:** A natural language chat interface that adapts to the candidate's responses.
-   **Profile Gathering:** Collects essential information (Experience, Position, Tech Stack) through conversation.
-   **Tech Stack Analysis:** Automatically identifies the candidate's technical skills to tailor the interview.
-   **Dynamic Questioning:** Generates relevant technical interview questions based on the identified tech stack.
-   **Privacy-Focused:** Securely handles personal data.

### 🛡️ For Recruiters (Admin Flow)
-   **Secure Dashboard:** Password-protected area for hiring managers.
-   **Candidate Management:** View a list of all interviewed candidates with key metrics.
-   **Automated Evaluation:**
    -   **Scoring:** 0-100 technical assessment score.
    -   **Recommendation:** "Hire", "Consider", or "Reject" suggestions.
    -   **Strengths & Weaknesses:** AI-generated breakdown of the candidate's performance.
-   **Transcript Review:** Full access to the interview chat history.
-   **Sentiment Analysis:** Insights into the candidate's attitude and communication style during the interview.

---

## 3. Technical Architecture

The application is built as a monolithic Streamlit application with a clear separation of concerns.

### Tech Stack
-   **Frontend & UI:** [Streamlit](https://streamlit.io/) (Python-based web framework).
-   **Backend Logic:** Python 3.x.
-   **AI & LLM Orchestration:** [LangChain](https://www.langchain.com/).
-   **LLM Providers:** Supports OpenAI (GPT models) and Groq (High-speed inference).
-   **Data Storage:** JSON-based local storage (`anonymized_records.json`) for simplicity and portability.
-   **Data Processing:** Pandas for dashboard data visualization.

### Architecture Components
1.  **`app.py`**: The entry point. Handles routing (Applicant vs. Admin), UI rendering, and session state management.
2.  **`utils.py`**: Contains core logic for interacting with LLMs (generating responses, analyzing sentiment, evaluating candidates).
3.  **`prompts.py`**: Stores the system prompts and templates used to guide the AI's behavior and persona.
4.  **`data_handler.py`**: Manages reading and writing to the storage system (`anonymized_records.json`), including PII handling and data retrieval.

---

## 4. Setup and Installation

### Prerequisites
-   Python 3.8 or higher.
-   Git.
-   An API Key from OpenAI or Groq.

### Step-by-Step Installation

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd Internship_project
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Create a `.env` file in the root directory to store your secrets.
    ```bash
    # Create .env file
    touch .env
    ```
    
    Add your API keys to the `.env` file:
    ```env
    OPENAI_API_KEY=sk-proj-...
    # OR if using Groq
    GROQ_API_KEY=gsk_...
    ```

---

## 5. Usage Guide

### Starting the Application
Run the Streamlit server:
```bash
streamlit run app.py
```
The application will open in your default web browser at `http://localhost:8501`.

### Using the Applicant Mode
1.  On the landing page, select **"Applicant"**.
2.  Chat with the AI. Introduce yourself and mention your tech stack (e.g., "I'm a Python developer").
3.  The AI will verify your information and switch to the **Technical Interview** phase.
4.  Answer the technical questions posed by the AI.
5.  When finished, click **"Finish Interview"** in the sidebar or type "exit".

### Using the Admin Dashboard
1.  On the landing page, select **"Recruiter"**.
2.  Login with the default credentials:
    -   **Password:** `admin123`
3.  View the table of candidates.
4.  Select a "Record ID" from the dropdown to view the detailed transcript and evaluation report.

---

## 6. Directory Structure

```
Internship_project/
├── .env                # API keys and secrets (not committed)
├── .gitignore          # Git ignore rules
├── app.py              # Main application file
├── data_handler.py     # Data persistence logic
├── prompts.py          # LLM System prompts
├── requirements.txt    # Python dependencies
├── utils.py            # AI helper functions
└── anonymized_records.json # Local database (auto-created)
```
