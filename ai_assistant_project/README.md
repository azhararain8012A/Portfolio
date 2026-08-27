# 🤖 AI Assistant — Streamlit Portfolio Project

A professional starter AI assistant demonstrating how to build a conversational application with **Python + Streamlit + an LLM API integration layer**.

## Architecture

```text
User
  ↓
Streamlit Chat UI
  ↓
Session Conversation History
  ↓
Prompt / Message Construction
  ↓
LLM API Integration
  ↓
Assistant Response
```

## Features

- Modern conversational chat interface
- Persistent conversation state during a session
- User and assistant message rendering
- Environment-variable based API key handling
- Sidebar feature panel
- Clear separation between UI and model integration
- Ready to connect to an OpenAI-compatible LLM endpoint
- Easy deployment with Streamlit

## Installation

```bash
pip install streamlit
```

Set your API key as an environment variable when adding a live model provider:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-key"
```

Run the app:

```bash
streamlit run app.py
```

## AI Concepts Demonstrated

- Conversational AI
- LLM application architecture
- Prompt/message construction
- Context and session memory
- API-based inference
- Secret management
- Interactive AI UI design

## Future Improvements

- Connect a production LLM API
- Add streaming responses
- Add conversation export
- Add document/PDF question answering with RAG
- Add embeddings and vector search
- Add tool/function calling
- Add authentication and usage limits
- Add response evaluation and monitoring

> Never commit API keys or other secrets to GitHub.
