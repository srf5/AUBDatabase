from urllib import request
from flask import Flask,  render_template

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def main_page():
    return render_template('Mainpage.html')

# Route for the students page
@app.route('/students')
def students_page():
    information_data = {
    "Fname": "Alice",
    "Lname": "Smith",
    "Major": "Computer Science",
    "Email": "alice.smith@example.com",
    "GPA": 3.8,
    "DOB": "1998-05-15",
    "Start_Date": "2016-09-01",
    "End_Date": "2020-06-30",
    "Phone_Number": "123-456-7890",
    "Dep_ID": "CS101"
    }

    clubs_data = [
    {"Name": "Chess Club", "MeetingLocation": "Room A101"},
    {"Name": "Photography Club", "MeetingLocation": "Room B202"},
    {"Name": "Debate Club", "MeetingLocation": "Room C303"}
    ]

    schedule_data = {
    "Monday": [
        { "sectionName": "Math 101", "startTime": "9:00 AM", "endTime": "10:30 AM" },
        { "sectionName": "Physics 201", "startTime": "11:00 AM", "endTime": "12:30 PM" }
    ],
    "Tuesday": [
        { "sectionName": "English 102", "startTime": "10:00 AM", "endTime": "11:30 AM" },
        { "sectionName": "Biology 301", "startTime": "1:00 PM", "endTime": "2:30 PM" }
    ],
    }

    timeSlots = [
        "9:00 AM", "10:00 AM", "11:00 AM",
        "12:00 PM", "1:00 PM", "2:00 PM",
        "3:00 PM", "4:00 PM", "5:00 PM",
        "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"
    ]

    TranscriptData = [
    { "CourseName": 'Mathematics 101', "Grade": 'A' },
    { "CourseName": 'Physics 201', "Grade": 'B+' },
    {  "CourseName": 'English Composition', "Grade": 'A-' },
    {  "CourseName": 'History 101', "Grade": 'C' }  
    ]

    return render_template('students.html', student = information_data, clubs=clubs_data, scheduleData=schedule_data, timeSlots=timeSlots, transcriptData=TranscriptData)

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

