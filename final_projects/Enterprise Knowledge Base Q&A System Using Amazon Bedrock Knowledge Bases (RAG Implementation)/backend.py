"""
Backend Module — Amazon Bedrock Knowledge Base RAG Engine.

Provides the core retrieve-and-generate functionality using
Amazon Bedrock's Knowledge Base API via boto3.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from config import load_aws_config, load_bedrock_config, AWSConfig, BedrockConfig

logger = logging.getLogger(__name__)


# ── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class Citation:
    """Represents a single source citation from the knowledge base."""

    text: str
    source_uri: str
    source_name: str
    score: Optional[float] = None

    @property
    def display_name(self) -> str:
        """Return a clean display name from the source URI."""
        if self.source_name:
            return self.source_name
        # Extract filename from S3 URI or path
        return self.source_uri.rstrip("/").split("/")[-1] if self.source_uri else "Unknown"


@dataclass
class RAGResponse:
    """Structured response from the RAG pipeline."""

    answer: str
    citations: list[Citation] = field(default_factory=list)
    is_error: bool = False
    error_message: str = ""
    session_id: Optional[str] = None


# ── Bedrock RAG Client ──────────────────────────────────────────────────────

class BedrockRAGClient:
    """
    Client for Amazon Bedrock Knowledge Base retrieve-and-generate operations.

    Usage:
        client = BedrockRAGClient()
        response = client.query("What is our leave policy?")
        print(response.answer)
        for citation in response.citations:
            print(f"  Source: {citation.display_name}")
    """

    def __init__(
        self,
        aws_config: Optional[AWSConfig] = None,
        bedrock_config: Optional[BedrockConfig] = None,
    ):
        self.aws_config = aws_config or load_aws_config()
        self.bedrock_config = bedrock_config or load_bedrock_config()
        self._client = self._create_client()
        logger.info("BedrockRAGClient initialized successfully.")

    def _create_client(self):
        """Create and return a boto3 Bedrock Agent Runtime client."""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_config.access_key_id,
                aws_secret_access_key=self.aws_config.secret_access_key,
                region_name=self.aws_config.region,
            )
            client = session.client("bedrock-agent-runtime")
            logger.info("Bedrock Agent Runtime client created for region: %s", self.aws_config.region)
            return client
        except (ClientError, BotoCoreError) as e:
            logger.error("Failed to create Bedrock client: %s", e)
            raise

    def query(self, user_query: str, session_id: Optional[str] = None) -> RAGResponse:
        """
        Send a query to the Bedrock Knowledge Base and return a structured response.

        Args:
            user_query: The user's natural language question.
            session_id: Optional session ID for multi-turn conversations.

        Returns:
            RAGResponse: Contains the answer, citations, and metadata.
        """
        if not user_query or not user_query.strip():
            return RAGResponse(
                answer="",
                is_error=True,
                error_message="Please enter a valid question.",
            )

        logger.info("Processing query: %s", user_query[:100])

        try:
            # Build the request payload
            request_params = self._build_request(user_query, session_id)

            # Call the Bedrock Knowledge Base API
            response = self._client.retrieve_and_generate(**request_params)

            # Parse the response
            return self._parse_response(response)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error("AWS ClientError [%s]: %s", error_code, error_msg)

            # Provide user-friendly error messages
            user_message = self._get_user_friendly_error(error_code, error_msg)
            return RAGResponse(answer="", is_error=True, error_message=user_message)

        except BotoCoreError as e:
            logger.error("BotoCoreError: %s", e)
            return RAGResponse(
                answer="",
                is_error=True,
                error_message="A connection error occurred. Please check your AWS configuration and network.",
            )

        except Exception as e:
            logger.exception("Unexpected error during query processing")
            return RAGResponse(
                answer="",
                is_error=True,
                error_message=f"An unexpected error occurred: {str(e)}",
            )

    def _build_request(self, user_query: str, session_id: Optional[str]) -> dict:
        """Build the retrieve_and_generate API request payload."""
        # Prepend the guardrail system prompt to the user query
        augmented_query = (
            f"{self.bedrock_config.guardrail_prompt}\n\n"
            f"User Question: {user_query}"
        )

        request_params = {
            "input": {"text": augmented_query},
            "retrieveAndGenerateConfiguration": {
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": self.bedrock_config.knowledge_base_id,
                    "modelArn": self.bedrock_config.model_arn,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": self.bedrock_config.max_results,
                        }
                    },
                },
            },
        }

        if session_id:
            request_params["sessionId"] = session_id

        return request_params

    def _parse_response(self, response: dict) -> RAGResponse:
        """Parse the raw Bedrock API response into a structured RAGResponse."""
        # Extract the generated answer
        output = response.get("output", {})
        answer = output.get("text", "No answer was generated.")

        # Extract session ID for multi-turn
        session_id = response.get("sessionId")

        # Extract citations
        citations = []
        for citation_group in response.get("citations", []):
            retrieved_refs = citation_group.get("retrievedReferences", [])
            for ref in retrieved_refs:
                content = ref.get("content", {}).get("text", "")
                location = ref.get("location", {})

                # Handle different location types (S3, Web, etc.)
                source_uri = ""
                source_name = ""

                s3_location = location.get("s3Location", {})
                if s3_location:
                    source_uri = s3_location.get("uri", "")

                web_location = location.get("webLocation", {})
                if web_location:
                    source_uri = web_location.get("url", "")

                # Try to extract a friendly name
                metadata = ref.get("metadata", {})
                source_name = metadata.get("x-amz-bedrock-kb-source-file-name", "")
                if not source_name:
                    source_name = metadata.get("source", "")

                # Get relevance score if available
                score = ref.get("score")

                citations.append(
                    Citation(
                        text=content[:500],  # Truncate long passages
                        source_uri=source_uri,
                        source_name=source_name,
                        score=score,
                    )
                )

        logger.info(
            "Query processed successfully. Answer length: %d, Citations: %d",
            len(answer),
            len(citations),
        )

        return RAGResponse(
            answer=answer,
            citations=citations,
            session_id=session_id,
        )

    @staticmethod
    def _get_user_friendly_error(error_code: str, error_msg: str) -> str:
        """Map AWS error codes to user-friendly messages."""
        error_map = {
            "AccessDeniedException": (
                "Access denied. Please verify your AWS credentials have "
                "permission to access Bedrock Knowledge Bases."
            ),
            "ResourceNotFoundException": (
                "Knowledge Base not found. Please verify your "
                "BEDROCK_KNOWLEDGE_BASE_ID is correct."
            ),
            "ThrottlingException": (
                "Request was throttled. Please wait a moment and try again."
            ),
            "ValidationException": (
                f"Invalid request: {error_msg}"
            ),
            "ServiceQuotaExceededException": (
                "Service quota exceeded. Please try again later or request "
                "a quota increase in the AWS console."
            ),
        }
        return error_map.get(
            error_code,
            f"AWS Error ({error_code}): {error_msg}",
        )
