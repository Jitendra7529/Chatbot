# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
import os
from dotenv import load_dotenv
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_openai(message):
    try:
        response = openai.api_key.chat.completions.create(
            model="gpt-4o mini",
            messages=[
                {"role": "system", "content": "You are very helpful"},
                {"role": "user", "content": message},
            ],
        )
        answer = response.choices[0].message.content.strip()  
        return answer
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, there was an issue with the AI service."

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message') 
        response = ask_openai(message) 

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now()) 
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})  


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.htmk', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error while creating a account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password do not match each other'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')