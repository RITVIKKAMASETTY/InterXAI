from groq import Groq

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

