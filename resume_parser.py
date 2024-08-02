import json
import PyPDF2
import docx
import re
from collections import defaultdict
from email_validator import validate_email, EmailNotValidError
from phonenumbers import parse as parse_phone_number, PhoneNumberParseException
import logging

logging.basicConfig(level=logging.INFO)

def extract_text(file_path: str) -> str:
    """
    Extract text from a PDF or Word document.

    Args:
        file_path (str): Path to the file

    Returns:
        str: Extracted text

    Raises:
        ValueError: If the file format is unsupported
    """
    if file_path.endswith('.pdf'):
        pdf_file = open(file_path, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        text = ''
        for page in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page).extractText()
        pdf_file.close()
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text
    else:
        raise ValueError("Unsupported file format. Please use PDF or Word format.")
    return text

def parse_sections(text: str) -> list:
    """
    Split the text into sections.

    Args:
        text (str): Extracted text

    Returns:
        list: List of sections

    Raises:
        ValueError: If the text does not contain at least 5 sections
    """
    sections = text.split('\n\n')
    if len(sections) < 5:
        raise ValueError("Invalid file format. Expected at least 5 sections.")
    return sections

def parse_contact_info(section: str) -> dict:
    """
    Parse contact information from a section.

    Args:
        section (str): Section containing contact information

    Returns:
        dict: Contact information

    Raises:
        ValueError: If the email or phone number format is invalid
    """
    contact_info = section.split('\n')
    name = contact_info[0]
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', contact_info[2])
    if email_match:
        email = email_match.group()
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValueError("Invalid email format")
    else:
        raise ValueError("Invalid email format")
    phone_match = re.search(r'\(\d{3}\) \d{3}-\d{4}', contact_info[2])
    if phone_match:
        phone = phone_match.group()
        try:
            parse_phone_number(phone)
        except PhoneNumberParseException:
            raise ValueError("Invalid phone number format")
    else:
        raise ValueError("Invalid phone number format")
    address = contact_info[1]
    return {"name": name, "email": email, "phone": phone, "address": address}

def parse_education(section: str) -> list:
    """
    Parse education information from a section.

    Args:
        section (str): Section containing education information

    Returns:
        list: List of education information
    """
    education = []
    for edu in section.split('\n'):
        if edu:
            degree, institution, graduation_date = edu.split(', ')
            education.append({
                "degree": degree,
                "institution": institution,
                "graduationDate": graduation_date.strip('()')
            })
    return education

def parse_work_experience(section: str) -> list:
    """
    Parse work experience information from a section.

    Args:
        section (str): Section containing work experience information

    Returns:
        list: List of work experience information
    """
    work_experience = []
    for exp in section.split('\n'):
        if exp:
            # Add validation checks here
            work_experience.append({"experience": exp})
    return work_experience

def main(file_path: str) -> dict:
    """
    Main function to extract and parse data from a file.

    Args:
        file_path (str): Path to the file

    Returns:
        dict: Extracted and parsed data
    """
    try:
        text = extract_text(file_path)
        sections = parse_sections(text)
        contact_info = parse_contact_info(sections[0])
        education = parse_education(sections[1])
        work_experience = parse_work_experience(sections[2])
        return {"contactInfo": contact_info, "education": education, "workExperience": work_experience}
    except Exception as e:
        logging.error(f"Error parsing file: {e}")
        return {}

if __name__ == "__main__":
    file_path = "example.docx"  # Replace with your file path
    data = main(file_path)
    print(json.dumps(data, indent=4))
