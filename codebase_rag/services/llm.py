from __future__ import annotations

from typing import TYPE_CHECKING
import re

from loguru import logger
from pydantic_ai import Agent, DeferredToolRequests, Tool

from .. import constants as cs
from .. import exceptions as ex
from .. import logs as ls
from ..config import ModelConfig, settings
from ..prompts import (
    build_cypher_system_prompt,
    build_local_cypher_system_prompt,
    build_rag_orchestrator_prompt,
)
from ..providers.base import get_provider_from_config

if TYPE_CHECKING:
    from pydantic_ai.models import Model


def _create_provider_model(config: ModelConfig) -> Model:
    provider = get_provider_from_config(config)
    return provider.create_model(config.model_id)


def _clean_cypher_response(response_text: str) -> str:
    """
    Robustly extracts Cypher queries from LLM output.
    """
    # 1. Priority: Extract from markdown code blocks
    markdown_match = re.search(r'```(?:cypher)?\s*\n?(.*?)\n?```', response_text, re.DOTALL | re.IGNORECASE)
    if markdown_match:
        query = markdown_match.group(1).strip()
        # Even inside code blocks, sometimes LLMs put comments/explanations
        # Use the brutal extraction on the block content just in case, but usually it's clean
        try:
            extracted = _extract_cypher_brutal(query)
            return _ensure_semicolon(extracted)
        except ValueError:
            # If brutal extraction fails (e.g. valid query but weird formatting), return the block content
            pass
        return _ensure_semicolon(query)

    # 2. Fallback: Brutal extraction from raw text
    try:
        query = _extract_cypher_brutal(response_text)
        return _ensure_semicolon(query)
    except ValueError:
        # 3. Last Resort: Basic stripping if brutal extraction fails
        # This handles cases where the query might be just "MATCH (n) RETURN n" with no newlines
        query = response_text.strip()
        if query.lower().startswith(cs.CYPHER_PREFIX):
            query = query[len(cs.CYPHER_PREFIX):].strip()
        return _ensure_semicolon(query)

def _extract_cypher_brutal(text: str) -> str:
    lines = text.split('\n')
    start_idx = None
    
    # Find start: Look for standard Cypher clauses at start of line
    # Added CREATE, MERGE, UNWIND just in case, though usually read-only
    cypher_start_pattern = r'^\s*(MATCH|WITH|CALL|RETURN|CREATE|MERGE|UNWIND)\b'
    
    for i, line in enumerate(lines):
        # Check if line is a Cypher command
        if re.match(cypher_start_pattern, line, re.IGNORECASE):
            # Check it's not a conversational list item like "1. MATCH..."
            if not re.match(r'^\s*\d+\.', line):
                start_idx = i
                break
    
    if start_idx is None:
        raise ValueError("No Cypher query found")
    
    # Find end: Look for conversational text or end of code block
    end_idx = len(lines)
    
    # Keywords that definitively start a conversational explanation
    conversational_starts = r'^(Note|This query|Explanation|Here|If you|The query|[0-9]+\.|Analysis|Result|Or|Alternatively|You can)'
    
    # Keywords that definitively continue a Cypher query
    cypher_continuation = r'^\s*(MATCH|WHERE|AND|OR|RETURN|LIMIT|ORDER|WITH|SKIP|UNWIND|CALL|DELETE|DETACH|SET|REMOVE|CREATE|MERGE|ON CREATE|ON MATCH)\b'
    
    for i in range(start_idx + 1, len(lines)):
        line = lines[i].strip()
        
        # Immediate stop if we hit a conversational marker
        if re.match(conversational_starts, line, re.IGNORECASE):
            end_idx = i
            break
            
        # Heuristic: If we hit a blank line, check the NEXT line.
        # If the next line doesn't look like Cypher, we assume the query ended at the blank line.
        if not line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not re.match(cypher_continuation, next_line, re.IGNORECASE):
                # But wait, is the next line a comment? // or /*
                if not next_line.startswith('//') and not next_line.startswith('/*'):
                    end_idx = i
                    break
    
    query = '\n'.join(lines[start_idx:end_idx])
    return query.strip()

def _ensure_semicolon(query: str) -> str:
    # Remove any existing semicolon to avoid double ;;
    query = query.rstrip(';')
    return query + cs.CYPHER_SEMICOLON


class CypherGenerator:
    def __init__(self, project_id: str) -> None:
        try:
            config = settings.active_cypher_config
            llm = _create_provider_model(config)

            from ..prompts import (
                build_cypher_system_prompt,
                build_local_cypher_system_prompt,
            )

            system_prompt = (
                build_local_cypher_system_prompt(project_id)
                if config.provider == cs.Provider.OLLAMA
                else build_cypher_system_prompt(project_id)
            )

            self.agent = Agent(
                model=llm,
                system_prompt=system_prompt,
                output_type=str,
                retries=settings.AGENT_RETRIES,
            )
        except Exception as e:
            raise ex.LLMGenerationError(ex.LLM_INIT_CYPHER.format(error=e)) from e

    async def generate(
        self, natural_language_query: str, project_id: str | None = None
    ) -> str:
        logger.info(ls.CYPHER_GENERATING.format(query=natural_language_query))

        if project_id:
            natural_language_query = (
                f"For project with id '{project_id}', {natural_language_query}"
            )
        try:
            result = await self.agent.run(natural_language_query)
            if (
                not isinstance(result.output, str)
                or cs.CYPHER_MATCH_KEYWORD not in result.output.upper()
            ):
                raise ex.LLMGenerationError(
                    ex.LLM_INVALID_QUERY.format(output=result.output)
                )

            query = _clean_cypher_response(result.output)
            logger.info(ls.CYPHER_GENERATED.format(query=query))
            return query
        except Exception as e:
            logger.error(ls.CYPHER_ERROR.format(error=e))
            raise ex.LLMGenerationError(ex.LLM_GENERATION_FAILED.format(error=e)) from e


def create_rag_orchestrator(tools: list[Tool]) -> Agent:
    try:
        config = settings.active_orchestrator_config
        llm = _create_provider_model(config)

        return Agent(
            model=llm,
            system_prompt=build_rag_orchestrator_prompt(tools),
            tools=tools,
            retries=settings.AGENT_RETRIES,
            output_retries=settings.ORCHESTRATOR_OUTPUT_RETRIES,
            output_type=[str, DeferredToolRequests],
        )
    except Exception as e:
        raise ex.LLMGenerationError(ex.LLM_INIT_ORCHESTRATOR.format(error=e)) from e
