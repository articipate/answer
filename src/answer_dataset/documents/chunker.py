"""Text chunking."""

from typing import List

try:
    import tiktoken
    HAS_TIKTOKEN = True
except Exception:
    HAS_TIKTOKEN = False


class Chunker:
    def __init__(self, max_tokens: int = 6000, overlap: int = 200):
        self.max_tokens = max_tokens
        self.overlap = overlap
        if HAS_TIKTOKEN:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoding = None
        else:
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        if self.encoding:
            return len(self.encoding.encode(text))
        # Rough estimate: ~4 chars per token
        return len(text) // 4
    
    def chunk(self, text: str) -> List[str]:
        if not text.strip():
            return []
        
        total_tokens = self.count_tokens(text)
        if total_tokens <= self.max_tokens:
            return [text]
        
        chunks = []
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            if current_tokens + para_tokens > self.max_tokens and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                # Keep overlap from end of current chunk
                overlap_text = "\n\n".join(current_chunk[-2:]) if len(current_chunk) >= 2 else current_chunk[-1] if current_chunk else ""
                overlap_tokens = self.count_tokens(overlap_text)
                if overlap_tokens <= self.overlap:
                    current_chunk = [overlap_text]
                    current_tokens = overlap_tokens
                else:
                    current_chunk = []
                    current_tokens = 0
            current_chunk.append(para)
            current_tokens += para_tokens
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
