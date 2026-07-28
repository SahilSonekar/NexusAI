# 🌟 Nexus AI — Intelligent Customer Support Platform

Welcome to **Nexus AI** — an AI-powered customer support platform that delivers intelligent, real-time customer service through **Agentic Function Calling** and **Direct Context Injection**, built with **Django** and **Google Gemini**.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?style=for-the-badge&logo=django)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-orange?style=for-the-badge&logo=google)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=for-the-badge&logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=for-the-badge&logo=bootstrap)

</p>

---

## 🚀 Project Overview

Modern e-commerce platforms handle thousands of customer support requests every day — order status checks, refund requests, delivery tracking, warranty questions — most of which are repetitive and costly to handle manually.

**Nexus AI** solves this with **Maya**, an AI-powered virtual support assistant that understands natural language queries and autonomously resolves customer issues. Instead of relying solely on the language model's internal knowledge, Maya combines LLM reasoning with **live business data** pulled straight from a MySQL database.

- For order-specific questions, Gemini invokes Python functions through **Agentic Function Calling**, letting Django ORM fetch real-time information before a response is generated.
- For general company policies, product documentation, warranties, and FAQs, Maya uses **Direct Context Injection** — official business documentation supplied directly within the model's system prompt.

This hybrid architecture delivers accurate, explainable, production-oriented AI support without the added complexity of a vector database or a full Retrieval-Augmented Generation (RAG) pipeline.

---

## ✨ Key Highlights

* 🤖 AI-powered virtual customer support assistant ("Maya")
* 🧠 Google Gemini Function Calling
* 📦 Live order tracking using Django ORM
* 💰 Automated refund eligibility evaluation
* 🚚 Delivery status tracking
* 📚 Direct Context Injection for company policies
* 💬 Stateful multi-turn conversation memory
* 📝 Complete AI execution logging
* 🔐 Secure authentication using Django Authentication
* 🎨 Responsive Bootstrap user interface
* ⚡ Hybrid AI architecture focused on reliability and simplicity

---

## 🧩 Features

### 🤖 Intelligent Customer Support
Customers interact with Maya using natural language, just like speaking to a human support representative — e.g. *"Where is my order?"*, *"Can I request a refund?"*, *"What is my warranty period?"*. Maya determines intent, decides whether live data is required, invokes backend tools when necessary, and generates an accurate, conversational reply.

### 📦 Real-Time Order Tracking
For order-specific queries, Nexus AI retrieves information directly from the database rather than generating assumptions — current status, product details, shipping carrier, tracking number, delivery address, and days since the order was placed.

### 💰 Intelligent Refund Eligibility
Refund requests are evaluated with predefined business rules rather than left to the language model's discretion. A refund is approved only if:
- The order was placed within the last **30 days**
- The customer has made **fewer than two previous refund requests**

Otherwise, the request is denied per company policy — keeping every decision deterministic, transparent, and compliant.

### 🚚 Delivery Tracking
Maya retrieves shipment status, current location, estimated delivery date, delay reason, and carrier information before responding.

### 📚 Company Knowledge Base
General questions — warranty policies, refund policies, installation guidelines, maintenance instructions, product specs, FAQs — are answered using official documentation injected directly into Gemini's system prompt. Since the knowledge base is small and changes infrequently, this is simpler and more efficient than maintaining a vector database.

### 💬 Conversation Memory
Every conversation is stored in the database. Before processing a new message, prior history is reconstructed so Maya keeps context across multiple turns (e.g. resolving "it" to the customer's most recently discussed order).

### 📝 Agent Execution Logging
Every significant AI action — function calls, tool inputs/outputs, exceptions, final responses — is logged, making the reasoning pipeline observable and easy to debug and monitor.

---

## 🏗️ Architecture at a Glance

Nexus AI follows a **hybrid AI architecture**, combining LLM reasoning with deterministic backend logic. Rather than letting the LLM answer everything from memory, the system decides whether a query needs live business data, company documentation, or no external information at all.

```text
                    ┌──────────────────────┐
                    │      Customer        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Bootstrap Frontend │
                    │ HTML • CSS • JS      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Django Backend    │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
     Direct Context Injection        Google Gemini API
 (Policies & Documentation)          (LLM Reasoning)
                                           │
                              Function Call Required?
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     │                                           │
                    No                                          Yes
                     │                                           │
                     ▼                                           ▼
           Generate Response                    Execute Python Functions
                                                         │
                                                         ▼
                                                 Django ORM Queries
                                                         │
                                                         ▼
                                                      MySQL
                                                         │
                                                         ▼
                                            Function Result Returned
                                                         │
                                                         ▼
                                              Gemini Generates Reply
                                                         │
                                                         ▼
                                                Django Response
                                                         │
                                                         ▼
                                                     Customer
```

### 🤖 AI Workflow — Step by Step

1. **Customer Sends a Message** — the frontend passes the natural language query to Django.
2. **Conversation History** — Django retrieves previous messages so Maya understands context (e.g. "it" referring to a previously mentioned order).
3. **System Prompt Construction** — Django builds a prompt containing Maya's identity, company policies, warranty/refund rules, product docs, conversation history, and the latest message.
4. **Intent Understanding** — Gemini classifies the request (order query, refund, delivery tracking, warranty, FAQ, etc.) and decides whether a backend function is needed.
5. **Function Calling (when required)** — Gemini requests a function such as `get_order_details()`, `check_delivery_status()`, or `get_refund_history()`. Django executes it via the ORM against MySQL and returns the result.
6. **Direct Response (no function required)** — Policy/FAQ-type questions are answered directly from the documentation already in the system prompt.
7. **Response Generation** — Gemini combines live data or documentation with natural language reasoning to produce the final reply.
8. **Conversation Storage** — the customer message, assistant response, and timestamp are saved for future context.

### 🧠 Agentic Function Calling

Traditional chatbots often hallucinate or rely on outdated internal knowledge. Nexus AI avoids this by letting Gemini delegate to Django whenever live data is required:

```
Customer → "Where is my order?"
   → Gemini decides live data is needed
   → Calls get_order_details()
   → Django ORM → MySQL
   → Real order data returned
   → Gemini generates response
   → Customer receives accurate answer
```

### 📚 Direct Context Injection

Small, infrequently-changing knowledge (warranty policies, refund policies, installation guides, maintenance instructions, FAQs) is injected directly into Gemini's system prompt instead of powering a full RAG pipeline — no embeddings, no vector index, no retrieval step, just a simpler and faster path to an answer.

### 💡 Why This Hybrid Architecture?

| Responsibility                 | Handled By            |
| ------------------------------ | ---------------------- |
| Natural language understanding | Google Gemini          |
| Decision making                | Google Gemini          |
| Function selection             | Google Gemini          |
| Business rules                 | Django                 |
| Database operations            | Django ORM             |
| Data storage                   | MySQL                  |
| User authentication            | Django Authentication  |
| Conversation persistence       | Django                 |
| Execution logging              | Django                 |

This separation of concerns keeps the system reliable, easy to debug, and aligned with production-ready engineering practices.

---

## 💬 Example Conversations

**📦 Order Tracking**
```text
Customer: Where is my order?

Maya: Your order #ORD-10245 has been shipped and is currently in transit.
• Product: LG Dual Inverter AC
• Carrier: BlueDart
• Tracking Number: BD87492361
• Current Status: In Transit
• Estimated Delivery: 28 July
```

**💰 Refund Eligibility**
```text
Customer: Can I get a refund for my air conditioner?

Maya: I checked your purchase history.
✅ Your order was placed 18 days ago.
✅ You have no previous refund requests.
Your order is eligible for a refund according to our refund policy.
```

**📚 Product Information**
```text
Customer: How often should I clean my AC filter?

Maya: For optimal cooling performance, we recommend cleaning the air filter
every 2–4 weeks depending on usage.
```

**🚚 Delivery Status**
```text
Customer: Has my order been dispatched?

Maya: Yes. Your order was dispatched yesterday and is currently with
BlueDart Logistics.
Estimated Delivery: 29 July
Tracking Number: BD87361922
```

---

## 🆚 Why Agentic AI Instead of Traditional Chatbots?

| Traditional Chatbot               | Nexus AI                            |
| ---------------------------------- | ------------------------------------ |
| Static responses                   | Dynamic AI reasoning                 |
| Rule-based workflows               | Agentic decision making              |
| Limited personalization            | Customer-specific responses          |
| Cannot access live business data   | Retrieves real-time data from MySQL  |
| Difficult to scale                 | Easily extendable with new tools     |
| Higher risk of outdated responses  | Uses current business information    |

---

## 🔒 Security

* Django Authentication for secure user login
* CSRF protection for form submissions
* ORM-based database queries to prevent SQL Injection
* Environment variables for sensitive credentials
* Server-side business rule validation
* Secure API key management using `.env`
* Input validation before AI processing
* AI execution logging for auditing and debugging

Sensitive information such as API keys and database credentials are never hardcoded into the source code.

---


## 👨‍💻 Author

**Sahil Sonekar**

GitHub: [https://github.com/SahilSonekar](https://github.com/SahilSonekar)
---

<p align="center">
Built with ❤️ by <strong>Sahil Sonekar</strong>
</p>
