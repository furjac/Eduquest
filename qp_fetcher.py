import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

MAIN_PAGE = "https://www.bubangalore.com"

course_links = {
    "open_courses": "https://ehelper.live/UG/open course/OC.html",
    "BCA": "https://ehelper.live/UG/BCA/computer application.html",
    "BBA": "https://ehelper.live/ug/bba/bba",
    "bttm": "https://ehelper.live/UG/B T T M/travelandtourism.html",
    "bsc_psychology": "https://ehelper.live/UG/Bsc psychology/psy.html",
    "BCOM": "https://ehelper.live/ug/bcom/commerce",
    "ba_english": "https://ehelper.live/UG/BA english/english.html",
    "bsc_chemistry": "https://ehelper.live/UG/Bsc chemistry/chemistry.html",
    "bsc_botany": "https://ehelper.live/UG/Bsc botany/botany.html",
    "bsc_mathematics": "https://ehelper.live/UG/Bsc Mathematics/maths.html",
    "bsc_physics": "https://ehelper.live/UG/Bsc physics/physics.html",
    "ba_economics": "https://ehelper.live/UG/BA economics/economics.html",
    "bsc_zoology": "https://ehelper.live/UG/Bsc zoology/zoology.html",
    "ba_hindi": "https://ehelper.live/UG/BA hindi/hindi.html",
    "ba_history": "https://ehelper.live/UG/BA history/history.html",
    "ba_malayalam": "https://ehelper.live/UG/BA malayalam/malayalam.html",
    "MCA": "https://ehelper.live/pg/mca/mca",
    "mttm": "https://ehelper.live/pg/mttm/mttm",
    "MCOM": "https://ehelper.live/pg/mcom/mcom",
    "ma_history": "https://ehelper.live/PG/MA HISTORY/history.html",
    "msc_biostatistics": "https://ehelper.live/pg/biostatistics/biostatistics",
    "msc_biotechnology": "https://ehelper.live/pg/biotechnology/biotechnology",
    "ma_english": "https://ehelper.live/PG/MA english/english.html",
    "msc_statistics": "https://ehelper.live/PG/MSC statistics/statistics.html",
    "msc_chemistry": "https://ehelper.live/PG/Msc Chemistry/msc chemistry.html",
    "msc_botany": "https://ehelper.live/PG/Msc Botany/mscbotany.html",
    "msc_mathematics": "https://ehelper.live/PG/Msc Mathematics/maths.html",
    "msc_physics": "https://ehelper.live/PG/MSC physics/physics.html",
    "msc_zoology": "https://ehelper.live/PG/MSC zoology/msczoology.html",
    "ma_economics": "https://ehelper.live/PG/MA economics/economics.html",
    "ma_hindi": "https://ehelper.live/PG/MA hindi/HINDI.html",
    "ma_malayalam": "https://ehelper.live/PG/MA malayalam/MALAYALAM.html",
    "msc_microbiology": "https://ehelper.live/pg/microbiology/microbiology"
}

claret = {
    "BSC": 'bsc',
    "BBA": 'bba',
    "BA": 'ba',
    "BCOM": 'bcom',
    "BCA": 'bca'
}

vishwa = {
    "BBA": 'bba',
    "MCOM": 'mcom',
    "BCOM": 'bcom',
    "BCA": 'bca'
}

sheshadri = {
    "BCOM": 'bcom',
    "BBA": 'bba',
    "BCA": 'bca',
    "BCOM-HNS": "bcom-hns"
}

bangalore_university = {
    "BA": "BA",
    "BBA": "BBA",
    "BBM": "BBM",
    "BCA": "BCA",
    "BCOM": "BCOM",
    "BED": "B-ED",
    "BHM": "BHM",
    "BSC": "BSC",
    "BSW": "BSW",
    "LLB": "LLB",
    "LLM": "LLM",
    "MA": "MA",
    "MBA": "MBA",
    "MCA": "MCA",
    "MCOM": "MCOM",
    "MFA": "MFA",
    "MIB": "MIB",
    "MSC": "MSC",
    "PHD": "PHD",
    "MIX": "MIX"
}


def MG_University(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the webpage.")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")

    question_paper_titles = []
    question_paper_links = []

    # Extract semester numbers from comments
    semester_mapping = {"main": "Semester 1"}  # First semester is always "main"
    comments = soup.find_all(string=lambda text: isinstance(text, str) and "SEMESTER" in text.upper())

    for idx, comment in enumerate(comments):
        match = re.search(r"SEMESTER\s*(\d+)", comment, re.IGNORECASE)
        if match:
            sem_number = match.group(1)
            div_id = f"main-{idx}" if idx > 0 else "main"  # Ensures first sem remains "main"
            semester_mapping[div_id] = f"Semester {sem_number}"

    # Extract question papers under each semester
    for div_id, semester in semester_mapping.items():
        div = soup.find("div", id=div_id)
        if not div:
            continue
        
        tables = div.find_all("table", class_="table")
        for table in tables:
            for link in table.find_all("a", href=True):
                title = link.text.strip()
                href = link["href"]
                if title and href:
                    question_paper_titles.append(f"{semester}: {title}")
                    question_paper_links.append(href)

    return question_paper_titles, question_paper_links

def vishwacollege_pdfs(course_slug):
    BASE_URL = "https://vishwachethanadegreecollege.com/"
    if course_slug == "bcom":
        url = f"{BASE_URL}question.html"
    else:
        url = f"{BASE_URL}{course_slug}-question.html"

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the webpage.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    pdf_titles = []
    pdf_links = []

    # Find all semester content sections
    content_sections = soup.select(".tab_content .tabs_item")

    if not content_sections:
        print("No semester sections found. The page structure may have changed.")
        return

    for semester_num, section in enumerate(content_sections, start=1):  # Semester starts from 1
        pdf_blocks = section.select(".row.align-items-center")

        for block in pdf_blocks:
            title_tag = block.select_one(".course-pdf p")
            title = title_tag.text.strip() if title_tag else "No Title"
            title = f"Semester {semester_num}: {title}"  # Append semester number to title

            pdf_link_tag = block.select_one(".download-pdf a")
            pdf_link = pdf_link_tag["href"] if pdf_link_tag else "No PDF Found"

            # Convert relative links to absolute links
            pdf_link = (
                urljoin(BASE_URL, pdf_link)
                if pdf_link != "No PDF Found"
                else pdf_link
            )

            pdf_titles.append(title)
            pdf_links.append(pdf_link)

    return pdf_titles, pdf_links


def claret_pdf(course_slug):
    if course_slug == 'bcom':
        url = "https://www.claretcollege.edu.in/previous-bu-question-papers"
    else:
        url = f"https://www.claretcollege.edu.in/previous-bu-question-papers-{course_slug}"

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")
    all_titles = []
    all_links = []

    for sem in range(1, 7):
        tab_id = f"nav-sem{sem}"
        sem_section = soup.find(id=tab_id)
        if not sem_section:
            continue

        pdf_links = sem_section.find_all("a", href=True)

        for link in pdf_links:
            title = link.get_text(strip=True)
            href = link["href"]
            full_url = urljoin(url, href)  # Ensure full URL

            if title and href.endswith(".pdf"):
                clean_title = re.sub(r'^\d+\s*', '', title).strip()
                all_titles.append(f"semester {sem}: {clean_title}")
                all_links.append(full_url)

        time.sleep(0.3)  # Small delay to avoid overwhelming the server

    return all_titles, all_links


def sheshadripuram_pdfs(course_slug):
    base_url = "https://www.spmcollege.ac.in/"
    if course_slug == "bcom":
        url = urljoin(base_url, "question-papers")
    else:
        url = urljoin(base_url, f"question-papers-{course_slug}")

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the page.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []
    pdf_texts = []

    # Find all semester tabs
    tabs = soup.select(".tabs-nav ul li a")
    for num, tab in enumerate(tabs, start=1):  # Using enumerate for index
        tab_id = tab.get("href").replace("#", "")  # Extract tab ID
        tab_content = soup.find("div", id=tab_id)
        if not tab_content:
            continue

        pdf_elements = tab_content.select(".tabbed-content_container a")

        for pdf in pdf_elements:
            link = pdf.get("href")
            text = pdf.get_text(strip=True)
            if link and link.endswith(".pdf"):
                pdf_links.append(urljoin(base_url, link))
                pdf_texts.append(f"semester {num}: {text}")

    return pdf_texts, pdf_links


def get_course_url(course_name):
    """Find the correct URL for a course from the main page."""

    try:
        response = requests.get(MAIN_PAGE, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Find course links dynamically
    for a in soup.select("div.card a"):
        if course_name.lower() in a.text.strip().lower():
            return urljoin(MAIN_PAGE, a["href"])

    print(f"Course '{course_name}' not found.")
    return None


def bu_pdf(course_name):
    """Scrape PDFs from the specific course page."""
    course_url = get_course_url(course_name)
    if not course_url:
        return [], []

    try:
        response = requests.get(course_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching course page: {e}")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")

    all_texts, all_links = [], []

    # Step 1: Extract PDFs and find `.html` links
    for box in soup.select(".box, .card"):
        for a_tag in box.find_all("a", href=True):
            link = urljoin(course_url, a_tag["href"])
            text = a_tag.text.strip()

            if text and link.endswith(".pdf"):
                all_texts.append(text)
                all_links.append(link)

    return all_texts, all_links


def sanitize_filename(name):
    return "_".join(name.split()).replace("/", "_").replace("\\", "_")


def download_pdf(title, url):
    sanitized_title = sanitize_filename(title)
    folder_path = os.path.join("downloads", sanitized_title)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{sanitized_title}.pdf")
    count = 1
    while os.path.exists(file_path):
        file_path = os.path.join(folder_path, f"{sanitized_title}_{count}.pdf")
        count += 1

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download: {title}")


def get_question_papers(course_slug):
    """
    Fetch question papers from different websites based on the course provided.

    Arguments:
    - course_slug: The course slug (e.g., "bcom", "bca").

    Returns:
    - A list of tuples (site_name, titles, links) for question papers from all sites.
    """
    all_papers = []

    # Define the course URLs for each site (you already have these dictionaries set up)
    site_courses = {
        "MG University": course_links,
        "Vishwachethana College": vishwa,
        "Claret College": claret,
        "Sheshadripuram College": sheshadri,
        "bangalore university": bangalore_university
    }
    
    # Check each site for the selected course
    for site_name, course_dict in site_courses.items():
        # Check if the course exists in the current site's course dictionary
        if course_slug not in course_dict:
            print(f"Course '{course_slug}' not available on {site_name}. Skipping...")
            continue  # Skip this site if course is not available

        # Fetch papers from the current site
        if site_name == "MG University":
            titles, links = MG_University(course_dict[course_slug])
        elif site_name == "Vishwachethana College":
            titles, links = vishwacollege_pdfs(course_dict[course_slug])
        elif site_name == "Claret College":
            titles, links = claret_pdf(course_dict[course_slug])
        elif site_name == "Sheshadripuram College":
            titles, links = sheshadripuram_pdfs(course_dict[course_slug])
        elif site_name == "bangalore university":
            titles, links = bu_pdf(course_dict[course_slug])

        # Only add the site if it has papers available
        if titles and links:
            all_papers.append((site_name, titles, links))

    # Return the list of available papers across sites, or empty if none found
    return all_papers if all_papers else None




def fetch_and_download_papers(course_slug):
    """
    Fetch question papers for a selected course.
    
    Arguments:
    - course_slug: The course slug (e.g., "bcom", "bca").

    Returns:
    - A list of tuples (site_name, titles, links) for question papers from all sites.
    """
    # Dictionary of courses across different sites
    courses = {
        "claret": claret,
        "vishwa": vishwa,
        "sheshadripuram": sheshadri,
        "mg": course_links  # MG University courses are listed in course_links
    }

    if course_slug not in courses["mg"]:
        return "Invalid course selected."
    
    # Fetch papers for the selected course from all sites
    all_papers = get_question_papers(course_slug)

    if not all_papers:
        return "No papers found for this course."

    return all_papers  # This will be rendered in the result page
