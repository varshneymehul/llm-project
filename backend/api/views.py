from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import time
import json
import os
import logging

# Import our services
from .git_analysis_service import GitAnalysisService
from .utils import extract_github_url

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create service instance
git_service = GitAnalysisService()

# Initialize conversation for chat
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

chat_prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    template="""
    You are a Git repository analysis assistant. You help users understand codebases by analyzing Git history,
    summarizing files, and answering questions about code changes and functionality.

    Conversation so far:
    {chat_history}
    Human: {input}
    Assistant:
    """,
)

chat_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversation = ConversationChain(
    llm=git_service.get_llm(temperature=0.0),
    verbose=True,
    memory=chat_memory,
    prompt=chat_prompt,
)

# Global retrieval chain
retrieval_chain = None


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def chat_with_llm(request):
    """Processes chat messages and returns responses."""
    global retrieval_chain
    print(request.data)
    user_message = request.data.get("message", "")
    if not user_message:
        return Response({"error": "No message provided"}, status=400)

    logger.info(f"Received user message: {user_message}")

    # Check if the message indicates a request to analyze a repository
    is_analysis_intent, github_url = git_service.detect_analysis_intent(user_message)

    if is_analysis_intent and github_url:
        # Run the analysis workflow if intent is detected
        workflow_generator = git_service.run_analysis_workflow(github_url)
        return StreamingHttpResponse(workflow_generator(), content_type="text/plain")

    # Handle normal chat queries using the appropriate system
    def stream_response():
        if retrieval_chain and git_service.state.vector_db_loaded:
            # Use RAG-based answering when we have a repository loaded
            response = retrieval_chain.invoke({"question": user_message})
            answer = response["answer"]
        else:
            # Use regular conversation for general chat
            response = conversation.predict(input=user_message)
            answer = response

        # Stream the response word by word
        for word in answer.split():
            yield word + " "
            time.sleep(0.02)  # small delay for smoother frontend streaming

    return StreamingHttpResponse(stream_response(), content_type="text/plain")


@api_view(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse(
        {
            "status": "healthy",
            "message": "Git analysis system is online",
            "repository_loaded": git_service.state.current_repo_name is not None,
            "current_repo": git_service.state.current_repo_name,
        }
    )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def repository_status(request):
    """Get current repository status"""
    return JsonResponse(
        {
            "current_repo": git_service.state.current_repo_name,
            "analysis_complete": git_service.state.analysis_complete,
            "vector_db_loaded": git_service.state.vector_db_loaded,
        }
    )
