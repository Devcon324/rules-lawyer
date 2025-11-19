import os
import time
from io import StringIO
from pathlib import Path
from typing import Callable

from docling.datamodel import vlm_model_specs
from docling.datamodel.accelerator_options import (AcceleratorDevice,
                                                   AcceleratorOptions)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (PdfPipelineOptions,
                                                RapidOcrOptions,
                                                TableFormerMode,
                                                TesseractOcrOptions,
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
    """PyPDF2 Parser, produces txt, worst outcome"""
    reader = PyPDF2PdfReader(self.pdf_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_pypdf2.txt"
    with open(output_path, "w", encoding="utf-8") as f:
      for page in reader.pages:
        f.write(page.extract_text())
    print(f"Extracted text saved to: {output_path}")

  def pypdf_parser(self):
    """PyPDF Parser, produces txt, better than pypdf2."""
    reader = PyPDFPdfReader(self.pdf_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_pypdf.txt"
    with open(output_path, "w", encoding="utf-8") as f:
      for page in reader.pages:
        f.write(page.extract_text())
    print(f"Extracted text saved to: {output_path}")

  def pdf_miner_parser(self):
    """PDFMiner Parser, produces txt, better than pypdf"""
    with open(self.pdf_path, 'rb') as fin:
      text = extract_text(fin)
    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_pdfminer.txt"
    with open(output_path, "w", encoding="utf-8") as f:
      f.write(text)
    print(f"Extracted text saved to: {output_path}")

  def docling_parser(self):
    """Default Docling Parser, sucks, don't use it."""
    pipeline_options = PdfPipelineOptions(
      generate_table_images=True,
      enable_parallel_processing=True,
      do_ocr=True,
      ocr_options = RapidOcrOptions(lang=["english"]),
      do_table_structure=True,
      generate_picture_images=True,
      generate_page_images=False,
      do_formula_enrichment=True,
      table_structure_options={"do_cell_matching": True, "mode": TableFormerMode.ACCURATE},
      accelerator_options=AcceleratorOptions(num_threads=4, device=AcceleratorDevice.CUDA),
    )

    format_options = {InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    converter      = DocumentConverter(format_options=format_options)
    result         = converter.convert(source=self.pdf_path)

    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_docling.md"
    with open(output_path, "w", encoding="utf-8") as f: 
      f.write(result.export_to_markdown())

    print(f"Extracted text saved to: {output_path}")

  def docling_ocr_parser(self):
    """
    Docling Parser with OCR, uses EasyOCR.
    uses models provided by docling.
    produces markdown, with images embedded.
    Best outcome.
    """
    pipeline_options = PdfPipelineOptions(
      generate_table_images=True,
      enable_parallel_processing=True,
      do_ocr=True,
      ocr_options = RapidOcrOptions(lang=["english"]),
      do_table_structure=True,
      generate_picture_images=True,
      generate_page_images=True,
      do_formula_enrichment=True,
      images_scale=2,
      table_structure_options={"do_cell_matching": True, "mode": TableFormerMode.ACCURATE},
      accelerator_options=AcceleratorOptions(num_threads=4, device=AcceleratorDevice.CUDA),
    )

    format_options = {InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    converter      = DocumentConverter(format_options=format_options)
    result         = converter.convert(source=self.pdf_path)
    markdown_text  = result.document.export_to_markdown(image_mode="embedded")

    output_path = output_dir / f"{os.path.basename(self.pdf_path).replace('.pdf', '')}_docling_ocr_base.md"
    with open(output_path, "w", encoding="utf-8") as f:
      f.write(markdown_text)

    print(f"Extracted text saved to: {output_path}")




if __name__ == "__main__":
  """Run all parsers and measure time taken."""
  pdf_parser = PDFParser(DRG_PDF_PATH)

  func_dict: dict[str, Callable] = {
    "pypdf2_parser": pdf_parser.pypdf2_parser,
    "pypdf_parser": pdf_parser.pypdf_parser,
    "pdf_miner_parser": pdf_parser.pdf_miner_parser,
    "docling_parser": pdf_parser.docling_parser,
    "docling_ocr_parser": pdf_parser.docling_ocr_parser,
  }

  for func_name, func in func_dict.items():
    try:
      time_start = time.time()
      func()
      time_end = time.time()
      print(f"Time taken {func_name}: {time_end - time_start} seconds")
    except Exception as e:
      print(f"Error in {func_name}: {e}")
