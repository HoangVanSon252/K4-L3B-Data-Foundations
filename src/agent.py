from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # 1. Retrieve top-k relevant chunks
        chunks = self.store.search(question, top_k)

        # 2. Build a prompt with the chunks as context
        prompt = self._build_prompt(question, chunks)

        # 3. Call the LLM to generate an answer
        answer = self.llm_fn(prompt)
        return answer

    def _build_prompt(self, question: str, chunks: list[dict]) -> str:
        """
        Build a prompt for the LLM.
        
        Args:
            question: The user's question
            chunks: List of retrieved chunks from the knowledge base
        
        Returns:
            A formatted prompt string
        """
        context_blocks = []
        for i, chunk in enumerate(chunks, 1):
            context = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            
            # Add metadata to context if available
            meta_info = ""
            if metadata:
                meta_info_lines = []
                for key, value in metadata.items():
                    # Skip embedding and id if present
                    if key in ["embedding", "id", "_id"]:
                        continue
                    meta_info_lines.append(f"- {key}: {value}")
                if meta_info_lines:
                    meta_info = "\n".join(meta_info_lines)
            
            # Format the context block
            block = f"""Document {i}:
{context}
{meta_info}"""
            context_blocks.append(block)
        
        context_section = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."
        
        # Use a clear and structured prompt template
        prompt_template = f"""# Instruction
You are an expert assistant that answers questions based on the provided context.

# Context
{context_section}

# Question
{question}

# Instruction
- Use ONLY the information provided in the context to answer the question.
- If the answer is not in the context, respond with: "I cannot answer this question based on the available information."
- Do not use any external knowledge.
- If multiple documents provide conflicting information, mention the conflict.
- Be concise and accurate.

# Answer
"""
        return prompt_template
