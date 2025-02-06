from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
import logging
from .models import Grade
from .ai_module import generate_quiz_for_subject
from .utils import youtube_search
from .ai_utils import generate_search_query
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import StudentForm, EssayForm
from .models import SubjectContent
import urllib.parse
import numpy as np
import pytesseract, base64, openai, cv2, json, random, pyttsx3
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
from .forms import EditProfileForm  # Create this form in forms.py
from .forms import UpdateProfileForm, UpdatePreferencesForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.http import HttpResponse
from sympy import Eq, symbols, solve, sympify
import re



# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set your OpenAI API key (use environment variables for security in production)
openai.api_key = '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'

# Subjects and Topics Mapping for Different Grades
subjects_map = {
    1: ["First Additional Language", "Mathematics"],
    2: ["First Additional Language", "Mathematics"],
    3: ["First Additional Language", "Mathematics"],
    4: ["Arts and Culture", "First Additional Language", "Home Language", "Mathematics", "Natural Science",
        "Economic Management and Science", "Life Orientation", "Technology", "Social Sciences"],
    5: ["Arts and Culture", "First Additional Language", "Home Language", "Mathematics", "Natural Science",
        "Economic Management and Science", "Life Orientation", "Technology", "Social Sciences"],
    6: ["Arts and Culture", "First Additional Language", "Home Language", "Mathematics", "Natural Science",
        "Economic Management and Science", "Life Orientation", "Technology", "Social Sciences"],
    7: ["Arts and Culture", "First Additional Language", "Home Language", "Mathematics", "Natural Science",
        "Economic Management and Science", "Life Orientation", "Technology", "Social Sciences"],
    8: ["Arts and Culture", "First Additional Language", "Home Language", "Mathematics", "Natural Science",
        "Economic Management and Science", "Life Orientation", "Technology", "Social Sciences"],
    9: ["Arts and Culture", "First Additional Language", "Home Language", "Mathematics", "Natural Science",
        "Economic Management and Science", "Life Orientation", "Technology", "Social Sciences"],
    10: ["First Additional Language", "Home Language", "Mathematics", "Physical Science", "Information Technology",
         "Geography", "Life Science", "History", "Accounting", "Economics", "Business Studies"],
    11: ["First Additional Language", "Home Language", "Mathematics", "Physical Science", "Information Technology",
         "Geography", "Life Science", "History", "Accounting", "Economics", "Business Studies"],
    12: ["First Additional Language", "Home Language", "Mathematics", "Physical Science", "Information Technology",
         "Geography", "Life Science", "History", "Accounting", "Economics", "Business Studies"]
}

# Helper functions
def get_subjects_for_grade(grade):
    # Predefined subjects based on grade levels
    subjects_map = {
        1: ["First Additional Language", "Mathematics"],
        2: ["First Additional Language", "Mathematics"],
        3: ["First Additional Language", "Mathematics"],
        4: ["Arts and Culture", "First Additional Language", "Home Language",
            "Mathematics", "Natural Science", "Economic Management and Science",
            "Life Orientation", "Technology", "Social Sciences"],
        5: ["Arts and Culture", "First Additional Language", "Home Language",
            "Mathematics", "Natural Science", "Economic Management and Science",
            "Life Orientation", "Technology", "Social Sciences"],
        6: ["Arts and Culture", "First Additional Language", "Home Language",
            "Mathematics", "Natural Science", "Economic Management and Science",
            "Life Orientation", "Technology", "Social Sciences"],
        7: ["Arts and Culture", "First Additional Language", "Home Language",
            "Mathematics", "Natural Science", "Economic Management and Science",
            "Life Orientation", "Technology", "Social Sciences"],
        8: ["Arts and Culture", "First Additional Language", "Home Language",
            "Mathematics", "Natural Science", "Economic Management and Science",
            "Life Orientation", "Technology", "Social Sciences"],
        9: ["Arts and Culture", "First Additional Language", "Home Language",
            "Mathematics", "Natural Science", "Economic Management and Science",
            "Life Orientation", "Technology", "Social Sciences"],
        10: ["First Additional Language", "Home Language", "Mathematics",
             "Physical Science", "Information Technology", "Geography",
             "Life Science", "History", "Accounting", "Economics", "Business Studies"],
        11: ["First Additional Language", "Home Language", "Mathematics",
             "Physical Science", "Information Technology", "Geography",
             "Life Science", "History", "Accounting", "Economics", "Business Studies"],
        12: ["First Additional Language", "Home Language", "Mathematics",
             "Physical Science", "Information Technology", "Geography",
             "Life Science", "History", "Accounting", "Economics", "Business Studies"],
    }
    return subjects_map.get(grade, [])

#added recently
def get_topics_for_subject(subject, grade):
    topics_map = {
        1: {
            "First Additional Language": ["Listening and Speaking", "Reading and Phonics", "Writing", "Language Structure"],
            "Mathematics": ["Numbers, Operations, and Relationships", "Addition, Substraction, Multiplication and Division", "Space and Shape", "Measurement", "Data Handling"],
        },
        2: {
            "First Additional Language": ["Listening and Speaking", "Reading and Phonics", "Writing", "Language Structure"],
            "Mathematics": ["Numbers, Operations, and Relationships", "Addition, Substraction, Multiplication and Division", "Space and Shape", "Measurement", "Data Handling"],
        },
        3: {
            "First Additional Language": ["Listening and Speaking", "Reading and Phonics", "Writing", "Language Structure"],
            "Mathematics": ["Numbers, Operations, and Relationships", "Patterns, Functions, and Algebra", "Space and Shape", "Measurement", "Data Handling"],
        },
        4: {
            "Arts and Culture": ["Elements of Art", "Drama", "Dance", "Music Theory and Performance", "Visual Arts (Drawing, Painting)"],
            "First Additional Language": ["Listening Comprehension", "Reading and Viewing", "Writing and Presenting", "Language Structures and Conventions"],
            "Home Language": ["Listening and Speaking", "Reading and Viewing", "Writing and Presenting", "Language Use and Structure"],
            "Mathematics": ["Whole Numbers, Fractions, and Decimals", "Measurement (Length, Mass, Volume, Time)", "Geometry (Shapes and Space)", "Patterns and Algebra", "Data Handling"],
            "Natural Science": ["Life and Living", "Energy and Change", "Planet Earth and Beyond", "Matter and Materials"],
            "Economic Management Sciences (EMS)": ["Introduction to Economics", "Financial Literacy (Money and Banking)", "Production and Entrepreneurship", "Economic Systems"],
            "Life Orientation": ["Personal Development", "Health and Environmental Responsibility", "Social Responsibility", "Physical Education"],
            "Technology": ["Systems and Control", "Processing and Manufacturing", "Structures and Mechanisms"],
            "Social Sciences": ["History: South African History, Early Civilizations, Explorations", "Geography: Map Skills, Water Resources, Weather and Climate"],
        },
        5: {
            "Arts and Culture": ["Elements of Art", "Drama", "Dance", "Music Theory and Performance", "Visual Arts (Drawing, Painting)"],
            "First Additional Language": ["Listening Comprehension", "Reading and Viewing", "Writing and Presenting", "Language Structures and Conventions"],
            "Home Language": ["Listening and Speaking", "Reading and Viewing", "Writing and Presenting", "Language Use and Structure"],
            "Mathematics": ["Whole Numbers, Fractions, and Decimals", "Measurement (Length, Mass, Volume, Time)", "Geometry (Shapes and Space)", "Patterns and Algebra", "Data Handling"],
            "Natural Science": ["Life and Living", "Energy and Change", "Planet Earth and Beyond", "Matter and Materials"],
            "Economic Management Sciences (EMS)": ["Introduction to Economics", "Financial Literacy (Money and Banking)", "Production and Entrepreneurship", "Economic Systems"],
            "Life Orientation": ["Personal Development", "Health and Environmental Responsibility", "Social Responsibility", "Physical Education"],
            "Technology": ["Systems and Control", "Processing and Manufacturing", "Structures and Mechanisms"],
            "Social Sciences": ["History: South African History, Early Civilizations, Explorations", "Geography: Map Skills, Water Resources, Weather and Climate"],
        },
        6: {
            "Arts and Culture": ["Elements of Art", "Drama", "Dance", "Music Theory and Performance", "Visual Arts (Drawing, Painting)"],
            "First Additional Language": ["Listening Comprehension", "Reading and Viewing", "Writing and Presenting", "Language Structures and Conventions"],
            "Home Language": ["Listening and Speaking", "Reading and Viewing", "Writing and Presenting", "Language Use and Structure"],
            "Mathematics": ["Whole Numbers, Fractions, and Decimals", "Measurement (Length, Mass, Volume, Time)", "Geometry (Shapes and Space)", "Patterns and Algebra", "Data Handling"],
            "Natural Science": ["Life and Living", "Energy and Change", "Planet Earth and Beyond", "Matter and Materials"],
            "Economic Management Sciences (EMS)": ["Introduction to Economics", "Financial Literacy (Money and Banking)", "Production and Entrepreneurship", "Economic Systems"],
            "Life Orientation": ["Personal Development", "Health and Environmental Responsibility", "Social Responsibility", "Physical Education"],
            "Technology": ["Systems and Control", "Processing and Manufacturing", "Structures and Mechanisms"],
            "Social Sciences": ["History: South African History, Early Civilizations, Explorations", "Geography: Map Skills, Water Resources, Weather and Climate"],
        },
        7: {
            "Arts and Culture": ["Creative Expression", "Music Theory and Practice", "Drama", "Dance Techniques", "Art Appreciation"],
            "First Additional Language": ["Listening and Speaking", "Reading Comprehension", "Writing and Presenting", "Grammar and Language Structures"],
            "Home Language": ["Reading and Viewing", "Listening and Speaking", "Writing and Presenting", "Language Structures", "" "", ""],
            "Mathematics": ["Number Systems (Integers, Fractions, Decimals)", "Geometry (Angles, Shapes, Symmetry)", "Algebra (Expressions, Equations)", "Measurement (Time, Area, Volume)", "Data Handling and Probability"],
            "Natural Science": ["Cells and Systems", "Ecology and Ecosystems", "Energy and Power", "Matter and Materials", "Solar System and Space Exploration"],
            "Economic Management Sciences (EMS)": ["Economics and Entrepreneurship", "Budgeting and Accounting", "Business Concepts", "Government and Taxes"],
            "Life Orientation": ["Development of Self in Society", "Constitutional Rights and Responsibilities", "Health, Social, and Environmental Responsibility", "Physical Education"],
            "Technology": ["Design and Problem Solving", "Mechanical Systems", "Electrical Systems", "Structures"],
            "Social Sciences": ["History: Apartheid, World War II, African History", "Geography: Settlement Patterns, Resources", "Environmental Issues"],
        },
        8: {
            "Arts and Culture": ["Creative Expression", "Music Theory and Practice", "Drama", "Dance Techniques", "Art Appreciation"],
            "First Additional Language": ["Listening and Speaking", "Reading Comprehension", "Writing and Presenting", "Grammar and Language Structures"],
            "Home Language": ["Reading and Viewing", "Listening and Speaking", "Writing and Presenting", "Language Structures", "" "", ""],
            "Mathematics": ["Number Systems (Integers, Fractions, Decimals)", "Geometry (Angles, Shapes, Symmetry)", "Algebra (Expressions, Equations)", "Measurement (Time, Area, Volume)", "Data Handling and Probability"],
            "Natural Science": ["Cells and Systems", "Ecology and Ecosystems", "Energy and Power", "Matter and Materials", "Solar System and Space Exploration"],
            "Economic Management Sciences (EMS)": ["Economics and Entrepreneurship", "Budgeting and Accounting", "Business Concepts", "Government and Taxes"],
            "Life Orientation": ["Development of Self in Society", "Constitutional Rights and Responsibilities", "Health, Social, and Environmental Responsibility", "Physical Education"],
            "Technology": ["Design and Problem Solving", "Mechanical Systems", "Electrical Systems", "Structures"],
            "Social Sciences": ["History: Apartheid, World War II, African History", "Geography: Settlement Patterns, Resources", "Environmental Issues"],
        },
        9: {
            "Arts and Culture": ["Creative Expression", "Music Theory and Practice", "Drama", "Dance Techniques", "Art Appreciation"],
            "First Additional Language": ["Listening and Speaking", "Reading Comprehension", "Writing and Presenting", "Grammar and Language Structures"],
            "Home Language": ["Reading and Viewing", "Listening and Speaking", "Writing and Presenting", "Language Structures", "" "", ""],
            "Mathematics": ["Number Systems (Integers, Fractions, Decimals)", "Geometry (Angles, Shapes, Symmetry)", "Algebra (Expressions, Equations)", "Measurement (Time, Area, Volume)", "Data Handling and Probability"],
            "Natural Science": ["Cells and Systems", "Ecology and Ecosystems", "Energy and Power", "Matter and Materials", "Solar System and Space Exploration"],
            "Economic Management Sciences (EMS)": ["Economics and Entrepreneurship", "Budgeting and Accounting", "Business Concepts", "Government and Taxes"],
            "Life Orientation": ["Development of Self in Society", "Constitutional Rights and Responsibilities", "Health, Social, and Environmental Responsibility", "Physical Education"],
            "Technology": ["Design and Problem Solving", "Mechanical Systems", "Electrical Systems", "Structures"],
            "Social Sciences": ["History: Apartheid, World War II, African History", "Geography: Settlement Patterns, Resources", "Environmental Issues"],
        },
        10: {
            "First Additional Language": ["Literature Analysis", "Essay Writing", "Comprehension", "Advanced Grammar"],
            "Home Language": ["Reading and Viewing", "Writing and Presenting", "Language Structures"],
            "Mathematics": ["Algebra", "Geometry", "Trigonometry", "Probability and Statistics", "Financial Mathematics"],
            "Physical Science": ["Mechanics (Forces, Motion, Energy)", "Chemical Reactions and Equilibrium", "Waves, Sound, and Light", "Electricity and Magnetism", "Organic Chemistry"],
            "Informational Technology": ["Software Development (Programming, Databases)", "Networks and Internet Technology", "Data Structures", "Information Management"],
            "Geography": ["Geomorphology", "Climatology", "Population Studies", "Economic Geography", "Map Skills and GIS"],
            "Life Sciences": ["DNA and Genetics", "Evolution and Natural Selection", "Human Physiology (Systems, Health)", "Human Physiology (Systems, Health)", "Microbiology and Disease"],
            "History": ["South African Struggle for Freedom", "World History (Cold War, Colonialism)", "Human Rights and Social Movements", "African History (Post-Colonialism, Apartheid)"],
            "Accounting": ["Financial Statements", "General Ledger", "Income and Expenditure", "Asset Management", "Cost Accounting"],
            "Economics": ["Micro and Macroeconomics", "Economic Growth and Development", "Globalization and Trade", "Inflation and Unemployment"],
            "Business Studies": ["Business Environment", "Entrepreneurship and Leadership", "Marketing and Sales Strategies", "Human Resources Management"],
        },
        11: {
            "First Additional Language": ["Literature Analysis", "Essay Writing", "Comprehension", "Advanced Grammar"],
            "Home Language": ["Reading and Viewing", "Writing and Presenting", "Language Structures"],
            "Mathematics": ["Algebra", "Geometry", "Trigonometry", "Probability and Statistics", "Financial Mathematics"],
            "Physical Science": ["Mechanics (Forces, Motion, Energy)", "Chemical Reactions and Equilibrium", "Waves, Sound, and Light", "Electricity and Magnetism", "Organic Chemistry"],
            "Informational Technology": ["Software Development (Programming, Databases)", "Networks and Internet Technology", "Data Structures", "Information Management"],
            "Geography": ["Geomorphology", "Climatology", "Population Studies", "Economic Geography", "Map Skills and GIS"],
            "Life Sciences": ["DNA and Genetics", "Evolution and Natural Selection", "Human Physiology (Systems, Health)", "Microbiology and Disease"],
            "History": ["South African Struggle for Freedom", "World History (Cold War, Colonialism)", "Human Rights and Social Movements", "African History (Post-Colonialism, Apartheid)"],
            "Accounting": ["Financial Statements", "General Ledger", "Income and Expenditure", "Asset Management", "Cost Accounting"],
            "Economics": ["Micro and Macroeconomics", "Economic Growth and Development", "Globalization and Trade", "Inflation and Unemployment"],
            "Business Studies": ["Business Environment", "Entrepreneurship and Leadership", "Marketing and Sales Strategies", "Human Resources Management"],
        },
        12: {
            "First Additional Language": ["Literature Analysis", "Essay Writing", "Comprehension", "Advanced Grammar"],
            "Home Language": ["Reading and Viewing", "Writing and Presenting", "Language Structures"],
            "Mathematics": ["Algebra", "Geometry", "Trigonometry", "Probability and Statistics", "Financial Mathematics"],
            "Physical Science": ["Mechanics (Forces, Motion, Energy)", "Chemical Reactions and Equilibrium", "Waves, Sound, and Light", "Electricity and Magnetism", "Organic Chemistry"],
            "Informational Technology": ["Software Development (Programming, Databases)", "Networks and Internet Technology", "Data Structures", "Information Management"],
            "Geography": ["Geomorphology", "Climatology", "Population Studies", "Economic Geography", "Map Skills and GIS"],
            "Life Sciences": ["DNA and Genetics", "Evolution and Natural Selection", "Human Physiology (Systems, Health)", "Human Physiology (Systems, Health)", "Microbiology and Disease"],
            "History": ["South African Struggle for Freedom", "World History (Cold War, Colonialism)", "Human Rights and Social Movements", "African History (Post-Colonialism, Apartheid)"],
            "Accounting": ["Financial Statements", "General Ledger", "Income and Expenditure", "Asset Management", "Cost Accounting"],
            "Economics": ["Micro and Macroeconomics", "Economic Growth and Development", "Globalization and Trade", "Inflation and Unemployment"],
            "Business Studies": ["Business Environment", "Entrepreneurship and Leadership", "Marketing and Sales Strategies", "Human Resources Management"],
        }
    }
    return topics_map.get(grade, {}).get(subject, [])



def generate_content_for_subject(subject, grade):
    prompt = f"Generate detailed learning content for the subject '{subject}' for Grade {grade} in a South African curriculum."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        content = response['choices'][0]['message']['content'].strip()
        return content
    except Exception as e:
        return {"error": str(e)}

def parse_quiz_from_response(response):
    quiz = []
    questions = response.split('\n\n')

    for question in questions:
        lines = question.split('\n')
        if len(lines) >= 5:
            question_text = lines[0].strip()
            options = [line.split(' ', 1)[1].strip() for line in lines[1:5]]

            # Ensure the correct answer format is extracted properly
            answer_line = next((line for line in lines if "answer" in line.lower()), None)
            answer = answer_line.split(':')[-1].strip().upper() if answer_line else None

            if answer and question_text:
                quiz.append({
                    "question": question_text,
                    "options": options,
                    "correct_answer": answer
                })

    return quiz

# Views
def home(request):
    grades = Grade.objects.all()
    return render(request, 'home.html', {'grades': grades})

def subjects_view(request, grade):
    subjects = get_subjects_for_grade(grade)
    return JsonResponse({"subjects": subjects})

#new views
def subject_content_view(request, grade, subject):
    content = generate_content_for_subject(subject, grade)
    return JsonResponse({"content": content})

def grade_page(request, grade):
    # Replace this with your logic for getting subjects
    subjects = get_subjects_for_grade(grade)  # Example: ['Math', 'Science', 'English']

    return render(request, 'grade_page.html', {
        'grade': grade,
        'subjects': subjects  # Pass the list of subjects to the template
    })

def grade_detail_view(request, grade):
    subjects = get_subjects_for_grade(grade)
    return render(request, 'grade_detail.html', {'grade': grade, 'subjects': subjects})

def subject_detail_view(request, grade, subject):
    topics = get_topics_for_subject(subject, grade)
    return render(request, 'subject_detail.html', {
        'grade': grade,
        'subject': subject,
        'topics': topics,
    })

def topic_content_view(request, grade, subject, topic):
    subject = urllib.parse.unquote(subject)
    topic = urllib.parse.unquote(topic)
    content = generate_content_for_topic(grade, subject, topic)
    return JsonResponse({'content': content})

def generate_content_for_topic(grade, subject, topic):
    prompt = f"Generate detailed learning content for the topic '{topic}' in the subject '{subject}' for Grade {grade} following the South African curriculum."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational assistant helping students learn."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        content = response['choices'][0]['message']['content'].strip()
        return content
    except Exception as e:
        return f"An error occurred: {e}"



def topic_content(request, grade, subject, topic):
    # Logic to retrieve content based on grade, subject, and topic
            content = get_content(grade, subject, topic)  # Replace with your actual content retrieval logic

            if content:
                return JsonResponse({'content': content})
            else:
                return JsonResponse({'error': 'No content found for this topic.'}, status=404)

def grades_view(request):
            grade = 10  # You can set this dynamically based on user input
            subjects = get_subjects_for_grade(grade)
            subjects_content = {subject: generate_content_for_subject(subject, grade) for subject in subjects}
            return render(request, 'grade_page.html', {'grade': grade, 'subjects_content': subjects_content})

#Search views
def search_view(request):
    search_query = ''
    video_data = None

    if request.method == 'POST':
        question = request.POST.get('question')
        search_query = generate_search_query(question)
        video_data = youtube_search(search_query)

    return render(request, 'search.html', {
        'search_query': search_query,
        'video_data': video_data,
    })


def grade_content_view(request, grade):
    # Retrieve the subject contents based on the grade
    subject_contents = SubjectContent.objects.filter(grade=grade)

    # Prepare the context to send to the template
    context = {
        'grade': grade,
        'subject_contents': {subject.content_name: subject.content for subject in subject_contents}
    }

    return render(request, 'grade_content.html', {'grade': grade})


#Assistance views
def assistant(request):
    if request.method == 'POST':
        user_input = request.POST.get('query')

        # Use the gpt-3.5-turbo model instead of the deprecated one
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.7
            )
            response_text = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            response_text = f"Sorry, something went wrong: {e}"

        return JsonResponse({"response": response_text})

    return render(request, 'index.html')

def process_query(query):
    # Simple NLP handling logic
    if "weather" in query.lower():
        return "The weather today is sunny."
    elif "time" in query.lower():
        return "It's 2 PM."
    else:
        return random.choice(["I'm sorry, I didn't understand that.", "Can you please repeat?"])

def speak_response(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def check_essay(request):
    corrected_text = ''
    if request.method == 'POST':
        form = EssayForm(request.POST)
        if form.is_valid():
            essay_text = form.cleaned_data['essay_text']
            corrected_text = correct_spelling(essay_text)
    else:
        form = EssayForm()

    return render(request, 'essay_form.html', {'form': form, 'corrected_text': corrected_text})

def correct_spelling(text):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": f"Please correct the spelling and grammar mistakes in the following text: {text}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

#scan view
# Set the Tesseract command path (adjust path if necessary)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Image preprocessing function for improved OCR accuracy
def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply bilateral filter to reduce noise while keeping edges sharp
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    # Thresholding to binarize the image
    _, thresh_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh_image

# View to display the main page with camera scanning
def new(request):
    return render(request, 'new.html')

# View to handle image upload and text extraction
@csrf_exempt
def extract_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            image_data = data['image']  # Extract base64 image data

            # Remove base64 header
            image_data = image_data.split(',')[1]
            img = base64.b64decode(image_data)
            nparr = np.frombuffer(img, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                return JsonResponse({'error': 'Failed to decode image.'}, status=400)

            # Preprocess the image
            preprocessed_image = preprocess_image(image)

            # Perform OCR using Tesseract with custom configurations
            custom_config = r'--oem 3 --psm 6'  # Use OEM 3 (default LSTM OCR) and PSM 6 (single uniform block of text)
            text = pytesseract.image_to_string(preprocessed_image, config=custom_config).strip()

            if not text:
                return JsonResponse({'error': 'No text extracted from the image.'}, status=400)

            return JsonResponse({'text': text}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# View to handle question-answering using extracted text and OpenAI
@csrf_exempt
def ask_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            captured_text = data['text']
            question = data['question']

            # Use the chat-based format
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"The following text was extracted from an image: '{captured_text}'."},
                {"role": "user", "content": f"Based on this text, the user asks: '{question}'."}
            ]

            # Make API call to the correct endpoint for chat models
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or use 'gpt-3.5-turbo'
                messages=messages,
                max_tokens=150,
                temperature=0.5
            )
            ai_answer = response['choices'][0]['message']['content'].strip()

            return JsonResponse({'answer': ai_answer}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


#new views beware
def contact_us(request):
    return render(request, 'contact_us.html')

def user_guide(request):
    return render(request, 'user_guide.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

#login views
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password-confirm']

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use.')
            return redirect('signup')

        if password == password_confirm:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            # Check if the profile already exists

            if messages.success(request, 'Account created successfully! You can now log in.'):
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
            return redirect('signup')

    return render(request, 'signup.html')
@login_required
def some_protected_view(request):
    # Logic for views that require login
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after successful login
        else:
            # Return an 'invalid login' error message
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UpdateProfileForm(instance=request.user)
    return render(request, 'update_profile.html', {'form': form})

@login_required
def update_preferences(request):
    if request.method == 'POST':
        form = UpdatePreferencesForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UpdatePreferencesForm(instance=request.user.profile)
    return render(request, 'update_preferences.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        profile = request.user.profile  # Access the user's profile
        if 'picture' in request.FILES:
            profile.picture = request.FILES['picture']  # Save the uploaded image
            profile.save()  # Save changes to the profile
        return redirect('profile')  # Redirect to the same page to reload with updated image

    # Pass user profile to the template to display current picture
    return render(request, 'profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('edit_profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')  # Redirect to profile page after changing password


# Define the variable for algebraic equations
x = symbols('x')

def chat_view(request):
    # Display the main chat page
    conversation_history = request.session.get("conversation", [])
    return render(request, 'chat_form.html', {'conversation': conversation_history})

# Define x as a symbolic variable for algebraic equations
x = symbols('x')

@csrf_exempt
def chat_step(request):
    if request.method == "POST":
        question_input = request.POST.get("question")  # User question
        answer_input = request.POST.get("answer")      # User answer
        conversation_history = request.session.get("conversation", [])  # Track conversation
        question = request.session.get("question", None)  # Current question
        question_type = request.session.get("question_type", None)  # Arithmetic or algebraic

        if question_input:
            # Handle new question
            question_input = question_input.replace("^", "**")  # Convert `^` to Python's `**`
            request.session['question'] = question_input

            # Detect question type
            if '=' in question_input or re.search(r'x', question_input):  # Algebraic equations
                question_type = 'algebra'
            else:
                question_type = 'arithmetic'

            request.session['question_type'] = question_type
            conversation_history.append({"role": "user", "content": question_input})
            request.session['conversation'] = conversation_history

            return JsonResponse({"reply": f"Question received! Please submit your answer to: {question_input}"})

        elif answer_input:
            # Handle answer submission
            conversation_history.append({"role": "user", "content": answer_input})

            if question_type == 'algebra':
                # Solve algebraic equation
                try:
                    question_input = request.session['question']

                    # Split into left and right sides of the equation
                    if '=' in question_input:
                        left_side, right_side = map(str.strip, question_input.split('='))
                    else:
                        left_side, right_side = question_input, '0'

                    # Parse the equation with SymPy
                    equation = Eq(sympify(left_side), sympify(right_side))  # Properly parse equation
                    correct_solution = solve(equation, x)

                    # Parse user's answer
                    user_solution = [
                        sympify(val.strip()) for val in answer_input.replace("x =", "").split("or")
                    ]

                    # Compare user's answer with the correct solution
                    if set(correct_solution) == set(user_solution):
                        reply_message = "That's correct! You've solved it."
                    else:
                        reply_message = "That's incorrect. The correct solution is: " + ", ".join(map(str, correct_solution))

                except Exception as e:
                    reply_message = f"There seems to be an error in your calculation: {str(e)}"

            elif question_type == 'arithmetic':
                # Solve arithmetic expressions
                try:
                    question_input = request.session['question']
                    expected_answer = eval(question_input)
                    user_answer = eval(answer_input)

                    if user_answer == expected_answer:
                        reply_message = "That's correct!"
                    else:
                        reply_message = f"That's incorrect. The correct answer is: {expected_answer}"

                except Exception as e:
                    reply_message = f"There seems to be an error in your calculation: {str(e)}"

            else:
                reply_message = "Unknown question type. Please try again."

            # Update conversation and reset question state
            conversation_history.append({"role": "assistant", "content": reply_message})
            request.session['conversation'] = conversation_history

            if "That's correct!" in reply_message:
                request.session['question'] = None
                request.session['question_type'] = None

            return JsonResponse({"reply": reply_message})

    return JsonResponse({"error": "This endpoint only accepts POST requests."}, status=405)


# View to Generate Quiz and Handle User Answers
def quiz_combined(request):
    selected_grade = None
    selected_subject = None
    selected_topic = None
    subjects_for_selected_grade = []
    user_answers = {}

    if request.method == 'POST':
        selected_grade = request.POST.get('grade')
        selected_subject = request.POST.get('subject')
        selected_topic = request.POST.get('topic')

        if selected_grade:
            selected_grade = int(selected_grade)
            subjects_for_selected_grade = subjects_map.get(selected_grade, [])

        for i in range(1, 4):
            answer_key = f'answer_{i}'
            user_answer = request.POST.get(answer_key, "").strip()
            user_answers[answer_key] = user_answer if user_answer else None

        if selected_subject and selected_topic and selected_grade:
            prompt = f"Generate 8 quiz questions for Grade {selected_grade}, Subject {selected_subject}, on the topic '{selected_topic}'. Each question should be followed by the correct answer, in this format: 'Q: question? A: answer'."

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant generating both question and answers."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )

                # Debugging output to check raw response
                print(response)

                response_text = response['choices'][0]['message']['content'].strip()

                if response_text:
                    quiz_content = response_text.split("\n")
                    questions = {}
                    correct_answers = {}

                    for i, line in enumerate(quiz_content, start=1):
                        if "Q:" in line and "A:" in line:
                            question, answer = line.split("A:", 1)
                            questions[f'question_{i}'] = question.replace("Q:", "").strip()
                            correct_answers[f'question_{i}'] = answer.strip()

                    if not questions or not correct_answers:
                        raise ValueError("The API did not generate valid quiz questions.")

                    request.session['questions'] = questions
                    request.session['correct_answers'] = correct_answers

                    return render(request, 'quiz_combined.html', {
                        'subjects_map': subjects_map,
                        'quiz_generated': True,
                        'selected_grade': selected_grade,
                        'selected_subject': selected_subject,
                        'selected_topic': selected_topic,
                        'subjects_for_selected_grade': subjects_for_selected_grade,
                        'questions': questions,
                        'correct_answers': correct_answers,
                    })
                else:
                    raise ValueError("No valid questions or answers were generated.")

            except Exception as e:
                return render(request, 'quiz_combined.html', {
                    'subjects_map': subjects_map,
                    'error': f'Error: {str(e)}',
                    'selected_grade': selected_grade,
                    'selected_subject': selected_subject,
                    'selected_topic': selected_topic,
                    'subjects_for_selected_grade': subjects_for_selected_grade,
                })

    return render(request, 'quiz_combined.html', {
        'subjects_map': subjects_map,
        'selected_grade': selected_grade,
        'selected_subject': selected_subject,
        'selected_topic': selected_topic,
        'subjects_for_selected_grade': subjects_for_selected_grade,
    })

# Handle quiz result submission and scoring
def submit_quiz(request):
    if request.method == 'POST':
        user_answers = {}
        correct_answers = request.session.get('correct_answers', {})
        correct_count = 0

        if not correct_answers:
            return HttpResponse("No correct answers found in the session.")

        for i in range(1, 9):
            # Get the user's answer for each question
            user_answer = request.POST.get(f'answer_{i}', '').strip().lower()
            correct_answer = correct_answers.get(f'question_{i}', '').strip().lower()

            # Normalize both user answer and correct answer
            def normalize_answer(answer):
                # Remove 'x =' and extra spaces, focusing on numeric value
                return ''.join(filter(str.isdigit, answer)) if answer else ""

            normalized_user_answer = normalize_answer(user_answer)
            normalized_correct_answer = normalize_answer(correct_answer)

            # Compare the normalized answers
            is_correct = normalized_user_answer == normalized_correct_answer
            user_answers[f'question_{i}'] = {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
            }

            if is_correct:
                correct_count += 1

        # Calculate the score
        total_questions = len(correct_answers)
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        # Store the user's answers, score, and other details in the session
        request.session['user_answers'] = user_answers
        request.session['score'] = score
        request.session['correct_count'] = correct_count
        request.session['total_questions'] = total_questions

        return redirect('quiz_results')  # Redirect to results page

    return HttpResponse("Invalid request method.")


# Display quiz results
def quiz_results(request):
    user_answers = request.session.get('user_answers', {})
    score = request.session.get('score', 0)
    correct_count = request.session.get('correct_count', 0)
    total_questions = request.session.get('total_questions', 0)

    return render(request, 'quiz_results.html', {
        'user_answers': user_answers,
        'score': score,
        'correct_count': correct_count,
        'total_questions': total_questions,
    })


def get_quiz_data(subject):
    return QUIZ_DATA.get(subject, [])

def subject_quiz_view(request, grade, subject):
    if request.method == "POST":
        user_answers = {int(key.split("_")[1]): value for key, value in request.POST.items() if key.startswith("question_")}

        quiz = request.session.get("quiz")
        results = []
        for index, question in enumerate(quiz):
            correct = question["correct_answer"] == user_answers.get(index)
            results.append({
                "question": question["question"],
                "correct_answer": question["correct_answer"],
                "user_answer": user_answers.get(index),
                "correct": correct
            })

        return render(request, 'subject_quiz.html', {
            'quiz': quiz,
            'subject': subject,
            'grade': grade,
            'user_answers': user_answers,
            'results': results,
        })

    if "quiz" in request.session:
        del request.session["quiz"]

    quiz = generate_quiz_for_subject(subject, grade)
    request.session["quiz"] = quiz

    return render(request, 'subject_quiz.html', {
        'quiz': quiz,
        'subject': subject,
        'grade': grade,
    })

def quiz_view(request):
    grades = list(range(1, 13))  # Grade 1 to 12
    grade = int(request.GET.get('grade', 1))  # Default to Grade 1 if not specified
    subjects = get_subjects_for_grade(grade)  # Get subjects based on grade
    selected_subject = request.GET.get('subject', subjects[0])  # Get selected subject

    if request.method == "POST":
        user_answers = process_user_answers(request)
        request.session["user_answers"] = user_answers  # Store answers in session
        quiz = request.session.get("quiz", [])  # Get the quiz from session
        results = evaluate_quiz(quiz, user_answers)  # Evaluate the quiz

        return render(request, 'quizzes.html', {
            'subjects': subjects,
            'selected_subject': selected_subject,
            'quiz': quiz,
            'grade': grade,
            'results': results,
            'grades': grades,
            'selected_grade': grade,
        })

    quiz = generate_quiz_for_subject(selected_subject, grade)  # Generate the quiz
    request.session["quiz"] = quiz  # Store the quiz in session

    user_answers = request.session.get("user_answers", {})

    return render(request, 'quizzes.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'quiz': quiz,
        'grade': grade,
        'grades': grades,
        'selected_grade': grade,
        'user_answers': user_answers,
    })

def process_user_answers(request):
    logging.debug(f"POST data: {request.POST}")
    user_answers = {}
    quiz = request.session.get("quiz", [])

    for idx, question in enumerate(quiz, start=1):
        question_key = f"question_{idx}"
        user_answers[idx] = request.POST.get(question_key, "Unanswered").strip() or "Unanswered"

    return user_answers

def evaluate_quiz(quiz, user_answers):
    results = []
    for idx, question in enumerate(quiz):
        correct = question["correct_answer"] == user_answers.get(idx, "Unanswered")
        results.append({
            "question": question["question"],
            "correct_answer": question["correct_answer"],
            "user_answer": user_answers.get(idx),
            "correct": correct
        })
    return results

def about(request):
    return render(request, 'about.html')


def help_center(request):
    return render(request, 'help_center.html')
