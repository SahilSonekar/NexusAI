from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from orders.models import Order
from support.agents import run_support_agent
from .models import Conversation, Message

@login_required
def chat(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get("message")

            if not user_message or not user_message.strip():
                return JsonResponse({'error': 'Empty message'}, status=400)

            order = get_object_or_404(Order, id=order_id, user=request.user)

            conversation, created = Conversation.objects.get_or_create(user=request.user, order=order)

            # Save user message to DB
            Message.objects.create(conversation=conversation, role="user", content=user_message)

            # Send message to LLM agent (saves agent response internally)
            reply = run_support_agent(user_message, conversation.id, order.id, request.user.id)

            return JsonResponse({'reply': reply})

        except Exception as e:
            return JsonResponse({'error': 'Something went wrong while processing your request.'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)