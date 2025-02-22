from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import uuid
from grants_bot import GrantsBot, State
from concurrent.futures import ThreadPoolExecutor
import asyncio
from threading import Lock
import queue
from datetime import datetime, timedelta
from typing import List, Dict
from dynamodb import insert_chat_messages, get_chat_history, get_conversations, table
from boto3.dynamodb.conditions import Key # Importamos `Key` para las consultas

app = FastAPI(root_path="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    user_id: str
    message: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    message: str

class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.state = State(
            messages=[],
            user_info={},
            userid=user_id,
            sessionid=self.session_id,
            selected_grant=None,
            grant_details=None,
            info_complete=False,
            find_grants=False,
            discuss_grant=False
        )
        self.bot = GrantsBot()
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.last_activity = datetime.now()
        self.is_active = True
        self.lock = Lock()

    def process_messages(self):
        """Process messages in the queue"""
        while self.is_active:
            try:
                message = self.message_queue.get(timeout=1)  # 1 second timeout
                with self.lock:
                    if message is None:  # Shutdown signal
                        break
                    
                    # Update last activity
                    self.last_activity = datetime.now()
                    
                    # Add user message to state if not empty
                    if message:
                        self.state["messages"].append({"role": "user", "content": message})

                                

                    if not self.state.get("info_complete"):
                        self.state = self.bot.get_initial_info(self.state)
                        response = self.get_bot_response(self.state)
                        
                        # Add this check - if info just completed, immediately process find_grants
                        if self.state.get("info_complete"):
                            self.state = self.bot.find_best_grants(self.state)
                            response = self.get_bot_response(self.state)
                        
                        self.response_queue.put((response, False))
                        continue
                        
                    # elif self.state.get("find_grants"):
                    #     self.state = self.bot.find_best_grants(self.state)
                    #     response = self.get_bot_response(self.state)
                    #     session_ended = False
                        
                    #     # Only proceed to next message if state changed
                    #     if self.state.get("find_grants"):
                    #         self.response_queue.put((response, session_ended))
                    #         continue

                    elif self.state.get("find_grants"):
                        self.state = self.bot.find_best_grants(self.state)
                        response = self.get_bot_response(self.state)
                        
                        # Add this check - if find_grants just completed and discuss_grant is set
                        if not self.state.get("find_grants") and self.state.get("discuss_grant"):
                            self.state = self.bot.review_grant(self.state)
                            response = self.get_bot_response(self.state)
                        
                        self.response_queue.put((response, False))
                        continue
                        
                    elif self.state.get("discuss_grant"):
                        self.state = self.bot.review_grant(self.state)
                        response = self.get_bot_response(self.state)
                        session_ended = False
                        
                        # Only proceed to next message if state changed
                        if self.state.get("discuss_grant"):
                            self.response_queue.put((response, session_ended))
                            continue
                    
                    # Check for session end condition (same as test.py)
                    if self.state.get("info_complete") and not self.state.get("find_grants") and not self.state.get("discuss_grant"):
                        response = "Conversation ended. Thank you for using the Grants Bot!"
                        session_ended = True
                    
                    # Put response in queue for the API endpoint to retrieve
                    self.response_queue.put((response, session_ended))

            except queue.Empty:
                continue  # Timeout occurred, continue the loop
            except Exception as e:
                # Handle any errors and put them in response queue
                self.response_queue.put((f"An error occurred: {str(e)}", True))
                break

    def get_bot_response(self, state: Dict) -> str:
        """Extract the last bot message from the state"""
        for message in reversed(state["messages"]):
            if message["role"] == "assistant":
                return message["content"]
        return ""

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.executor = ThreadPoolExecutor(max_workers=100)  # Adjust max_workers as needed
        self.lock = Lock()

    def create_session(self, user_id: str) -> UserSession:
        with self.lock:
            if user_id in self.sessions:
                return self.sessions[user_id]
            
            session = UserSession(user_id)
            self.sessions[user_id] = session
            # Start processing thread for this session
            self.executor.submit(session.process_messages)
            return session

    def get_session(self, user_id: str) -> Optional[UserSession]:
        return self.sessions.get(user_id)

   
    def end_session(self, user_id: str) -> bool:                       # IMPROVED
        """End a user's session with graceful handling"""
        with self.lock:
            if user_id in self.sessions:
                try:
                    session = self.sessions[user_id]
                    session.is_active = False
                    session.message_queue.put(None)  # Shutdown signal
                    del self.sessions[user_id]
                    return True
                except Exception as e:
                    print(f"Error ending session for {user_id}: {e}")
                    # Still remove the session even if there's an error
                    self.sessions.pop(user_id, None)
                    return True
            return False  # Session didn't exist

    def cleanup_inactive_sessions(self):
        """Remove inactive sessions"""
        with self.lock:
            current_time = datetime.now()
            inactive_users = [
                user_id for user_id, session in self.sessions.items()
                if current_time - session.last_activity > timedelta(minutes=30)
            ]
            for user_id in inactive_users:
                self.end_session(user_id)

class ChatMessage(BaseModel):
    userId: str
    timestamp: str
    role: str
    message_content: str
    
class ChatHistoryRequest(BaseModel):
    messages: List[ChatMessage]
    
# Initialize session manager
session_manager = SessionManager()

@app.post("/start_session")                                                 #Improved
async def start_session(user_data: UserMessage) -> SessionResponse:
    """Start a new session with improved validation"""
    try:
        # End any existing session first
        session_manager.end_session(user_data.user_id)
        
        # Create new session
        session = session_manager.create_session(user_data.user_id)
        session.message_queue.put("")  # Trigger initial message
        
        try:
            response, _ = session.response_queue.get(timeout=30)
        except queue.Empty:
            raise HTTPException(status_code=504, detail="Session initialization timeout")
            
        return SessionResponse(
            session_id=session.session_id,
            message=response
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in start_session: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not start session")

@app.post("/chat")                                # IMPROVED
async def chat(user_data: UserMessage) -> Dict:
    """Handle chat messages with improved error handling"""
    try:
        session = session_manager.get_session(user_data.user_id)
        if not session:
            # Instead of 404, create a new session
            session = session_manager.create_session(user_data.user_id)
            print(f"Created new session for existing chat: {user_data.user_id}")
        
        # Add message to queue with timeout
        try:
            session.message_queue.put(user_data.message, timeout=1)
        except queue.Full:
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
            
        # Wait for response with timeout
        try:
            response, session_ended = session.response_queue.get(timeout=30)
        except queue.Empty:
            raise HTTPException(status_code=504, detail="Response timeout")
            
        if session_ended:
            session_manager.end_session(user_data.user_id)
        
        return {
            "message": response,
            "session_ended": session_ended
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return {
            "message": "An error occurred, please try again",
            "session_ended": True
        }

@app.get("/session_state/{user_id}")
async def get_session_state(user_id: str):
    """Get current session state for debugging"""
    session = session_manager.get_session(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    with session.lock:
        return {
            "info_complete": session.state["info_complete"],
            "find_grants": session.state["find_grants"],
            "discuss_grant": session.state["discuss_grant"],
            "user_info": session.state["user_info"]
        }

@app.delete("/end_session/{user_id}")
async def end_session(user_id: str):
    """End a user's session with graceful error handling"""
    try:
        was_ended = session_manager.end_session(user_id)
        return {
            "message": "Session ended successfully" if was_ended else "No active session found",
            "status": "success"
        }
    except Exception as e:
        print(f"Error in end_session endpoint for {user_id}: {e}")
        # Return 200 even if there was an error, since the session is effectively ended
        return {
            "message": "Session cleanup completed",
            "status": "success"
        }

# Background task to clean up inactive sessions
@app.on_event("startup")
async def start_cleanup_task():
    async def cleanup_loop():
        while True:
            try:
                # Get current time once per cleanup cycle
                current_time = datetime.now()
                
                # Create list of sessions to remove to avoid dict size changing during iteration
                to_remove = []
                
                # Only acquire lock briefly to check sessions
                with session_manager.lock:
                    for user_id, session in session_manager.sessions.items():
                        if current_time - session.last_activity > timedelta(minutes=30):
                            to_remove.append(user_id)
                
                # Remove sessions outside the lock
                for user_id in to_remove:
                    try:
                        session_manager.end_session(user_id)
                    except Exception as e:
                        print(f"Error removing session {user_id}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Cleanup error: {e}")
            
            # Sleep for 5 minutes between cleanup cycles
            await asyncio.sleep(300)
    
    # Start the cleanup loop without waiting for it
    asyncio.create_task(cleanup_loop())
    
@app.post("/save_chat")
async def insert_messages(chat_data: ChatHistoryRequest):
    """
    Endpoint para insertar mensajes en DynamoDB.
    """
    if not chat_data.messages:
        raise HTTPException(status_code=400, detail="Faltan datos en la petición")

    try:
        user_id = chat_data.messages[0].userId  # Tomamos el userId del primer mensaje
        conversation_id = str(uuid.uuid4())  # Generamos un ID único para la conversación

        # Convertimos los datos al formato esperado por `insert_chat_messages`
        messages = [
            {
                "sender": msg.role,
                "text": msg.message_content,
                "timestamp": msg.timestamp
            }
            for msg in chat_data.messages
        ]

        # Insertamos los mensajes en DynamoDB
        insert_chat_messages(user_id, conversation_id, messages)

        return {"message": "Mensajes insertados exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando los mensajes: {str(e)}")

@app.get("/get_chat_messages")
async def get_chat_messages(user_id: str = Query(...), conversation_id: str = Query(...)):
    """
    Obtiene los mensajes de una conversación específica de un usuario.
    """
    try:
        messages = get_chat_history(user_id)
        # Filtrar mensajes por `conversation_id`
        filtered_messages = [msg for msg in messages if msg["conversationId"] == conversation_id]

        if not filtered_messages:
            raise HTTPException(status_code=404, detail="No se encontraron mensajes para esta conversación")

        # Ordenamos los mensajes por 'order'
        sorted_messages = sorted(filtered_messages, key=lambda x: x["order"])

        return {"messages": sorted_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mensajes: {str(e)}")

@app.get("/get_user_conversations/{user_id}")
async def get_user_conversations(user_id: str):
    """
    Obtiene la lista de conversaciones guardadas para un usuario en DynamoDB.
    """
    try:
        messages = get_conversations(user_id)

        # Ordenamos los mensajes por 'order'
        sorted_messages = sorted(messages, key=lambda x: x["conversation_date"], reverse=True)

        return {"messages": sorted_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mensajes: {str(e)}")
