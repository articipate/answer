"""Dataset generator."""

import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from answer_dataset.providers.registry import get_provider
from answer_dataset.providers.base import BaseProvider
from answer_dataset.models import Document, GenerationConfig, DatasetRow, GenerationMode
from answer_dataset.pipeline.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from answer_dataset.pipeline.validator import ResponseValidator
from answer_dataset.pipeline.schema import SchemaHandler


class Generator:
    def __init__(self, provider_config, gen_config: GenerationConfig):
        self.provider = get_provider(
            provider_config.provider_type.value,
            api_key=provider_config.api_key,
            base_url=provider_config.base_url or "",
            model=provider_config.model,
        )
        self.gen_config = gen_config
        self.rows: List[DatasetRow] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.cancelled = False
    
    def cancel(self):
        self.cancelled = True
    
    async def generate(self, documents: List[Document], 
                       progress_callback: Optional[Callable] = None,
                       log_callback: Optional[Callable] = None) -> List[DatasetRow]:
        self.rows = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.cancelled = False
        
        for doc_idx, doc in enumerate(documents):
            if self.cancelled:
                break
            
            if log_callback:
                log_callback(f"Processing: {doc.name}")
            
            if progress_callback:
                progress_callback(doc_idx, len(documents), f"Processing {doc.name}")
            
            try:
                if self.gen_config.mode == GenerationMode.PER_DOCUMENT:
                    await self._generate_per_document(doc, log_callback)
                elif self.gen_config.mode == GenerationMode.PER_CHUNK:
                    await self._generate_per_chunk(doc, log_callback)
                elif self.gen_config.mode == GenerationMode.MULTI_PER_CHUNK:
                    await self._generate_multi_per_chunk(doc, log_callback)
            except Exception as e:
                if log_callback:
                    log_callback(f"Error processing {doc.name}: {e}")
        
        return self.rows
    
    async def _generate_per_document(self, doc: Document, log_callback=None):
        content = doc.text
        if not content.strip():
            return
        
        prompt = self._build_prompt(doc.name, content)
        result = await self.provider.complete(
            SYSTEM_PROMPT,
            prompt,
            temperature=0.7,
        )
        
        if result.error:
            if log_callback:
                log_callback(f"API error: {result.error}")
            return
        
        self.total_input_tokens += result.input_tokens
        self.total_output_tokens += result.output_tokens
        
        rows, err = ResponseValidator.parse_response(result.text)
        if err:
            if log_callback:
                log_callback(f"Parse error: {err}")
            return
        
        for row in rows:
            row = ResponseValidator.clean_row(row)
            if self.gen_config.add_source:
                row["_source"] = doc.name
            self.rows.append(DatasetRow(data=row, source=doc.name))
    
    async def _generate_per_chunk(self, doc: Document, log_callback=None):
        for idx, chunk in enumerate(doc.chunks):
            if self.cancelled:
                break
            
            prompt = self._build_prompt(doc.name, chunk, chunk_index=idx, total_chunks=len(doc.chunks))
            result = await self.provider.complete(
                SYSTEM_PROMPT,
                prompt,
                temperature=0.7,
            )
            
            if result.error:
                if log_callback:
                    log_callback(f"API error (chunk {idx}): {result.error}")
                continue
            
            self.total_input_tokens += result.input_tokens
            self.total_output_tokens += result.output_tokens
            
            rows, err = ResponseValidator.parse_response(result.text)
            if err:
                if log_callback:
                    log_callback(f"Parse error (chunk {idx}): {err}")
                continue
            
            for row in rows:
                row = ResponseValidator.clean_row(row)
                if self.gen_config.add_source:
                    row["_source"] = doc.name
                    row["_chunk"] = idx
                self.rows.append(DatasetRow(data=row, source=doc.name, chunk_index=idx))
    
    async def _generate_multi_per_chunk(self, doc: Document, log_callback=None):
        for idx, chunk in enumerate(doc.chunks):
            if self.cancelled:
                break
            
            row_count_instr = f"Generate up to {self.gen_config.rows_per_chunk} diverse rows from this chunk."
            prompt = self._build_prompt(doc.name, chunk, chunk_index=idx, total_chunks=len(doc.chunks), row_count_instr=row_count_instr)
            result = await self.provider.complete(
                SYSTEM_PROMPT,
                prompt,
                temperature=0.8,
            )
            
            if result.error:
                if log_callback:
                    log_callback(f"API error (chunk {idx}): {result.error}")
                continue
            
            self.total_input_tokens += result.input_tokens
            self.total_output_tokens += result.output_tokens
            
            rows, err = ResponseValidator.parse_response(result.text)
            if err:
                if log_callback:
                    log_callback(f"Parse error (chunk {idx}): {err}")
                continue
            
            for row in rows[:self.gen_config.rows_per_chunk]:
                row = ResponseValidator.clean_row(row)
                if self.gen_config.add_source:
                    row["_source"] = doc.name
                    row["_chunk"] = idx
                self.rows.append(DatasetRow(data=row, source=doc.name, chunk_index=idx))
                if self.gen_config.max_rows and len(self.rows) >= self.gen_config.max_rows:
                    break
            if self.gen_config.max_rows and len(self.rows) >= self.gen_config.max_rows:
                break
    
    def _build_prompt(self, doc_name: str, content: str, chunk_index: int = -1, total_chunks: int = 1, row_count_instr: str = ""):
        source_info = f"Chunk {chunk_index + 1}/{total_chunks}" if chunk_index >= 0 and total_chunks > 1 else ""
        
        format_instruction = "Follow this structure exactly:"
        if self.gen_config.example_row:
            format_instruction += f"\n{json.dumps(self.gen_config.example_row, indent=2, ensure_ascii=False)}"
        elif self.gen_config.user_prompt:
            format_instruction = self.gen_config.user_prompt
        
        schema_instruction = ""
        if self.gen_config.json_schema:
            schema_instruction = f"JSON Schema:\n{json.dumps(self.gen_config.json_schema, indent=2, ensure_ascii=False)}"
        
        example_instruction = ""
        if self.gen_config.example_row and not self.gen_config.user_prompt:
            example_instruction = f"Example row format:\n{json.dumps(self.gen_config.example_row, ensure_ascii=False)}"
        
        additional_instructions = self.gen_config.system_prompt or ""
        if self.gen_config.language and self.gen_config.language != "auto":
            additional_instructions += f"\nGenerate content in {self.gen_config.language}."
        
        return USER_PROMPT_TEMPLATE.format(
            document_name=doc_name,
            source_info=source_info,
            format_instruction=format_instruction,
            schema_instruction=schema_instruction,
            example_instruction=example_instruction,
            additional_instructions=additional_instructions,
            content=content[:50000],  # Limit content size
            row_count_instruction=row_count_instr,
        )
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_rows": len(self.rows),
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
        }
