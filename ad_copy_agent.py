import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

# Define the input/output schema for LangGraph nodes
class RewriteState(TypedDict):
    input_text: str
    tone: str
    platform: str
    rag_context: str
    rewritten_ad: str
    evaluation_result: str

# Build your LLM with the API key from environment variables
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Create a prompt template for the rewriting step
rewrite_prompt = ChatPromptTemplate.from_template(
    """
        You are an expert ad copywriter. Your goal is to rewrite the given ad text.
        Original Ad: {input_text}
        Target Tone: {tone}
        Target Platform: {platform}

        Consider the following best practices and context for ad copywriting:
        {rag_context}

        Rewritten Ad:
        """
    )

# Create a runnable chain
rewrite_chain: Runnable = (
    rewrite_prompt
    | llm
    | StrOutputParser()
)

# Define the LangGraph node
def rewrite_node(state: RewriteState) -> RewriteState:
    print("Executing RewriteAgent")
    rewritten_ad = rewrite_chain.invoke({
        "input_text": state["input_text"],
        "tone": state["tone"],
        "platform": state["platform"],
        "rag_context": state["rag_context"]
    })
    return {**state, "rewritten_ad": rewritten_ad}