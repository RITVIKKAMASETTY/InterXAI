import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .models import *
import json
from django.http import JsonResponse
from django.contrib import messages
from .utils import *


# views.py

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



