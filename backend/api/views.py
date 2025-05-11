from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse, FileResponse
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
import re

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
    You are a chatbot with Git repository analysis assistant capabilities. You help users understand codebases by analyzing Git history,
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

# Flag to indicate if repository knowledge has been requested
repo_knowledge_requested = False


def initialize_retrieval_chain_wrapper():
    """Initialize retrieval chain and assign it to the global variable"""
    global retrieval_chain

    # Only initialize if not already initialized
    if retrieval_chain is None:
        success, chain_or_error = git_service.initialize_retrieval_chain()
        if success:
            retrieval_chain = chain_or_error
            logger.info("Retrieval chain initialized and assigned to global variable")
            return True
        else:
            logger.error(f"Failed to initialize retrieval chain: {chain_or_error}")
            return False
    else:
        logger.info("Retrieval chain already initialized, skipping")
        return True


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def chat_with_llm(request):
    """Processes chat messages and returns responses."""
    global retrieval_chain, repo_knowledge_requested
    print(request.data)
    user_message = request.data.get("message", "")
    if not user_message:
        return Response({"error": "No message provided"}, status=400)

    logger.info(f"Received user message: {user_message}")

    # Check if the message indicates a request to analyze a repository
    is_analysis_intent, github_url = git_service.detect_analysis_intent(user_message)
    print("Analysis intent:" + is_analysis_intent.__str__())
    if is_analysis_intent and github_url:
        # Run the analysis workflow if intent is detected
        def workflow_generator_wrapper():
            workflow_generator = git_service.run_analysis_workflow(github_url)

            # Yield all the updates from the original generator
            for update in workflow_generator():
                yield update

            # After workflow completes, initialize the retrieval chain
            if git_service.state.analysis_complete:
                yield "Setting up retrieval system...\n"
                if initialize_retrieval_chain_wrapper():
                    yield "Retrieval system is ready! You can now ask questions about the repository.\n"
                    # Mark that repository knowledge is now available and requested
                    global repo_knowledge_requested
                    repo_knowledge_requested = True
                else:
                    yield "Failed to initialize retrieval system. Please try again.\n"

        # Reset retrieval chain when analyzing a new repository
        retrieval_chain = None
        # Reset the flag since we're analyzing a new repository
        repo_knowledge_requested = False
        return StreamingHttpResponse(
            workflow_generator_wrapper(), content_type="text/plain"
        )

    # Handle normal chat queries
    def stream_response():
        global retrieval_chain, repo_knowledge_requested

        # Check if this query potentially needs repository knowledge
        if git_service.state.vector_db_loaded:
            # Check if this is a first request for repository knowledge
            if not repo_knowledge_requested:
                # This is the first query that might need repository knowledge
                # We'll try to identify if it's about the repository
                from .utils import extract_github_url

                # Simple heuristic - check if message mentions "repository", "code", "file", etc.
                repo_keywords = [
                    "repository",
                    "code",
                    "file",
                    "function",
                    "class",
                    "method",
                    "git",
                    "commit",
                    "repo",
                    "project",
                    "directory",
                    "module",
                ]

                is_repo_query = any(
                    keyword in user_message.lower() for keyword in repo_keywords
                )

                # If repository name is available, check if it's mentioned
                if git_service.state.current_repo_name:
                    repo_name = git_service.state.current_repo_name.lower()
                    is_repo_query = is_repo_query or repo_name in user_message.lower()

                if is_repo_query:
                    # This is a repository-specific query, set the flag for all future queries
                    repo_knowledge_requested = True
                    logger.info(
                        "Repository knowledge requested - all future queries will use RAG"
                    )

                    # Initialize the retrieval chain if needed
                    if retrieval_chain is None:
                        logger.info(
                            "Initializing retrieval chain for first repository query"
                        )
                        initialize_retrieval_chain_wrapper()

        # Decision logic for which chain to use
        if repo_knowledge_requested and git_service.state.vector_db_loaded:
            # Repository knowledge was requested previously, use RAG for all future queries
            if retrieval_chain is None:
                # Ensure retrieval chain is initialized
                initialize_retrieval_chain_wrapper()

            if retrieval_chain:
                # Use RAG-based answering
                try:
                    logger.info(f"Using retrieval chain to answer: {user_message}")
                    response = retrieval_chain.invoke({"question": user_message})
                    answer = response["answer"]
                    logger.info(f"Got answer from retrieval chain")
                except Exception as e:
                    logger.error(f"Error using retrieval chain: {e}")
                    # Fallback to regular conversation
                    response = conversation.predict(input=user_message)
                    answer = response
            else:
                # Fallback if initialization failed
                logger.warning(
                    "Failed to initialize retrieval chain, using regular conversation"
                )
                response = conversation.predict(input=user_message)
                answer = response
        else:
            # No repository knowledge requested yet or no repository loaded
            logger.info(f"Using regular conversation for: {user_message}")
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
    global retrieval_chain
    return JsonResponse(
        {
            "status": "healthy",
            "message": "Git analysis system is online",
            "repository_loaded": git_service.state.current_repo_name is not None,
            "current_repo": git_service.state.current_repo_name,
            "retrieval_chain_active": retrieval_chain is not None,
        }
    )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def repository_status(request):
    """Get current repository status"""
    global retrieval_chain, repo_knowledge_requested
    return JsonResponse(
        {
            "current_repo": git_service.state.current_repo_name,
            "analysis_complete": git_service.state.analysis_complete,
            "vector_db_loaded": git_service.state.vector_db_loaded,
            "retrieval_chain_active": retrieval_chain is not None,
            "repo_knowledge_requested": repo_knowledge_requested,
        }
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_retrieval_chain(request):
    """Force re-initialization of retrieval chain"""
    global retrieval_chain, repo_knowledge_requested
    # Only reset if we actually have one
    if retrieval_chain is not None:
        retrieval_chain = None
        logger.info("Retrieval chain reset to None")

    # Reset the flag as well
    repo_knowledge_requested = False
    logger.info("Repository knowledge requested flag reset")

    # Initialize a new one if requested
    if request.data.get("initialize", False):
        success = initialize_retrieval_chain_wrapper()
        if success:
            repo_knowledge_requested = True
    else:
        success = True

    return JsonResponse(
        {
            "success": success,
            "retrieval_chain_active": retrieval_chain is not None,
            "repo_knowledge_requested": repo_knowledge_requested,
        }
    )


# New view to list subdirectories in the graphs path
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_graph_folders(request):
    base_path = "/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/backend/git_file_history_output/graphs"
    try:
        folders = [
            f
            for f in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, f))
        ]
        return JsonResponse({"folders": sorted(folders)})
    except Exception as e:
        logger.error(f"Failed to list graph folders: {str(e)}")
        return JsonResponse({"error": f"Failed to list folders: {str(e)}"}, status=500)


# New view to get details of a specific graph folder
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_graph_folder_details(request, folder_name):
    base_path = "/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/backend/git_file_history_output/graphs"
    folder_path = os.path.join(base_path, folder_name)
    
    try:
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return JsonResponse({"error": "Folder not found"}, status=404)
        
        # Find the files in the folder
        file_image = None
        functional_image = None
        dependencies_file = None
        
        for file in os.listdir(folder_path):
            if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".svg"):
                if "file" in file.lower() or "structure" in file.lower():
                    file_image = file
                elif "function" in file.lower() or "call" in file.lower():
                    functional_image = file
            elif file == "dependencies.json":
                dependencies_file = file
        
        # Load dependencies if available
        dependencies = {}
        if dependencies_file:
            with open(os.path.join(folder_path, dependencies_file), 'r') as f:
                dependencies = json.load(f)
        
        return JsonResponse({
            "folder": folder_name,
            "fileImage": file_image,
            "functionalImage": functional_image,
            "dependencies": dependencies
        })
        
    except Exception as e:
        logger.error(f"Failed to get graph folder details: {str(e)}")
        return JsonResponse({"error": f"Failed to get folder details: {str(e)}"}, status=500)


# Serve static files from graph folders directly
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def serve_graph_file(request, folder, filename):
    base_path = "/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/backend/git_file_history_output/graphs"
    file_path = os.path.join(base_path, folder, filename)
    
    try:
        if not os.path.exists(file_path):
            return JsonResponse({"error": "File not found"}, status=404)
        
        return FileResponse(open(file_path, 'rb'))
    except Exception as e:
        logger.error(f"Failed to serve graph file: {str(e)}")
        return JsonResponse({"error": f"Failed to serve file: {str(e)}"}, status=500)