from flask import Flask,  render_template, request
import psycopg2
import sqlite3
app = Flask(__name__, static_url_path='/static')

@app.route('/')
def main_page():
    return render_template('Mainpage.html')

# SQLite database connection
# Database connection
conn = psycopg2.connect(
    database="AUB_Database_final",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5434"
)

cursor = conn.cursor()

# Endpoint for /students
@app.route('/students')
def students_page():
    # Getting student id from request, assuming it's passed as a query parameter
    student_id = request.args.get('student-id')
    #print(student_id)

    timeSlots = [
        "09:00", "10:00", "11:00",
        "12:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00"
    ]

    # Fetching student information
    cursor.execute("""
        SELECT 
            s.fname AS First_Name,
            s.lname AS Last_Name,
            m.name AS Major_Name,
            s.email AS Email,
            s.gpa AS GPA,
            s.dob AS Date_of_Birth,
            s.start_date AS Start_Date,
            s.end_date AS End_Date,
            s.phone_number AS Phone_Number,
            d.name AS Department_Name
        FROM 
            student AS s
        JOIN 
            major AS m ON s.major_id = m.id
        JOIN 
            department AS d ON m.dep_id = d.id
        WHERE 
            s.id = %s;
    """, (student_id,))
    information_data = cursor.fetchone()
    #print(information_data)

    if information_data is not None:
        information_data_dict = {
        "First_Name": information_data[0],
        "Last_Name": information_data[1],
        "Major_Name": information_data[2],
        "Email": information_data[3],
        "GPA": information_data[4],
        "Date_of_Birth": information_data[5],
        "Start_Date": information_data[6],
        "End_Date": information_data[7],
        "Phone_Number": information_data[8],
        "Department_Name": information_data[9]
    }
    else:
    # Handle the case where no data is found for the student ID
    # For example, you can set information_data_dict to an empty dictionary or display an error message
        information_data_dict = {}

    # Fetching student clubs
    cursor.execute("""
        SELECT 
            c.name AS Name,
            r.number AS MeetingLocation
        FROM 
            student_club_enrollment AS sce
        JOIN 
            club AS c ON sce.club_id = c.id
        JOIN 
            room AS r ON c.room_id = r.number AND c.building = r.building
        WHERE 
            sce.student_id = %s;
    """, (student_id,))
    clubs_data_list = [{"Name": club[0], "MeetingLocation": club[1]} for club in cursor.fetchall()]
    #print(clubs_data_list)

    # Fetching student schedule
    cursor.execute("""
        SELECT 
            c.name AS sectionName,
            t.day_schedule AS Day,
            t.start_time AS startTime,
            t.end_time AS endTime
        FROM 
            student_section_enrollment AS sse
        JOIN 
            section AS s ON sse.section_crn = s.crn
        JOIN 
            time AS t ON s.crn = t.section_crn
        JOIN 
            course AS c ON s.course_id = c.id
        WHERE 
            sse.student_id = %s;
    """, (student_id,))
    schedule_data_list = [{"sectionName": entry[0], "Day": entry[1], "startTime": entry[2], "endTime": entry[3]} for entry in cursor.fetchall()]
    print(schedule_data_list)
    # Fetching student transcript data
    cursor.execute("""
        SELECT 
            c.name AS CourseName,
            s.semester_given AS Semester,
            s.year_given AS Year,
            sse.grade AS Grade
        FROM 
            student_section_enrollment AS sse
        JOIN 
            section AS s ON sse.section_crn = s.crn
        JOIN 
            course AS c ON s.course_id = c.id
        WHERE 
            sse.student_id = %s;
    """, (student_id,))
    transcript_data_list = [{"CourseName": entry[0], "Semester": entry[1], "Year": entry[2], "Grade": entry[3]} for entry in cursor.fetchall()]
    #print(transcript_data_list)

    # Data to be passed to the template
    return render_template('students.html', timeSlots=timeSlots,information_data=information_data_dict, clubs=clubs_data_list, scheduleData=schedule_data_list, transcriptData=transcript_data_list)

# Route for the professors page
@app.route('/professors')
def professors_page():
    professor_id = request.args.get('professor-id')
    print("Professor ID received:", professor_id)
    # Fetch professor information
    cursor.execute('''
        SELECT fname, minit, lname, research_area, email, title, salary, dob, hiring_date, phone_number, highest_education
        FROM professor
        WHERE id = %s
    ''', (professor_id,))
    professor_info = cursor.fetchone()
    
    print(professor_info)

    if professor_info is not None:

        professor = {
            "Fname": professor_info[0] + " " + (professor_info[1] + "." if professor_info[1] else ""),
            "Lname": professor_info[2],
            "ResearchArea": professor_info[3],
            "Email": professor_info[4],
            "Title": professor_info[5],
            "Salary": professor_info[6],
            "DOB": professor_info[7],
            "HiringDate": professor_info[8],
            "PhoneNumber": professor_info[9],
            "HighestEducation": professor_info[10]
            }
    else:
        professor={}

    # Fetch office location
    cursor.execute('''
        SELECT r.building AS Building_Name, r.number AS Room_Number
        FROM professor AS p
        JOIN room AS r ON p.room_id = r.number
        WHERE p.id = %s
    ''', (professor_id,))
    office = cursor.fetchone()
    #print(office)

    # Fetch courses taught
    cursor.execute('''
        SELECT c.name AS Course_Name, s.crn AS Section_CRN, s.semester_given AS Semester, s.year_given AS Year
        FROM section AS s
        JOIN course AS c ON s.course_id = c.id
        WHERE s.professor_id = %s
    ''', (professor_id,))
    courses = [
        {"Name": row[0], "CRN": row[1], "Semester": row[2], "Year": row[3]}
        for row in cursor.fetchall()
    ]
    print(courses)

    return render_template('professors.html', professor=professor, office=office, courses=courses)

# Route for the courses page
@app.route('/courses')
def courses_page():
    course_id = request.args.get('course-id')
    #print(course_id)
    # Fetch basic information about the course
    cursor.execute('''
        SELECT name, credit_hours, description
        FROM course
        WHERE id = %s
    ''', (course_id,))
    course_info = cursor.fetchone()
    #print(course_info)
    if course_info is not None:
        course_details = {
            "Course_Name": course_info[0],
            "Credit_Hours": course_info[1],
            "Course_Description": course_info[2]
        }
    else:
        course_details= {}
    #print(course_details)

    # Fetch corequisite courses
    cursor.execute('''
        SELECT cr.name
        FROM corequisite AS co
        JOIN course AS c ON co.course_id = c.id
        JOIN course AS cr ON co.corequisite_id = cr.id
        WHERE c.id = %s
    ''', (course_id,))
    corequisites = [row[0] for row in cursor.fetchall()]
    #print(corequisites)

    # Fetch prerequisite courses
    cursor.execute('''
        SELECT p.name
        FROM prerequisite AS pr
        JOIN course AS c ON pr.course_id = c.id
        JOIN course AS p ON pr.prerequisite_id = p.id
        WHERE c.id = %s
    ''', (course_id,))
    prerequisites = [row[0] for row in cursor.fetchall()]
    #print(prerequisites)

    # Fetch accounts for information
    cursor.execute('''
        SELECT caf.accounts_for
        FROM course_accounts_for AS caf
        JOIN course AS c ON caf.course_id = c.id
        WHERE c.id = %s
    ''', (course_id,))
    accounts_for = [row[0] for row in cursor.fetchall()]
    #print(accounts_for)

    # Fetch restrictions
    cursor.execute('''
        SELECT cr.restriction
        FROM course_restrictions AS cr
        JOIN course AS c ON cr.course_id = c.id
        WHERE c.id = %s
    ''', (course_id,))
    restrictions = [row[0] for row in cursor.fetchall()]
    #print(restrictions)

    # Fetch all sections for the course
    cursor.execute('''
        SELECT s.crn, s.semester_given, s.year_given
        FROM section AS s
        JOIN course AS c ON s.course_id = c.id
        WHERE c.id = %s
    ''', (course_id,))
    sections = [{"Section_CRN": row[0], "Semester": row[1], "Year": row[2]} for row in cursor.fetchall()]
    #print(sections)

    # Render the course page with all collected information
    return render_template('courses.html', course=course_details, corequisites=corequisites, prerequisites=prerequisites, accounts_for=accounts_for, restrictions=restrictions, sections=sections)

# Fetch a Club's information    
@app.route('/clubs')
def clubs_page():
    club_id = request.args.get('club-id')
    #print(club_id)
    
    # Fetch basic information about the club
    cursor.execute('''
        SELECT 
            c.name, 
            CONCAT(s.fname, ' ', s.lname) AS President_Name,
            CONCAT(p.fname, ' ', p.lname) AS Advisor_Name,
            r.building, 
            r.number
        FROM 
            club AS c
        JOIN 
            student AS s ON c.president_id = s.id
        JOIN 
            professor AS p ON c.professor_id = p.id
        JOIN 
            room AS r ON c.room_id = r.number AND c.building = r.building
        WHERE 
            c.id = %s;
    ''', (club_id,))
    club_info = cursor.fetchone()
    #print(club_info)
    
    if club_info is not None:
        club_details = {
            "Club_Name": club_info[0],
            "President_Name": club_info[1],
            "Advisor_Name": club_info[2],
            "Meeting_Building": club_info[3],
            "Meeting_Room_Number": club_info[4]
        }
    else: 
        club_details={}
    # Fetch all the students enrolled in the club
    cursor.execute('''
        SELECT 
            s.id,
            CONCAT(s.fname, ' ', s.lname) AS Student_Name
        FROM 
            student_club_enrollment AS sce
        JOIN 
            student AS s ON sce.student_id = s.id
        WHERE 
            sce.club_id = %s;
    ''', (club_id,))
    students_enrolled = [{"Student_ID": row[0], "Student_Name": row[1]} for row in cursor.fetchall()]
    #print(students_enrolled)
    
    # Render the club page with all collected information
    return render_template('clubs.html', club=club_details, students=students_enrolled)

# Fetch information about a department
@app.route('/departments')
def departments_page():
    department_id = request.args.get('department-id')
    #print(department_id)
    
    # Fetch basic information about the department
    cursor.execute('''
        SELECT 
            d.name, 
            d.email, 
            d.faculty, 
            d.extension, 
            d.accreditation_status, 
            CONCAT(p.fname, ' ', p.lname) AS Chairperson_Name
        FROM 
            department AS d
        LEFT JOIN 
            professor AS p ON d.chairperson = p.id
        WHERE 
            d.id = %s;
    ''', (department_id,))
    department_info = cursor.fetchone()
    #print(department_info)
    
    if department_info is not None:
            
        department_details = {
            "Department_Name": department_info[0],
            "Department_Email": department_info[1],
            "Faculty": department_info[2],
            "Extension": department_info[3],
            "Accreditation_Status": department_info[4],
            "Chairperson_Name": department_info[5]
        }

    else:
        department_details={}
    # Fetch majors it offers
    cursor.execute('''
        SELECT 
            m.name
        FROM 
            major AS m
        WHERE 
            m.dep_id = %s;
    ''', (department_id,))
    majors = [row[0] for row in cursor.fetchall()]
    #print(majors)

    # Fetch courses it offers
    cursor.execute('''
        SELECT 
            c.id, 
            c.name, 
            c.description, 
            c.credit_hours
        FROM 
            course AS c
        WHERE 
            c.dep_id = %s;
    ''', (department_id,))
    courses = [
        {
            "Course_ID": row[0],
            "Course_Name": row[1],
            "Course_Description": row[2],
            "Credit_Hours": row[3]
        } for row in cursor.fetchall()
    ]
    #print(courses)
    
    # Render the department page with all collected information
    return render_template('departments.html', department=department_details, majors=majors, courses=courses)

#return all students in the major:
@app.route('/majors')
def students_in_major():
    major_name = request.args.get('major-name')
    #print(major_name)
    
    # Fetch all students in the given major
    cursor.execute('''
        SELECT 
            s.id,
            CONCAT(s.fname, ' ', s.lname) AS Student_Name
        FROM 
            student AS s
        JOIN 
            major AS m ON s.major_id = m.id
        WHERE 
            m.name = %s;
    ''', (major_name,))
    students_list = [{"Student_ID": row[0], "Student_Name": row[1]} for row in cursor.fetchall()]
    #print(students_list)

    # Render the template with the list of students in the major
    return render_template('majors.html', major_name=major_name, students=students_list)

#checks the availability of classrooms
@app.route('/rooms')
def room_availability():

    # Get room number and building name from query parameters
    room_number = request.args.get('room_number')
    building_name = request.args.get('building_name')
    #print(room_number + building_name)

    # Fetch room information based on the provided number and building
    cursor.execute('''
        SELECT capacity, type
        FROM room
        WHERE number = %s AND building = %s;
    ''', (room_number, building_name))
    room_info = cursor.fetchone()
    #print(room_info)

    if room_info is not None:
        room_details = {
            "Capacity": room_info[0],
            "Room_Type": room_info[1]
        }
    else: 
        room_details={}
    # Render the room availability page with the collected information
    return render_template('rooms.html', room_details=room_details)

#all info about a section: 
@app.route('/sections')
def section_info():
    section_crn = request.args.get('section-crn')
    #print(section_crn)
    
    # Fetch all information about the section
    cursor.execute('''
        SELECT 
            s.max_enrollment,
            s.actual_enrollment,
            c.name,
            CONCAT(p.fname, ' ', p.lname) AS Professor_Name,
            r.building,
            r.number,
            s.semester_given,
            s.year_given,
            s.rec_crn
        FROM 
            section AS s
        JOIN 
            course AS c ON s.course_id = c.id
        JOIN 
            professor AS p ON s.professor_id = p.id
        JOIN 
            room AS r ON s.room_id = r.number AND s.building = r.building
        WHERE 
            s.crn = %s;
    ''', (section_crn,))
    section = cursor.fetchone()
    #print(section)
    
    if section is not None:
        section_info = {
        "Max_Enrollment": section[0],
        "Actual_Enrollment": section[1],
        "Course_Name": section[2],
        "Professor_Name": section[3],
        "Building": section[4],
        "Room_Number": section[5],
        "Semester": section[6],
        "Year": section[7],
        "Recitation": section[8]
    }
    else:
        section_info={}
        
    if section is not None:
        # Fetch recitation for the section
        cursor.execute('''
            SELECT 
                s.max_enrollment,
                s.actual_enrollment,
                c.name,
                CONCAT(p.fname, ' ', p.lname) AS Professor_Name,
                r.building,
                r.number,
                t.day_schedule,
                t.start_time,
                t.end_time,
                s.semester_given,
                s.year_given
            FROM 
                section AS s
            JOIN 
                course AS c ON s.course_id = c.id
            JOIN 
                professor AS p ON s.professor_id = p.id
            JOIN 
                room AS r ON s.room_id = r.number AND s.building = r.building
            JOIN 
                time AS t ON s.crn = t.section_crn
            WHERE 
                s.crn = %s;
        ''', (section[8],))
        recitation = cursor.fetchone()
        #print(recitation)

    else:
        recitation={}

    # Fetch timing for the section
    cursor.execute('''
        SELECT 
            t.day_schedule,
            t.start_time,
            t.end_time
        FROM 
            time AS t
        WHERE 
            t.section_crn = %s;
    ''', (section_crn,))
    timing = cursor.fetchall()
    #print(timing)


    recitation_info = {
        "Max_Enrollment": recitation[0],
        "Actual_Enrollment": recitation[1],
        "Course_Name": recitation[2],
        "Professor_Name": recitation[3],
        "Building": recitation[4],
        "Room_Number": recitation[5],
        "Day": recitation[6],
        "Start_Time": recitation[7],
        "End_Time": recitation[8],
        "Semester": recitation[9],
        "Year": recitation[10]
    } if recitation else None

    timings = [{
        "Day": t[0],
        "Start_Time": t[1],
        "End_Time": t[2]
    } for t in timing]

    # Render the section page with all collected information
    return render_template('sections.html', section=section_info, recitation=recitation_info, timings=timings)

@app.route('/add_section_time', methods=['GET', 'POST'])
def add_section_time():
    
    # Fetch all CRNs to populate the dropdown
    cursor.execute('SELECT DISTINCT crn FROM section ORDER BY crn')
    crns = cursor.fetchall()
    Days=['Monday','Tuesday','Wednesday','Thursday','Friday']

    if request.method == 'POST':
        # Retrieve data from form
        section_crn = request.form['section_crn']
        day_schedule = request.form['day_schedule']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        try:
            cursor.execute('CALL addsectiontime(%s, %s, %s, %s)', (section_crn, day_schedule, start_time, end_time,))
            conn.commit()
            return render_template('success.html', message="Time added successfully for section CRN: " + section_crn)
        except psycopg2.Error as e:
            conn.rollback()
            return render_template('error.html', error=str(e))
    else:
        # GET request: show the form to the user
        return render_template('add_time_form.html', crns=crns, days=Days)

  
@app.route('/add_section', methods=['GET', 'POST'])
def add_section():

    # Fetch courses, professors, and sections to populate the form
    cursor.execute('SELECT id, name FROM course')
    courses = cursor.fetchall()
    cursor.execute('SELECT id, CONCAT(fname' ' ,  lname) AS name FROM professor')
    professors = cursor.fetchall()
    cursor.execute('SELECT crn FROM section')
    sections = cursor.fetchall()
    cursor.execute('SELECT number, building FROM room')
    room_building= cursor.fetchall()

    if request.method == 'POST':
        # Retrieve data from form
        crn = request.form['crn']
        max_enrollment = request.form['max_enrollment']
        actual_enrollment = request.form['actual_enrollment']
        rec_crn = request.form['rec_crn']
        course_id = request.form['course_id']
        professor_id = request.form['professor_id']
        room = request.form['room']
        building = request.form['building'] 
        semester_given = request.form['semester_given']
        year_given = request.form['year_given']
        print(room)
        print(building)
        rec_crn=rec_crn or None
        try:
            p=cursor.execute('select number from room where building=%s', (building,))
            print(building)
            cursor.execute('CALL AddSection(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (crn, max_enrollment, actual_enrollment, rec_crn, course_id, professor_id,  building, room, semester_given, year_given,))
            conn.commit()
            return render_template('success.html', message="Section added successfully with CRN: " + crn)
        except psycopg2.Error as e:
            conn.rollback()
            return render_template('error.html', error=str(e))
    else:
        # GET request: show the form to the user with dropdowns
        return render_template('add_section.html', courses=courses, professors=professors, sections=sections, room_building=room_building)



@app.route('/sections_by_semester', methods=['GET', 'POST'])
def sections_by_semester():

    # Fetch distinct semesters and years for dropdown
    cursor.execute('SELECT DISTINCT semester_given, year_given FROM section ORDER BY year_given, semester_given')
    semester_years = cursor.fetchall()
    semesters=[ "Fall", "Spring", "Summer" ]
    if request.method == 'POST':
        p_semester_given = request.form['semester_given']
        p_year_given = request.form['year_given']
        # Call the stored function
        cursor.execute('SELECT * FROM GetSectionsBySemester(%s, %s)', (p_semester_given, p_year_given))
        sections = cursor.fetchall()
        return render_template('display_sections.html', sections=sections, semester_years=semester_years, selected_semester=p_semester_given, selected_year=p_year_given)
    else:
        # GET request, show only the form
        return render_template('sections_by_semester_form.html', semester_years=semester_years, semesters=semesters)
    
if __name__ == '__main__':
    app.run(debug=True)





