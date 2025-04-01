from flask import Flask, render_template, request, redirect, send_from_directory, send_file
import requests
from io import BytesIO
from urllib.parse import unquote
import re
from qp_fetcher import get_question_papers, course_links,claret,vishwa,sheshadri, bangalore_university

app = Flask(__name__)

@app.route('/')
def index():
    # Combine all course dictionaries to get a unique list of courses
    all_courses = set()

    # Add courses from course_links (Main Course Links)
    all_courses.update(course_links.keys())

    # Add courses from claret
    all_courses.update(claret.keys())

    # Add courses from vishwa
    all_courses.update(vishwa.keys())

    # Add courses from sheshadri
    all_courses.update(sheshadri.keys())

    # Add courses from Bangalore University
    all_courses.update(bangalore_university.keys())

    # Convert to a sorted list for neatness
    courses = sorted(list(all_courses))

    return render_template('index.html', courses=courses)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


@app.route('/result')
def result():
    selected_course = request.args.get('course')
    selected_college = request.args.get('college')

    if not selected_course:
        return "No course selected.", 400

    if selected_course not in course_links and selected_course not in claret and selected_course not in vishwa and selected_course not in sheshadri:
        return f"Invalid course selected: {selected_course}"

    all_papers = get_question_papers(selected_course)

    if not all_papers:
        return "No question papers found for this course."

    semester_papers = []
    semester_set = set()

    for site_name, titles, links in all_papers:
        if selected_college and selected_college != "all" and site_name != selected_college:
            continue

        temp_papers = []
        for title, link in zip(titles, links):
            semester = "Unknown"
            match = re.search(r'(?i)\b(?:semester\s*(\d+)|(\d+)-sem)\b', title)
            if match:
                semester = match.group(1) or match.group(2)
            semester_set.add(semester)
            temp_papers.append((title, link, semester))

        semester_papers.append((site_name, temp_papers))

    return render_template(
        'result.html',
        course=selected_course,
        papers_data=semester_papers,
        semesters=sorted(semester_set),
        selected_college=selected_college
    )



@app.route('/open_pdf/<paper_title>/<paper_link>')
def open_pdf(paper_title, paper_link):
    # This will open the PDF in a new tab
    return redirect(paper_link)


@app.route('/download_pdf/<paper_title>/<path:paper_link>')
def download_pdf(paper_title, paper_link):
    """Handles downloading PDFs from Google Drive or direct links"""
    paper_link = unquote(paper_link)

    return redirect(paper_link)



if __name__ == '__main__':
    app.run(debug=True)
