### GeminiConnect: An Advanced Proxy for Gemini API

**GeminiConnect** is a Python-based proxy server that adapts the Gemini API for use with any OpenAI-compatible clients, such as OpenWebUI.

The primary goal of this project is to resolve issues encountered when directly connecting OpenWebUI to Google's free Gemini API.

### What Problem Does It Solve?

If you've attempted to connect OpenWebUI directly to the Gemini API (especially the Pro model), you've likely faced strict rate limits.

1.  **Free Pro Version Limit:** The free Gemini Pro API has a severe limitation of only 2 requests per minute.
2.  **"Noisy" Clients:** OpenWebUI, for its internal operations (meta-requests, web search), sends numerous background requests. These requests quickly consume the entire minute's limit, making normal interaction with the model impossible.

### How Does GeminiConnect Fix It?

GeminiConnect acts as an "intelligent" intermediary that addresses both issues:

  * **Automatic Model Selection:** The proxy automatically determines the complexity of the user's request and decides which model to call — the fast **Flash** for simple tasks or the powerful **Pro** for complex ones.
  * **API Key Pool (Key Feature):** The project allows you to use not just one, but an *unlimited number* of Gemini API keys. You can simply use multiple Google accounts (get keys, for example, [here](https://aistudio.google.com)) and add all free keys to the configuration. GeminiConnect will automatically **switch to the next key** if the current one exhausts its rate limit (minute-based or daily quota). With just two API keys, the aggregated throughput of the pool **exceeds** the paid Gemini tier.

## 🎬 See the Demo in Action!

[![GeminiConnect Demo](https://img.youtube.com/vi/UlgQ3N1PCbo/0.jpg)](https://youtu.be/UlgQ3N1PCbo)

### 🛠️ Installation and Setup

The project is written in Python, utilizing **FastAPI** (for the API endpoint) and **httpx v2** (for asynchronous requests to Google).

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration and Start:**

      * Configure the `.env` file (at minimum, specify the port for the server).
      * Add your Gemini API keys to the configuration.
      * Start the server:
        ```bash
        python main.py
        ```

### 🔌 Connecting to OpenWebUI

1.  In OpenWebUI, navigate to "Connections" settings.
2.  Add a new "OpenAI-compatible" (External Endpoint).
3.  For the endpoint URL, enter: `http://localhost:YOUR_PORT/v1` (replace `YOUR_PORT` with the port you specified in `.env`).
4.  **Auth (Authentication):** `None`.
5.  **Model Name:** You can specify any name; it doesn't affect functionality (e.g., `gemini-connect`).

### ⚠️ Limitations

  * Currently, GeminiConnect **does not support** the "Tools" feature in OpenWebUI.
  * However, the **built-in OpenWebUI web search is supported** and, thanks to the key pool, will not trigger rate limit errors.

-----

### Found a Bug?

If something isn't working as expected, breaks, or you encounter any unforeseen issues, please don't hesitate to report it. The best way to do so is by creating an **Issue** in the project's GitHub repository.