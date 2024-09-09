import os
import re
import pytz
import json
import shutil
import shelve
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from collections import defaultdict
from logger import get_logger
logger = get_logger(__name__)

class Parser:
    def __init__(self):
        pass

    def parse_sec_filing(self, html_content):
        """
        Parse SEC filing HTML content and extract relevant sections.
        Args:
            html_content (str): The HTML content of the SEC filing.
        Returns:
            dict: A dictionary containing parsed sections of the SEC filing.
                  Keys are section names, and values are the corresponding content.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        sections = defaultdict(list)
        current_section = None

        for element in soup.find_all(['span', 'div']):
            style = element.get('style', '')
            if 'font-weight:700' in style or 'font-weight: 700' in style:
                text = element.get_text(strip=True)
                if text.lower().startswith("item "):
                    current_section = text
                    sections[current_section] = []
            elif current_section:
                text = element.get_text(strip=True)
                if text:
                    sections[current_section].append(text)

        # Clean up section names
        cleaned_sections = {}
        for section, content in sections.items():
            if len(content) == 0:
                continue
            content = [c for c in content if len(c.split(" ")) > 15]
            content = '\n'.join(content)
            words_in_content = len(content.split(" "))
            if words_in_content < 20:
                continue
        
            section = str(section).split(".")[1]
            section = section.strip(" ")
            section = ' '.join(section.split())
            
            # first four words are section_key
            section_key = '_'.join(section.split()[:4])
            section_key = section_key.replace(",", "")
            section_key = section_key.replace("’", "")
            section_key = str(section_key).lower()

            # make these more readable for an LLM
            if section_key == "business":
                section_key = "business_info"
            
            cleaned_sections[section_key] = content

        return cleaned_sections
