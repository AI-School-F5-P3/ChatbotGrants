from fastapi import FastAPI, HTTPException
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
from contextlib import asynccontextmanager

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
                message = self.message_queue.get(timeout=1)
                with self.lock:
                    if message is None:
                        break
                    
                    self.last_activity = datetime.now()
                    
                    if message:
                        self.state["messages"].append({"role": "user", "content": message})

                    if not self.state.get("info_complete"):
                        self.state = self.bot.get_initial_info(self.state)
                        response = self.get_bot_response(self.state)
                        
                        if self.state.get("info_complete"):
                            self.state = self.bot.find_best_grants(self.state)
                            response = self.get_bot_response(self.state)
                        
                        self.response_queue.put((response, False))
                        continue

                    elif self.state.get("find_grants"):
                        self.state = self.bot.find_best_grants(self.state)
                        response = self.get_bot_response(self.state)
                        
                        if not self.state.get("find_grants") and self.state.get("discuss_grant"):
                            self.state = self.bot.review_grant(self.state)
                            response = self.get_bot_response(self.state)
                        
                        self.response_queue.put((response, False))
                        continue
                        
                    elif self.state.get("discuss_grant"):
                        self.state = self.bot.review_grant(self.state)
                        response = self.get_bot_response(self.state)
                        session_ended = False
                        
                        if self.state.get("discuss_grant"):
                            self.response_queue.put((response, session_ended))
                            continue
                    
                    if self.state.get("info_complete") and not self.state.get("find_grants") and not self.state.get("discuss_grant"):
                        response = "Conversation ended. Thank you for using the Grants Bot!"
                        session_ended = True
                    
                    self.response_queue.put((response, session_ended))

            except queue.Empty:
                continue
            except Exception as e:
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
        self.executor = ThreadPoolExecutor(max_workers=100)
        self.lock = Lock()

    def create_session(self, user_id: str) -> UserSession:
        with self.lock:
            if user_id in self.sessions:
                return self.sessions[user_id]
            
            session = UserSession(user_id)
            self.sessions[user_id] = session
            self.executor.submit(session.process_messages)
            return session

    def get_session(self, user_id: str) -> Optional[UserSession]:
        return self.sessions.get(user_id)

    def end_session(self, user_id: str):
        with self.lock:
            if user_id in self.sessions:
                session = self.sessions[user_id]
                session.is_active = False
                session.message_queue.put(None)
                del self.sessions[user_id]

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

session_manager = SessionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def cleanup_loop():
        while True:
            session_manager.cleanup_inactive_sessions()
            await asyncio.sleep(300)
    
    task = asyncio.create_task(cleanup_loop())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start_session")
async def start_session(user_data: UserMessage) -> SessionResponse:
    session = session_manager.create_session(user_data.user_id)
    session.message_queue.put("")
    
    response, _ = session.response_queue.get()
    return SessionResponse(
        session_id=session.session_id,
        message=response
    )

@app.post("/chat")
async def chat(user_data: UserMessage) -> Dict:
    session = session_manager.get_session(user_data.user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.message_queue.put(user_data.message)
    
    response, session_ended = session.response_queue.get()
    
    if session_ended:
        session_manager.end_session(user_data.user_id)
    
    return {
        "message": response,
        "session_ended": session_ended
    }

@app.get("/session_state/{user_id}")
async def get_session_state(user_id: str):
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
    session = session_manager.get_session(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_manager.end_session(user_id)
    return {"message": "Session ended successfully"}
