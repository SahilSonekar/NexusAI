from google import genai
from google.genai import types
from django.conf import settings
from .tools import get_order_details, get_refund_history, check_delivery_status
from .models import Conversation, Message, AgentLog


# Initialize Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)
genai_model = settings.GEMINI_MODEL



## SUPPORT SYSTEM PROMPT --> Maya's job description
SUPPORT_SYSTEM_PROMPT = """
You are Maya, a customer support agent at CoolBreeze AC.
You help customers with issues related to their AC orders.

Your responsibilities:
- Always use your tools to gather facts before responding
- Check order details when customer mentions their order
- Check refund history before making any refund decisions
- Be empathetic but honest

Your personality:
- Friendly and professional
- Patient even when customer is angry
- Clear and concise in your replies
- No emojies

Important rules:
- Always check order details first before responding
- Never approve or deny a refund yourself
- If refund decision is needed — tell customer you are checking with your team
- Never use bold text, bullet points or any markdown formatting. Plain text only.
- Keep replies concise and conversational. Maximum 3-4 sentences. No long paragraphs.
"""


## SUPPORT TOOLS --> Tool schemas, that ai agents will use 


# Google's google-genai
SUPPORT_TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_order_details",
                description="Fetch complete order details including status, carrier, tracking number and days since order was placed.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "order_id": types.Schema(type="INTEGER", description="The order ID to look up"),
                    },
                    required=["order_id"],
                ),
            ),
            types.FunctionDeclaration(
                name="get_refund_history",
                description="Get complete refund history for a user.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "user_id": types.Schema(type="INTEGER", description="The user ID to check refund history for"),
                    },
                    required=["user_id"],
                ),
            ),
            types.FunctionDeclaration(
                name="check_delivery_status",
                description="Check current delivery status using tracking number and carrier.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "tracking_number": types.Schema(type="STRING", description="The shipment tracking number"),
                        "carrier": types.Schema(type="STRING", description="The carrier name"),
                    },
                    required=["tracking_number", "carrier"],
                ),
            ),
        ]
    )
]

# SUPPORT_TOOLS = [get_order_details, get_refund_history, check_delivery_status]


# SUPPORT_TOOLS = [
#     {
#         "name": "get_order_details",
#         "description": "Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "order_id": {
#                     "type": "integer",
#                     "description": "The order ID to look up"
#                 }
#             },
#             "required": ["order_id"]
#         }
#     },

#     {
#         "name": "get_refund_history",
#         "description": "Get complete refund history for a user. Use this before making any refund related decisions.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "user_id": {
#                     "type": "integer",
#                     "description": "The user ID to check refund history for"
#                 }
#             },
#             "required": ["user_id"]
#         }
#     },

#     {
#         "name": "check_delivery_status",
#         "description": "Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "tracking_number": {
#                     "type": "string",
#                     "description": "The shipment tracking number"
#                 },
#                 "carrier": {
#                     "type": "string",
#                     "description": "The carrier name for example BlueDart or Delhivery"
#                 }
#             },
#             "required": ["tracking_number", "carrier"]
#         }
#     },
# ]


## execute_tool() --> bridge between genai and python functions(tools)
def execute_tool(tool_name, tool_input):
    if tool_name == "get_order_details":
        return get_order_details(tool_input["order_id"])
    
    if tool_name == "get_refund_history":
        return get_refund_history(tool_input["user_id"])
    
    if tool_name == "check_delivery_status":
        return check_delivery_status(tool_input["tracking_number"], tool_input["carrier"])

    raise ValueError(f"Unknown tool: {tool_name}")


## Agent Loop --> while loop that loop untill the task is done 

def run_support_agent(user_message, conversation_id, order_id, user_id):
    conv = Conversation.objects.get(id=conversation_id)

    # Build conversation history
    conversation_messages = []

    for msg in conv.messages.order_by("created_at"):
        role = "model" if msg.role == "agent" else "user"

        conversation_messages.append({
            "role": role,
            "parts": [
                {
                    "text": msg.content
                }
            ]
        })

    while True:

        response = client.models.generate_content(
            model=genai_model,
            contents=conversation_messages,
            config=types.GenerateContentConfig(
                system_instruction=(
                    SUPPORT_SYSTEM_PROMPT
                    + f"\n\nContext: This conversation is about Order #{order_id}, User #{user_id}"
                ),
                max_output_tokens=1024,
                tools=SUPPORT_TOOLS,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

        candidate = response.candidates[0]

        print("=" * 60)
        print("Finish Reason:", candidate.finish_reason)
        print(candidate.content)
        print("=" * 60)

        # Extract function calls
        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if hasattr(part, "function_call") and part.function_call
        ]

        # If Gemini returned text, we're done
        if not function_calls:

            final_reply = "".join(
                part.text
                for part in candidate.content.parts
                if hasattr(part, "text") and part.text
            ).strip()

            # Save assistant reply
            Message.objects.create(
                conversation=conv,
                role="agent",
                content=final_reply
            )

            return final_reply

        # Save Gemini's function call turn
        conversation_messages.append({
            "role": "model",
            "parts": candidate.content.parts
        })

        tool_response_parts = []

        for call in function_calls:

            print(f"\nCalling Tool -> {call.name}")
            print("Arguments ->", call.args)

            AgentLog.objects.create(
                conversation=conv,
                event_type="tool_call",
                message=f"{call.name}: {dict(call.args)}"
            )

            try:
                result = execute_tool(call.name, call.args)

                print("Tool Result ->", result)

                AgentLog.objects.create(
                    conversation=conv,
                    event_type="tool_result",
                    message=str(result)
                )

            except Exception as e:

                result = {
                    "error": str(e)
                }

                print("Tool Error ->", e)

                AgentLog.objects.create(
                    conversation=conv,
                    event_type="tool_error",
                    message=str(e)
                )

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={
                        "result": result
                    }
                )
            )

        # Send tool results back to Gemini
        conversation_messages.append({
            "role": "user",
            "parts": tool_response_parts
        })