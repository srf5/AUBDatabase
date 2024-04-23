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
    database="AUBDatabase_project",
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
    print(student_id)

    timeSlots = [
        "9:00 AM", "10:00 AM", "11:00 AM",
        "12:00 PM", "1:00 PM", "2:00 PM",
        "3:00 PM", "4:00 PM", "5:00 PM",
        "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"
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

    # Data to be passed to the template
    return render_template('students.html', timeSlots=timeSlots,information_data=information_data_dict, clubs=clubs_data_list, scheduleData=schedule_data_list, transcriptData=transcript_data_list)

# Route for the professors page
@app.route('/professors')
def professors_page():
    # Mock data for courses given by the professor
    courses_given = [
        {"Name": "Mathematics 101"},
        {"Name": "Physics 201"},
        {"Name": "Chemistry 301"}
    ]
    # Mock data for professor information
    professor_info = {
        "Fname": "John",
        "Lname": "Doe",
        "ResearchArea": "Computer Science",
        "Email": "john.doe@example.com",
        "Title": "Professor",
        "Salary": "$80,000",
        "DOB": "1980-01-01",
        "HiringDate": "2010-09-01",
        "PhoneNumber": "123-456-7890",
        "HighestEducation": "Ph.D. in Computer Science"
    }
    return render_template('professors.html', courses=courses_given, professor=professor_info)

# Route for the courses page
@app.route('/courses')
def courses_page():
    return render_template('courses.html')


if __name__ == '__main__':
    app.run(debug=True)

