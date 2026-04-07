"""
Configuration Module for Amazon Bedrock Knowledge Base RAG System.

Loads environment variables and provides centralized configuration
for AWS credentials, Bedrock settings, and application parameters.
"""

import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# ── Load .env file ──────────────────────────────────────────────────────────
load_dotenv()

# ── Logging Setup ───────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AWSConfig:
    """Immutable AWS configuration loaded from environment variables."""

    access_key_id: str
    secret_access_key: str
    region: str


@dataclass(frozen=True)
class BedrockConfig:
    """Immutable Bedrock Knowledge Base configuration."""

    knowledge_base_id: str
    model_arn: str
    max_results: int
    guardrail_prompt: str


def load_aws_config() -> AWSConfig:
    """
    Load and validate AWS credentials from environment variables.

    Returns:
        AWSConfig: Validated AWS configuration.

    Raises:
        EnvironmentError: If any required variable is missing.
    """
    required_vars = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "AWS_REGION": os.getenv("AWS_REGION", "ap-south-1"),
    }

    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please set them in your .env file or system environment."
        )

    config = AWSConfig(
        access_key_id=required_vars["AWS_ACCESS_KEY_ID"],
        secret_access_key=required_vars["AWS_SECRET_ACCESS_KEY"],
        region=required_vars["AWS_REGION"],
    )
    logger.info("AWS configuration loaded successfully (region: %s)", config.region)
    return config


def load_bedrock_config() -> BedrockConfig:
    """
    Load and validate Bedrock Knowledge Base configuration.

    Returns:
        BedrockConfig: Validated Bedrock configuration.

    Raises:
        EnvironmentError: If Knowledge Base ID is missing.
    """
    kb_id = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID")
    if not kb_id:
        raise EnvironmentError(
            "Missing BEDROCK_KNOWLEDGE_BASE_ID. "
            "Set it in your .env file or system environment."
        )

    # Default to Claude 3 Sonnet — adjust the ARN for your region/model
    region = os.getenv("AWS_REGION", "ap-south-1")
    default_model_arn = (
        f"arn:aws:bedrock:{region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
    )

    config = BedrockConfig(
        knowledge_base_id=kb_id,
        model_arn=os.getenv("BEDROCK_MODEL_ARN", default_model_arn),
        max_results=int(os.getenv("BEDROCK_MAX_RESULTS", "5")),
        guardrail_prompt=(
            "You are a helpful enterprise assistant. "
            "Answer ONLY using the information provided in the retrieved documents. "
            "If the answer is not found in the documents, clearly state: "
            "'I don't have enough information in the knowledge base to answer this question.' "
            "Always cite the source document when providing an answer. "
            "Do not make up or hallucinate any information."
        ),
    )
    logger.info(
        "Bedrock configuration loaded (KB: %s, Model: %s)",
        config.knowledge_base_id,
        config.model_arn,
    )
    return config
