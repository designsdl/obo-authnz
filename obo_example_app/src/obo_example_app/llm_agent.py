import os
import google.generativeai as genai
from .context import get_current_user_id
from .database import get_db, AsyncSessionLocal # We need a way to get a session
from .notes_service import NotesService

# Configure Gemini
# NOTE: This requires GEMINI_API_KEY env var
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- OBO Tools ---

async def create_note_tool(content: str):
    """Creates a new note for the current user."""
    user_id = get_current_user_id()
    if not user_id:
        print("[Tool:create_note_tool] BLOCKED: No user context found.")
        return "Error: No user context found."
    
    print(f"[Tool:create_note_tool] Executing for Context User: '{user_id}'")
    # In a real app, use dependency injection. Here we create a fresh session.
    async with AsyncSessionLocal() as db:
        service = NotesService(db, user_id)
        note = await service.create_note(content)
        return f"Note created with ID: {note.id}"

async def list_notes_tool():
    """Lists all notes belonging to the current user."""
    user_id = get_current_user_id()
    if not user_id:
        print("[Tool:list_notes_tool] BLOCKED: No user context found.")
        return "Error: No user context found."
        
    print(f"[Tool:list_notes_tool] Executing for Context User: '{user_id}'")
    async with AsyncSessionLocal() as db:
        service = NotesService(db, user_id)
        notes = await service.get_my_notes()
        if not notes:
            return "You have no notes."
        return "\n".join([f"- [ID {n.id}]: {n.content}" for n in notes])

# --- Agent Definition ---

tools = [create_note_tool, list_notes_tool]
model = genai.GenerativeModel('gemini-3-flash-preview', tools=tools)

async def chat_with_agent(message: str) -> str:
    """
    Process a user message using Gemini with OBO tools.
    Manually handles function calling to ensure async tools are awaited.
    """
    chat = model.start_chat(enable_automatic_function_calling=False)
    
    try:
        # 1. Send initial message
        response = await chat.send_message_async(message)
        
        # 2. Loop to handle tool calls (multi-step capability)
        # We limit max turns to prevent infinite loops
        for _ in range(5):
            part = response.candidates[0].content.parts[0]
            
            # If text, we are done
            if part.text:
                return part.text
            
            # If function call, execute it
            if part.function_call:
                fc = part.function_call
                tool_result = ""
                
                print(f"Executing Tool: {fc.name}")
                
                if fc.name == "create_note_tool":
                    # Extract args safely
                    content = fc.args.get("content", "")
                    tool_result = await create_note_tool(content)
                
                elif fc.name == "list_notes_tool":
                    tool_result = await list_notes_tool()
                
                else:
                    tool_result = f"Error: Unknown tool {fc.name}"

                # 3. Send result back to model
                # We must use the specific FunctionResponse structure
                from google.ai.generativelanguage import Part, FunctionResponse
                
                response_part = Part(
                    function_response=FunctionResponse(
                        name=fc.name,
                        response={"result": tool_result}
                    )
                )
                
                response = await chat.send_message_async([response_part])
        
        return "Error: Too many tool steps."

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Agent Error: {str(e)}"
