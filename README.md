# 🧠 RAG-based Medical Assistant (WHO Data)

An AI-powered medical assistant that leverages **Retrieval-Augmented Generation (RAG)** on **World Health Organization (WHO)** data to provide accurate medical responses to user queries. The system is built using a modular architecture with separate Flask and FastAPI services, containerized with Docker, and deployed on Hugging Face Spaces.

---

## 🚀 Features

- 🧾 **Flask Frontend**  
  - User form for submitting symptoms/questions  
  - Displays LLM-generated answers

- ⚡ **FastAPI Backend**  
  - Handles query processing via APIs  
  - Two LLMs:
    - LLM 1 → Generates a search query from user input  
    - LLM 2 → Generates medical response based on WHO documents

- 🔍 **Pinecone Vector DB**  
  - Performs semantic search to retrieve relevant WHO document chunks  

- 🗂️ **MongoDB Database**  
  - Stores patient data (name, age, symptoms, query, diagnosis)

- 📦 **Dockerized Architecture**  
  - Both Flask and FastAPI apps run in separate Docker containers

- ☁️ **Deployed on Hugging Face Spaces**  
  - Easily accessible via public URLs

---

## 📂 Project Structure


