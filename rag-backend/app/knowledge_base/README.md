# Knowledge Base Directory

This directory should contain your documents and data for the RAG system.

## File Structure
- Add your text documents, PDFs, or other knowledge sources here
- The RAG system will index and retrieve from these documents
- Supported formats: .txt, .md, .pdf (with appropriate parsing)

## Example Documents
- system_prompt.txt - Your complete system prompt
- projects.md - Information about your projects
- tools.md - Documentation for your tools and capabilities
- portfolio_data.json - Structured portfolio information

## Customization
Update the `load_knowledge_base()` method in `rag.py` to parse and load your specific document formats.
