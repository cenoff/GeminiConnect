# GeminiConnect 

![Tests](https://github.com/cenoff/GeminiConnect/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/cenoff/GeminiConnect/branch/main/graph/badge.svg)](https://codecov.io/gh/cenoff/GeminiConnect)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**GeminiConnect** is a Python-based proxy server that adapts the Gemini API for use with any OpenAI-compatible clients, such as OpenWebUI.

## Why I Built This

If you've attempted to connect OpenWebUI directly to the Gemini API (especially the Pro model), you've likely faced strict rate limits.

**Free Pro Version Limit:** The free Gemini Pro API has a severe limitation of only 2 requests per minute.

**"Noisy" Clients:** OpenWebUI, for its internal operations (meta-requests, web search), sends numerous background requests. These requests quickly consume the entire minute's limit, making normal interaction with the model impossible.

## How It Works

GeminiConnect acts as an "intelligent" intermediary that addresses both issues:

**Automatic Model Selection** - The proxy automatically determines the complexity of the user's request and decides which model to call — the fast **Flash** for simple tasks or the powerful **Pro** for complex ones.

**API Key Pool** - The project allows you to use an *unlimited number* of Gemini API keys. You can simply use multiple Google accounts and add all free keys to the configuration. GeminiConnect will automatically **switch to the next key** if the current one exhausts its rate limit. With just two API keys, the aggregated throughput of the pool **exceeds** the paid Gemini tier.

## Tech Stack

Here's what's under the hood:

- **Python 3.11+**
- **FastAPI** for the high-performance API endpoint
- **httpx v2** for asynchronous non-blocking requests to Google
- **Docker** for containerization and easy deployment
- **Pytest** for robust testing

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- Gemini API Keys (get them from [Google AI Studio](https://aistudio.google.com))

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/cenoff/GeminiConnect.git
   cd GeminiConnect
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   
   Create a `.env` file (see `.env.example`) and add your keys:
   ```env
   GEMINI_API_KEYS=["key1", "key2", "key3"]
   PORT=4535
   ```

4. **Run the server**
   ```bash
   python main.py
   ```

### Running with Docker

1. **Configure `.env`** as shown above.
   
2. **Build and run**:
   ```bash
   docker-compose up -d --build
   ```
   
3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

## Connecting to OpenWebUI

1. Navigate to **Connections** settings in OpenWebUI.
2. Add a new **OpenAI-compatible** connection.
3. **URL**: `http://localhost:4535/v1` (adjust port if needed).
4. **Key**: `None` (or any string).
5. **Model Name**: 
   - Use `Auto` to enable automatic model selection based on query complexity (shows as 1 model in the list).
   - Leave empty to display all available models from `config.py`.

## Testing

The project includes **~88% test coverage** across core components:

- **Unit tests** for classifier logic and data handling
- **Integration tests** for the router and backend
- **Async tests** for streaming response generation

Run tests locally:
```bash
pip install -r requirements-dev.txt
pytest
```

## Demo

See it in action:

[![GeminiConnect Demo](https://img.youtube.com/vi/UlgQ3N1PCbo/0.jpg)](https://youtu.be/UlgQ3N1PCbo)

## Limitations

- Currently does not support the "Tools" feature in OpenWebUI.
- Built-in OpenWebUI web search **is supported**.

## License

This project is licensed under the [MIT License](LICENSE).