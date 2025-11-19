import os
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.converters import MarkdownToDocument
from haystack.components.joiners import DocumentJoiner
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.components.embedders.ollama import (
    OllamaDocumentEmbedder, OllamaTextEmbedder)
from haystack_integrations.components.generators.ollama import OllamaGenerator
from neo4j_haystack import Neo4jDocumentStore, Neo4jEmbeddingRetriever

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

class RAGService:
  def __init__(self):
    self.document_store = Neo4jDocumentStore(
      url=os.getenv("NEO4J_URI"),
      database=os.getenv("NEO4J_DATABASE"),
      username=os.getenv("NEO4J_USERNAME"),
      password=os.getenv("NEO4J_PASSWORD"),
      index=os.getenv("NEO4J_INDEX"), # The name of the Vector Index in Neo4j
      node_label=os.getenv("NEO4J_NODE_LABEL"), # Providing a label to Neo4j nodes which store Documents
      embedding_field="embedding",
      embedding_dim=768,
      recreate_index=True,
      progress_bar=True
    )
    self.embedding_pipeline = Pipeline()
    self.query_pipeline = Pipeline()

  def build_embeddings(self, path_to_markdown: str) -> bool:
    try:
      document_converter = MarkdownToDocument(
        table_to_single_line=False,
        progress_bar=True,
        store_full_path=False)
      document_joiner = DocumentJoiner()
      document_cleaner = DocumentCleaner(
        remove_empty_lines=True,
        remove_extra_whitespaces=True,
        remove_repeated_substrings=False,
        keep_id=False,
        remove_substrings=None,
        remove_regex=None,
        unicode_normalization=None,
        ascii_only=False)
      document_splitter = DocumentSplitter(
        split_by="word",
        split_length=200,
        split_overlap=0,
        split_threshold=0,
        splitting_function=None,
        respect_sentence_boundary=True,
        language="en",
        use_split_rules=False,
        extend_abbreviations=True,
        skip_empty_documents=True)
      document_embedder = OllamaDocumentEmbedder(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL"),
        url=os.getenv("OLLAMA_BASE_URL"))
      document_writer = DocumentWriter(
        document_store=self.document_store,
        policy=DuplicatePolicy.OVERWRITE)

      self.embedding_pipeline = Pipeline()
      # Add components to the pipeline
      self.embedding_pipeline.add_component(instance=document_converter, name="document_converter")
      self.embedding_pipeline.add_component(instance=document_joiner, name="document_joiner")
      self.embedding_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
      self.embedding_pipeline.add_component(instance=document_splitter, name="document_splitter")
      self.embedding_pipeline.add_component(instance=document_embedder, name="document_embedder")
      self.embedding_pipeline.add_component(instance=document_writer, name="document_writer")
      # Connect components
      self.embedding_pipeline.connect("document_converter", "document_joiner")
      self.embedding_pipeline.connect("document_joiner", "document_cleaner")
      self.embedding_pipeline.connect("document_cleaner", "document_splitter")
      self.embedding_pipeline.connect("document_splitter", "document_embedder")
      self.embedding_pipeline.connect("document_embedder", "document_writer")

      self.embedding_pipeline.run(({
        "document_converter": {"sources": [path_to_markdown]}
        }
      ))
      return True
    except Exception as e:
      print(f"Error in markdown_to_vector_embeeding: {e}")
      return None

  def build_query_pipeline(self):
    try:
      template = dedent("""
        Answer the questions based on the given context.

        Context:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}

        Question: {{ question }}
        Answer:
      """)

      embedder = OllamaTextEmbedder(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL"),
        url=os.getenv("OLLAMA_BASE_URL"))
      retriever = Neo4jEmbeddingRetriever(
        document_store=self.document_store)
      augmenter = PromptBuilder(
        template=template,
        required_variables=["documents", "question"])
      generator = OllamaGenerator(
        model=os.getenv("OLLAMA_GENERATIVE_MODEL"),
        url=os.getenv("OLLAMA_BASE_URL"))

      self.query_pipeline = Pipeline()
      # Add components to the pipeline
      self.query_pipeline.add_component(instance=embedder, name="embedder")
      self.query_pipeline.add_component(instance=retriever, name="retriever")
      self.query_pipeline.add_component(instance=augmenter, name="augmenter")
      self.query_pipeline.add_component(instance=generator, name="generator")
      # Connect components
      self.query_pipeline.connect("embedder.embedding", "retriever.query_embedding")
      self.query_pipeline.connect("retriever", "augmenter.documents")
      self.query_pipeline.connect("augmenter.prompt", "generator.prompt")

      self.query_pipeline.warm_up()

      return True
    except Exception as e:
      print(f"Error in query_pipeline_setup: {e}")
      return None


  def query(self, question: str) -> str:
    try:
      response = self.query_pipeline.run(
        data={
          "embedder": {"text": question},
          "augmenter": {"question": question}
        }
      )
      return response["generator"]["replies"][0]
    except Exception as e:
      print(f"Error in query: {e}")
      return None

if __name__ == "__main__":
  rag_service = RAGService()

  rag_service.build_embeddings(path_to_markdown="backend/data/processed_documents/DRG_2E_Rulebook_docling.md")
  rag_service.build_query_pipeline()

  result = rag_service.query(question="What are some special features of the driller?")

  print(result)