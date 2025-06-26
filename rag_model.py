from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import pinecone 
from langchain_pinecone import Pinecone as LangchainPinecone
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain.embeddings.base import Embeddings
from openai import OpenAI
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import PrivateAttr
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

load_dotenv()


class CustomAPIChatLLM(BaseChatModel):
    model_id: str  # Pydantic field
    _client: any = PrivateAttr()  # Private attribute (not a model field)

    def __init__(self, client, model_id, **kwargs):
        super().__init__(model_id=model_id, **kwargs)
        self._client = client  # store in private attr

    @property
    def _llm_type(self) -> str:
        return "custom_api_chat_llm"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        # Convert messages to dict
        text_messages = [
                {
                    "role": "user" if m.type == "human" else "assistant",
                    "content": m.content
                }
                for m in messages
            ]

        # Call your API
        completion = self._client.chat.completions.create(
            model=self.model_id,
            messages=text_messages,
        )
        
        content = completion.choices[0].message.content
        # Return as ChatResult
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )

llm_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
  base_url="https://api.a4f.co/v1",
  api_key=llm_key,
)

llm = CustomAPIChatLLM(client=client, model_id="provider-3/claude-3.5-haiku")



CUSTOM_PROMPT_TEMPLATE = """
You are a helpful, accurate, and knowledgeable AI medical assistant. Your role is to answer questions 
strictly related to health, medicine, symptoms, treatments, medications, diagnoses, and other medically 
relevant topics. Use only the most accurate and concise medical information available from the provided documents.

Respond according to the following rules:

1. **Non-medical questions**:  
   If the user asks a question that is *not* related to medicine or healthcare, politely respond with:  
   "I'm here to help with medical-related questions. For other topics, I’m afraid I can't assist."

2. **Greetings**:  
   If the user greets you (e.g., "Hi", "Hello", "Good morning", etc.), reply with a warm and polite greeting such as:  
   "Hello! How can I assist you with your medical concerns today?"

3. **Gratitude**:  
   If the user expresses gratitude (e.g., "thank you", "thanks", "thanks a lot", "thx", "okay thank you","ty", "thank u", "okay" etc.), respond with:  
   "You're welcome! Let me know if there's anything else I can help you with. 😊"  
   Do **not** retrieve documents or provide further answers in such cases.

4. **Insufficient information**:  
   If the answer is not clearly found in the provided documents, or you are uncertain, respond with:  
   "I'm sorry, I don't have enough information to answer that accurately."

5. **Important constraints**:  
   - Never make up or guess answers.  
   - Avoid providing legal, financial, or any non-medical advice.

Always keep your responses clear, professional, and empathetic.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""


def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "query"])
    return prompt

# ============================================================================

# api_key = os.getenv("PINECONE_API_KEY")

api_key = os.getenv("PINECONE_API_KEY")

# Step 1: Create Pinecone client
pc = pinecone.Pinecone(api_key=api_key)

# Step 2: Create index (if not exists)
index_name = "rag-index3"
# index = pc.Index(index_name)
dimension = 768  # Update to your embedding model dimension


# Check if index already exists
if index_name not in [index.name for index in pc.list_indexes()]:
    # Recreate with correct dimension
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",  # or "gcp"
            region="us-east-1"  # adjust based on your Pinecone region
        )
    )

index = pc.Index(index_name)

# Embedding model
# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
embedding_model = GoogleGenerativeAIEmbeddings(
    model = "models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    dimension=384
)


# Langchain Pinecone DB
db = LangchainPinecone(
    index=index,
    embedding=embedding_model,
    text_key="text"  # make sure your vectors have this metadata field
)


qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
)

# Now invoke with a single query
def ask_question(user_query):
    try:
        response = qa_chain.invoke({'query': user_query})
        return response.get("result", "Sorry, I couldn't understand that.")
    except Exception as e:
        return f"An error occurred: {str(e)}"