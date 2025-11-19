import os
import time
from io import StringIO
from pathlib import Path

from docling.datamodel import vlm_model_specs
from docling.datamodel.accelerator_options import (AcceleratorDevice,
                                                   AcceleratorOptions)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (PdfPipelineOptions,
                                                VlmPipelineOptions)
from docling.datamodel.pipeline_options_vlm_model import (ApiVlmOptions,
                                                          ResponseFormat)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from dotenv import load_dotenv
from pdfminer.high_level import extract_text, extract_text_to_fp
from pypdf import PdfReader as PyPDFPdfReader
from PyPDF2 import PdfReader as PyPDF2PdfReader

load_dotenv()

ollama_url   = os.getenv("OLLAMA_BASE_URL")
ollama_model = os.getenv("OLLAMA_MODEL")
DRG_PDF_PATH = Path(__file__).parent.parent.parent / "data" / "raw_documents" / "DRG_2E_Rulebook.pdf"
output_dir   = Path(__file__).parent.parent.parent / "data" / "processed_documents"

class PDFParser:
  def __init__(self, pdf_path: str):
    # Convert relative paths to absolute paths
    if not Path(pdf_path).is_absolute():
      # If path is relative, resolve it relative to this script's directory
      self.pdf_path = str(Path(__file__).parent / pdf_path)
    else:
      self.pdf_path = pdf_path

  def pypdf2_parser(self):
    reader = PyPDF2PdfReader(self.pdf_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_pypdf2.txt"
    with open(output_path, "w", encoding="utf-8") as f:
      for page in reader.pages:
        f.write(page.extract_text())
    print(f"Extracted text saved to: {output_path}")

  def pypdf_parser(self):
    reader = PyPDFPdfReader(self.pdf_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_pypdf.txt"
    with open(output_path, "w", encoding="utf-8") as f:
      for page in reader.pages:
        f.write(page.extract_text())
    print(f"Extracted text saved to: {output_path}")

  def pdf_miner_parser(self):
    output_string = StringIO()

    with open(self.pdf_path, 'rb') as fin:
      text = extract_text(fin)

    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_pdfminer.txt"
    with open(output_path, "w", encoding="utf-8") as f:
      f.write(text)
    print(f"Extracted text saved to: {output_path}")

  def docling_parser(self):
    converter = DocumentConverter()
    result = converter.convert(self.pdf_path).document

    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_docling.md"
    with open(output_path, "w", encoding="utf-8") as f: 
      f.write(result.export_to_markdown())

    print(f"Extracted text saved to: {output_path}")





  def docling_vlm_parser(self):
    pipeline_options = VlmPipelineOptions()

    pipeline_options.accelerator_options = AcceleratorOptions(num_threads=8, device=AcceleratorDevice.CUDA)
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    
    converter = DocumentConverter(
      format_options={
        InputFormat.PDF: PdfFormatOption(
          pipeline_options=pipeline_options,
          pipeline_cls=VlmPipeline,
        )
      }
    )
    result = converter.convert(source=self.pdf_path).document

    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_docling_vlm.md"
    with open(output_path, "w", encoding="utf-8") as f:
      f.write(result.export_to_markdown())

    print(f"Extracted text saved to: {output_path}")





  def ollama_vlm_parser(self):
    # Configure the VLM pipeline. Enabling remote services allows HTTP calls to
    # locally hosted APIs (LM Studio, Ollama) or cloud services.
    pipeline_options = VlmPipelineOptions(enable_remote_services=True)

    pipeline_options.accelerator_options = AcceleratorOptions(num_threads=8, device=AcceleratorDevice.CUDA)
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    # Example using the Granite Vision model with Ollama:
    pipeline_options.vlm_options = ApiVlmOptions(
      url=f"{ollama_url}/v1/chat/completions",  # the default Ollama endpoint
      params=dict(
          model=ollama_model,
      ),
      prompt=f"OCR the full page to markdown.",
      timeout=90,
      scale=1.0,
      response_format=ResponseFormat.MARKDOWN,
    )  

    # Create the DocumentConverter and launch the conversion.
    doc_converter = DocumentConverter(
      format_options={
        InputFormat.PDF: PdfFormatOption(
          pipeline_options=self._ollama_vlm_pipeline(),
          pipeline_cls=VlmPipeline,
        )
      }
    )
    
    result = doc_converter.convert(source=self.pdf_path).document
    
    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_ollama_vlm.md"
    with open(output_path, "w", encoding="utf-8") as f:
      f.write(result.export_to_markdown())

    print(f"Extracted text saved to: {output_path}")







if __name__ == "__main__":
  pdf_parser = PDFParser(DRG_PDF_PATH)

  time_start = time.time()
  pdf_parser.pypdf2_parser()
  time_end = time.time()
  print(f"Time taken pypdf2_parser:      {time_end - time_start} seconds")
  
  time_start = time.time()
  pdf_parser.pypdf_parser()
  time_end = time.time()
  print(f"Time taken pypdf_parser:       {time_end - time_start} seconds")

  time_start = time.time()
  pdf_parser.pdf_miner_parser()
  time_end = time.time()
  print(f"Time taken pdf_miner_parser:   {time_end - time_start} seconds")
  
  # time_start = time.time()
  # pdf_parser.docling_parser()
  # time_end = time.time()
  # print(f"Time taken docling_parser:     {time_end - time_start} seconds")
  
  time_start = time.time()
  pdf_parser.docling_vlm_parser()
  time_end = time.time()
  print(f"Time taken docling_vlm_parser: {time_end - time_start} seconds")
  
  time_start = time.time()
  pdf_parser.ollama_vlm_parser()
  time_end = time.time()
  print(f"Time taken ollama_vlm_parser:  {time_end - time_start} seconds")