from typing import List, Dict, Any

class DocumentParser:
    @staticmethod
    def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Takes a long string of text and chops it into smaller pieces (chunks)
        with a sliding window overlap so context isn't lost at the edges.
        """
        chunks = []
        
        # If the text is already smaller than our chunk size, no splitting needed!
        if len(text) <= chunk_size:
            return [text.strip()]
            
        start = 0
        while start < len(text):
            # Define where this chunk should end
            end = start + chunk_size
            
            # Extract the chunk
            chunk = text[start:end]
            chunks.append(chunk.strip())
            
            # Move our starting pointer forward, but step back by the overlap amount
            # This creates the "sliding window" effect
            start += (chunk_size - chunk_overlap)
            
        return chunks

    @staticmethod
    def parse_markdown(content: str) -> str:
        """
        Cleans up raw markdown text if needed. For now, we clean up
        excessive empty newlines to keep our chunks clean.
        """
        lines = [line.strip() for line in content.splitlines()]
        # Remove empty lines that add nothing to the AI's understanding
        cleaned_text = "\n".join([line for line in lines if line])
        return cleaned_text