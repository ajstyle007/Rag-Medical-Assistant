# 🧠 RAG-based Medical Assistant (WHO Data)

An AI-powered medical assistant that leverages **Retrieval-Augmented Generation (RAG)** on **World Health Organization (WHO)** data to provide accurate medical responses to user queries. The system is built using a modular architecture with separate Flask and FastAPI services, containerized with Docker, and deployed on Hugging Face Spaces.

#### Live App Link: https://musk12-rag-medical-bot.hf.space/assistant

<img width="1886" height="853" alt="Screenshot 2026-02-17 153532" src="https://github.com/user-attachments/assets/aff94968-43b0-4218-911d-af18a834b0e8" />


## Project Flow

![👤 (1)](https://github.com/user-attachments/assets/459fd34b-28b4-430a-b06c-116b26faa8f7)

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

## 🏥 Patient Management System

<img width="1888" height="821" alt="Screenshot 2026-02-17 152653" src="https://github.com/user-attachments/assets/b7103280-eb0d-4e01-96d9-6fbee3b15fc0" />


Along with the AI-powered medical query assistant, this project also includes a Patient Management Module built using FastAPI and MongoDB, enabling efficient handling of patient records.

- ✨ Features
- ✅ Create new patient records
- 📄 Retrieve patient details
- ✏️ Update existing patient information
- ❌ Delete patient records
- 🔄 Fully RESTful API design
- ⚡ High-performance asynchronous backend using FastAPI
- 🗄️ Scalable NoSQL database using MongoDB


## 📂 Project Structure

---

## 🛠️ Tech Stack

| Component      | Tool/Service         |
|----------------|----------------------|
| Frontend       | Flask                |
| Backend        | FastAPI              |
| LLMs           | Open Source Models   |
| Vector Search  | Pinecone             |
| Database       | MongoDB              |
| Containerization | Docker             |
| Hosting        | Hugging Face Spaces  |


