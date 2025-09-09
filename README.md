## Setup and Installation

1. **Clone the Repository:**

```shell
bash git clone https://github.com/otutukingsley/agent-con-project
```

2. **Create and Activate a Virtual Environment (Recommended):**

```shell
bash python -m venv venv # On macOS/Linux source venv/bin/activate # On Windows # venv\Scripts\activate
```

3. **Install Dependencies:**

Ensure `pip` is up-to-date, then install requirements:

```shell
bash pip install --upgrade pip pip install -r requirements.txt
```

4. **Set Up Environment Variables:**

Create a `.env` file in the news_agent directory with your API keys:

    -   `NEWS_API_KEY`: From newsapi.org.
    -   `GOOGLE_API_KEY`: For Google's Generative AI services (e.g., Gemini) from Google AI Studio.
    -   `GOOGLE_GENAI_USE_VERTEXAI=FALSE`: Ensures direct use of Google AI Generative Language API.

## How to Run
To interact with the agent run:
```shell
adk web
```