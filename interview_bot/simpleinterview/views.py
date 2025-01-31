from django.http import JsonResponse
from django.shortcuts import render
from groq import Groq

client = Groq(api_key="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")  # Replace with your API key


def interview_simulator(request):

    return render(request, 'simpleinterview/interview_simulator.html')

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