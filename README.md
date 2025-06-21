# MedMoya_agents
Medical agents at your finger tips, built with Moya

# Multi-Agent Healthcare System

This is a multi-agent conversational system built using the [Moya Framework](https://github.com/moyahq/moya) and [Ollama](https://ollama.com). It supports:

*  Healthcare and home remedies advice
* Fetching healthcare products from Amazon, with help of product agent
* Setting reminders for medicine intake based on the memory and chat with Medvisor agent

# Demo 

![video](https://drive.google.com/uc?export=view&id=1sqNdSLcXf8qysezbWd60S-_Glo8JoXqO)(https://github.com/vanbitcase/MedMoya_agents/blob/main/med.png)

---

## ✅ Prerequisites

* Python 3.8 or above
* Windows 10/11 or Linux/macOS
* Access to the internet (for Amazon API)

---

## 🪄 Setup Instructions

### 1⃣ Step 1: Install Ollama and Run a Model

> Ollama allows you to run LLMs like `gemma`, `llama3`, or `mistral` locally.

#### ▶ Install Ollama

**For Windows / macOS / Linux:**
Go to [https://ollama.com/download](https://ollama.com/download) and follow the platform-specific installation instructions.

#### ▶ Pull the model (e.g., Gemma 4B)

```bash
ollama pull gemma:4b
```

You can also run:

```bash
ollama run gemma:4b
```

Make sure it's accessible at `http://localhost:11434`.

---

### 2⃣ Step 2: Install Moya Framework

Moya is on PyPI, but install it from source is recommended:

```bash
git clone https://github.com/moyahq/moya.git
cd moya
pip install .
```

> Make sure Moya's modules like `moya.agents`, `moya.orchestrators`, etc. are accessible.

---

### 3⃣ Step 3: Install Project Requirements

From your project root directory, run:

```bash
pip install -r requirements.txt
```

> If `winotify` fails (on Linux/macOS), comment it out in the `requirements.txt` or install only on Windows.

---

## 🚀 Running the Chat System

Run the main script:

```bash
python ollama_multiagent.py
```
* CMD View
![image](https://drive.google.com/uc?export=view&id=1aAsruwoix6LP56UYElZa2I7jV6PXdkPw) 
You'll be able to:
* Chat with a Medvisor for medical advice
* Automatically fetch related products from Amazon
* Set reminders with system notifications

---

## 📦 API Key for Amazon Search

This project uses **RapidAPI** for real-time Amazon product data.

* Get your API key from: [https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)
* Replace the placeholder in the code:

  ```python
  'x-rapidapi-key': "YOUR_API_KEY"
  ```

---

##  Example Output

```
Welcome to the Multi-Agent Chat System! (Type 'exit' to quit)
You can ask about:
1. Healthcare and Home remedies
2. Find Product regarding the discussion
3. Set a reminder for your medicine intake.
--------------------------------------------------
```

---

## Architecture Overview

* **Classifier Agent**: Routes queries to the correct agent
* **Medvisor Agent**: Suggests remedies and basic advice
* **Product Agent**: Suggests Amazon products based on the context and give you the latest price and most suitable product based on the memory.
* **Reminder Agent**: Sets reminders and schedules notifications for medicine intake.

---

## 💪 Tech Stack

* Python 3
* Ollama (`gemma:4b`)
* Moya Framework
* RapidAPI (Amazon data)
* `winotify` for notifications

---

## 👤 Author

**Vansh Rastogi** _Hardware + Software Developer_
