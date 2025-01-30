import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from groq import Groq
from .models import *
from .forms import CustomAuthenticationForm, CustomUserCreationForm, EmailVerificationForm
import json
from django.http import JsonResponse
from django.contrib import messages

from .utils import generate_verification_code, send_verification_email

key = "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"

def llm(questions, convoid, ques, post, stage="general"):
    """
    Function to interact with the Groq API for generating AI responses.
    """
    previous_questions = "\n".join([f"Q: {q}" for q in questions]) if questions else "No prior questions."

    prompt = f"""
    You are an AI interviewer conducting a professional interview. Your task is to:
    - Provide a concise, objective evaluation of the candidate's response
    - Create a conversational reply that does not repeat the evaluation
    - Craft a follow-up question that advances the interview
    - After your 3 general questions ask more post related technical questions including problems if necesaary.

    Evaluation Criteria:
    - Clarity of communication
    - Relevance to the question
    - Depth of insight
    - Demonstration of relevant skills/knowledge
    - Alignment with the job role: {post}

    Context:
    - Interview Role: {post}
    - Conversation ID: {convoid}
    - Current Stage: {stage}
    - Previous Questions and Answers:
    {previous_questions}

    Candidate's Input:
    Q: {ques}

    Your Response Format:
    Evaluation: [Provide a brief, professional assessment of the candidate's response and evaluate]
    Reply: [Provide a conversational response that acknowledges the candidate's input and please do not ask any questions here as you will ask it in the next_question segment and just acknowledge the user's response.]
    Next Question: [Ask a focused follow-up question that builds on the conversation]
    """
    try:
        # Initialize Groq client
        client = Groq(api_key=key)

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            temperature=0.7,  # Balanced temperature for consistent yet creative responses
            top_p=1,
        )

        response_text = completion.choices[0].message.content
        print("Groq API Raw Response Content:", response_text)  # Debug the response text

        # Parse response
        evaluation, reply, next_question = parse_ai_response(response_text)
        return evaluation, reply, next_question

    except Exception as e:
        print(f"Error with Groq API: {e}")
        return "Unable to evaluate response.", "Sorry, there was an issue processing the response.", "Can we discuss this further?"

def parse_ai_response(response_text):

    try:
        # Split the response into lines
        lines = response_text.strip().split('\n')

        # Find the index of the line that starts with "Evaluation:"
        eval_index = next((i for i, line in enumerate(lines) if line.startswith("Evaluation:")), None)
        if eval_index is not None:
            # Extract the evaluation
            evaluation = lines[eval_index].split("Evaluation:")[1].strip()

            # Find the index of the line that starts with "Reply:"
            reply_index = next((i for i, line in enumerate(lines[eval_index+1:]) if line.startswith("Reply:")), None)
            if reply_index is not None:
                # Extract the reply
                reply = lines[eval_index+reply_index+1].split("Reply:")[1].strip()

                # Find the index of the line that starts with "Next Question:"
                next_question_index = next((i for i, line in enumerate(lines[eval_index+reply_index+2:]) if line.startswith("Next Question:")), None)
                if next_question_index is not None:
                    # Extract the next question
                    next_question = lines[eval_index+reply_index+next_question_index+2].split("Next Question:")[1].strip()

                    return evaluation, reply, next_question

        # If any of the required sections are not found, return default values
        return "Error in evaluation.", "Error processing response.", "Could you provide more details?"

    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return "Error in evaluation.", "Error processing response.", "Could you provide more details?"


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.utils import timezone
import json
import random
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}\nThis code will expire in 30 seconds.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Store form data in session
            user_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password1'],
            }
            request.session['pending_user'] = user_data

            # Generate and store verification code in session
            code = generate_verification_code()
            request.session['verification_code'] = code
            request.session['code_generated_at'] = timezone.now().timestamp()

            # Send verification email
            send_verification_email(user_data['email'], code)

            return redirect('verify_email')
    else:
        form = CustomUserCreationForm()
    return render(request, 'bot/register.html', {'form': form})


def verify_email(request):
    # Check if we have pending registration
    pending_user = request.session.get('pending_user')
    if not pending_user:
        return redirect('reg')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            submitted_code = data.get('verification_code')
            stored_code = request.session.get('verification_code')
            code_generated_at = request.session.get('code_generated_at')

            # Check if code is expired (30 seconds)
            current_time = timezone.now().timestamp()
            is_expired = (current_time - code_generated_at) > 30

            if stored_code and submitted_code == stored_code and not is_expired:
                # Create the user
                user = User.objects.create_user(
                    username=pending_user['username'],
                    email=pending_user['email'],
                    password=pending_user['password']
                )

                # Clean up session
                for key in ['pending_user', 'verification_code', 'code_generated_at']:
                    if key in request.session:
                        del request.session[key]

                # Authenticate and login the user
                authenticated_user = authenticate(
                    request,
                    username=pending_user['username'],
                    password=pending_user['password']
                )

                if authenticated_user is not None:
                    login(request, authenticated_user, backend='django.contrib.auth.backends.ModelBackend')
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Authentication failed'})
            else:
                error = 'Code expired' if is_expired else 'Invalid code'
                return JsonResponse({'success': False, 'error': error})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'bot/verify_email.html')

def resend_code(request):
    if request.method == 'POST':
        pending_user = request.session.get('pending_user')
        if not pending_user:
            return JsonResponse({'success': False, 'error': 'No pending registration'})

        try:
            # Generate new code
            code = generate_verification_code()
            del request.session['verification_code']
            del request.session['code_generated_at']
            request.session['verification_code'] = code
            request.session['code_generated_at'] = timezone.now().timestamp()
            send_verification_email(pending_user['email'], code)
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'bot/login.html', {'form': form})

@login_required(login_url='reg')
def home_view(request):
    post = posts.objects.all()
    return render(request, 'bot/home.html', {'post': post})

@login_required
def chatcreate(request, post):
    try:
        poste = posts.objects.get(id=post)
        convo = conversation.objects.create(user=request.user,post=poste)
        return redirect('chat', convoid=convo.id)
    except posts.DoesNotExist:
        return HttpResponse("Post not found", status=404)

@login_required
@csrf_exempt
def chat(request, convoid):
    convo = get_object_or_404(conversation, id=convoid)

    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        import json
        data = json.loads(request.body)
        user_response = data.get('response')

        if user_response:
            # Save the user's response
            questions.objects.create(convo=convo, question=user_response, user='user')

            # Fetch all questions for this conversation
            questions_list = list(questions.objects.filter(convo=convo).values_list('question', flat=True))

            # Generate AI response
            post_title = convo.post.post
            evaluation, reply, next_question = llm(questions_list, convoid, user_response, post_title)

            # Save evaluation
            questions.objects.create(convo=convo, question=f"Evaluation: {evaluation}", user='ai-evaluation')

            # Save reply or next question
            if reply:
                questions.objects.create(convo=convo, question=reply, user='ai')
            if next_question:
                questions.objects.create(convo=convo, question=next_question, user='ai')

            # Return AI responses as JSON
            return JsonResponse({
                "evaluation" : evaluation,
                "reply": reply,
                "next_question": next_question,
            })

        return JsonResponse({"error": "Invalid response"}, status=400)

    # Fetch all questions for this conversation
    questions_list = questions.objects.filter(convo=convo)

    # Initialize with a default question if no questions exist
    if not questions_list.exists():
        first_question = "Welcome to the interview! Can you tell me about your experience in this field?"
        questions.objects.create(convo=convo, question=first_question, user='ai')
        questions_list = questions.objects.filter(convo=convo)

    return render(request, 'bot/chat.html', {
        'convo': convo,
        'questions': questions_list,
    })
    # Fetch all questions for this conversation
    questions_list = questions.objects.filter(convo=convo)

    # Initialize with a default question if no questions exist
    if not questions_list.exists():
        first_question = "Welcome to the interview! Can you tell me about your experience in this field?"
        questions.objects.create(convo=convo, question=first_question, user='ai')
        questions_list = questions.objects.filter(convo=convo)

    return render(request, 'bot/chat.html', {
        'convo': convo,
        'questions': questions_list,
    })

@login_required
def previous_interviews(request):
    user = request.user  # Get the current logged-in user
    conversations = conversation.objects.filter(user=user).order_by('-time')
    return render(request, 'bot/previous_interviews.html', {'conversations': conversations})
@login_required
def view_conversation(request, convoid):
    convo = get_object_or_404(conversation, id=convoid, user=request.user)  # Ensure the conversation belongs to the logged-in user
    chats = questions.objects.filter(convo=convo).order_by('created_at')  # Fetch all messages for the conversation

    return render(request, 'bot/view_conversation.html', {'convo': convo, 'chats': chats})


from django.http import JsonResponse
from django.shortcuts import render
from groq import Groq

# Initialize the Groq API client
client = Groq(api_key="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")  # Replace with your API key


def interview_simulator(request):
    """
    Render the Interactive Interview Simulator page.
    """
    return render(request, 'bot/interview_simulator.html')


def generate_question(request):
    """
    Generate a concise technical question based on the job role.
    """
    role = request.GET.get('role')
    if not role:
        return JsonResponse({'error': 'Job role is required'}, status=400)

    prompt = (
        f"Generate a concise technical interview question for the job role: {role}. "
        f"The question should have a one-word or one-sentence answer. Don't generate any extra text other than question"
    )
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    question = response.choices[0].message.content.strip()
    return JsonResponse({'question': question})


def generate_hint(request):
    """
    Generate a hint for a given question.
    """
    question = request.GET.get('question')
    if not question:
        return JsonResponse({'error': 'Question is required'}, status=400)

    prompt = (
        f"Provide a short and helpful hint for answering this question:\n\n"
        f"Question: {question}\nHint:"
    )
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    hint = response.choices[0].message.content.strip()
    return JsonResponse({'hint': hint})


def generate_answer(request):
    """
    Generate the correct answer for a given question.
    """
    question = request.GET.get('question')
    if not question:
        return JsonResponse({'error': 'Question is required'}, status=400)

    prompt = (
        f"Provide the correct answer to the following technical interview question. "
        f"The answer should be concise, in one word or one sentence:\n\n"
        f"Question: {question}\nAnswer:"
    )
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    answer = response.choices[0].message.content.strip()
    return JsonResponse({'answer': answer})


def generate_summary(request, convoid):
    # Get the conversation and related questions
    convo = get_object_or_404(conversation, id=convoid)
    questions_list = list(questions.objects.filter(convo=convo).values_list('question', 'answer'))
    post = convo.post.post
    # Generate the summary using Groq
    interview_summary = genreatesummary(questions_list, post)

    # Check if a summary already exists for the conversation
    sum = summary.objects.filter(convo=convo).first()
    if sum is None:
        # If not, create a new summary instance
        sum = summary(convo=convo)

    # Save the generated summary to the database
    sum.sum = interview_summary
    sum.save()
    return redirect('home')


def genreatesummary(questions ,post ):
    """
    Function to interact with the Groq API for generating AI responses.
    """
    prompt = f"""
    You are an AI interviewer conducting a professional interview. Your task is to:
    - To generate the summary of the sequence of question, answer and evaluation given below
    - Evaluate the entire conversation and generate a constructive feedback on what parameters to improve for the person
    - The question list i have passed has questions you have asked along with your evaluation, follow up questions and the users response and may not be in any specified order

    Evaluation Criteria:
    - Clarity of communication
    - Relevance to the question
    - Depth of insight
    - Demonstration of relevant skills/knowledge
    - Alignment with the job role: {post}

    Your Response Format:
    Summary: [Provide a Proper summary of the interview and a constructive feedback on what parameters to improve for the person]
   
    """
    try:
        # Initialize Groq client
        client = Groq(api_key=key)

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            temperature=0.7,  # Balanced temperature for consistent yet creative responses
            top_p=1,
        )

        response_text = completion.choices[0].message.content
        return response_text

    except Exception as e:
        print(f"Error with Groq API: {e}")
        return "Unable to evaluate summary.", "Please retry."
def summ(request, convoid):
    convo = conversation.objects.filter(id=convoid).first()
    if convo is None:
        return redirect('home')
    sum = summary.objects.filter(convo=convo).first()
    if sum is None:
        sum = summary(convo=convo)
        questions_list = list(questions.objects.filter(convo=convo).values_list('question', 'answer'))
        post = convo.post.post
        sum.sum = genreatesummary(questions_list, post)
        sum.save()
    summarys = sum.sum
    return redirect('home')

def logoutView(request):
    logout(request)
    return redirect('login')