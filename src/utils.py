import base64
import re
from PIL import Image
from typing import Optional, Tuple, Union
import xml.etree.ElementTree as ET

def get_image_dimensions(file_path):
    with Image.open(file_path) as img:
        width, height = img.size
        return width, height

def concatenate_paper_text(paper_data: dict) -> str:
    """
    concatenate the text of the paper, including title, abstract and sections
    @param paper_data: dict
    @return: str
    """
    paper_text = ""
    if paper_data.get("title", ""):
        paper_text += f"Title: {paper_data['title']}\n"
    if paper_data.get("abstract", ""):
        paper_text += f"Abstract: {paper_data['abstract']}\n"
    if paper_data.get("sections", []):
        for section in paper_data["sections"]:
            if section.get("heading", ""):
                paper_text += f"{section['heading']}\n"
            if section.get("text", ""):
                paper_text += f"{section['text']}\n"

    return paper_text

def encode_image(image_path: str) -> str:
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')