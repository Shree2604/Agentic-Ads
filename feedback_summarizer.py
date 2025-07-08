import os
import logging
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))


def summarize_feedback(feedback_docs: list) -> str:
  """
  Summarizes a list of feedback documents if there are more than three.

  Args:
      feedback_docs: A list of feedback documents.

  Returns:
      A summarized string of the feedback, or the original feedback if there are three or fewer documents.
  """
  if len(feedback_docs) > 3:
    logger.info(f"Summarizing {len(feedback_docs)} feedback documents.")

    feedback_texts = [doc.page_content for doc in feedback_docs]

    prompt_template = """
        You are an expert in analyzing user feedback for an ad copy generation tool.
        Summarize the following user feedback into a concise paragraph.
        Focus on the key issues and suggestions mentioned in the feedback.

        User Feedback:
        {feedback}

        Summary:
        """

    prompt = PromptTemplate.from_template(prompt_template)

    chain = prompt | llm | StrOutputParser()

    summary = chain.invoke({"feedback": "\n".join(feedback_texts)})

    return summary
  else:
    logger.info(
        "Not summarizing feedback as there are three or fewer documents.")
    return "\n".join([doc.page_content for doc in feedback_docs])
