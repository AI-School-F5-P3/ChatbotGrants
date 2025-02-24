# grants_bot.py
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, START, END
from tools_aurora import  find_optimal_grants, get_grant_detail
from aws_connect import get_bedrock_response

class State(TypedDict):
    messages: List[Dict]
    user_info: Dict[str, str]
    userid: Optional[str]
    sessionid: Optional[str]
    selected_grants: Optional[Dict]
    grant_details: Optional[Dict]
    info_complete: bool
    find_grants:bool
    discuss_grant: bool

class GrantsBot:
    def __init__(self):
        self.FIELDS = [
            ("Comunidad Autónoma", "Por favor, ¿podrías decirme en qué Comunidad Autónoma está el cliente ?"),
            ("Tipo de Empresa", "¿Cuál es el tipo de empresa? (Autónomo, PYME, Gran Empresa)"),
            ("Presupuesto del Proyecto", "¿Cuál es el presupuesto aproximado del proyecto?"),
        ]
        self.greeting_shown = False

        self.graph_builder = StateGraph(State)
        self.graph_builder.add_node("get_initial_info", self.get_initial_info)
        self.graph_builder.add_node("find_best_grants", self.find_best_grants)
        self.graph_builder.add_node("review_grant", self.review_grant)
        self.graph_builder.add_node("end", lambda state: state)

        self.graph_builder.add_edge(START, "get_initial_info")
        
        self.graph_builder.add_conditional_edges(
            "get_initial_info",
            self.should_find_grants,
            {True: "find_best_grants", False: END}
        )

        self.graph_builder.add_conditional_edges(
            "find_best_grants",
            self.should_review_grant,
            {True: "review_grant", False: END}
        )


        self.graph_builder.add_conditional_edges(
            "review_grant",
            lambda state: state.get("find_grants", False) and not state.get("discuss_grant", True),
            {True: "find_best_grants", False: "review_grant"}
        )

            

        self.graph = self.graph_builder.compile()


    def is_info_complete(self, state: State) -> bool:
        """Checks if all required information has been collected."""
        return state.get("info_complete", False)

    def should_find_grants(self, state: State) -> bool:
        """Checks if the user would like to discuss the proposed grants"""
        return state.get("find_grants", False)
    
    def should_review_grant(self, state: State) -> bool:
        """Checks if the user would like to review the selected grant in detail"""
        return state.get("discuss_grant", False)
    



    def get_initial_info(self, state: State) -> State:
        """Collects initial information from the user."""
        messages = state.get("messages", [])
        user_info = state.get("user_info", {})
        
        if not messages:
            
            messages.extend([
                {"role": "assistant", "content": f"""
                    ¡Hola! 👋 Soy tu asistente virtual especializado. Estoy aquí para ayudarte a encontrar las mejores subvenciones para tu cliente.

                    Para empezar, necesito algunos datos clave. 

                    {self.FIELDS[0][1]}"""}])


            return {"messages": messages, "user_info": user_info, "info_complete": False}

        last_message = messages[-1]
        if last_message["role"] == "user":
            current_field_idx = len(user_info)
            if current_field_idx < len(self.FIELDS):
                field_name = self.FIELDS[current_field_idx][0]
                user_info[field_name] = last_message["content"].strip()
                
                if current_field_idx + 1 < len(self.FIELDS):
                    next_field, next_prompt = self.FIELDS[current_field_idx + 1]
                    messages.append({"role": "assistant", "content": next_prompt})
                    return {"messages": messages, "user_info": user_info, "info_complete": False}
                else:
                    messages.append({"role": "assistant", "content": "Gracias por proporcionar toda la información. Ahora buscaré las mejores subvenciones para ti."})
                    return {"messages": messages, "user_info": user_info, "info_complete": True, "find_grants":True}
            
        return {"messages": messages, "user_info": user_info, "info_complete": False}

    

    def find_best_grants(self, state: State) -> State:
        """Handles grant finding and discussion based on state messages."""
        messages = state["messages"]
        user_info = state.get("user_info", {})
        selected_grants = state.get("selected_grants", None)
        
        # Only do initial grant presentation if no grant selected yet
        if not selected_grants:
            best_grants = find_optimal_grants(user_info)
            if best_grants:
                state["selected_grants"] = best_grants
                prompt = f"""
                Use the following grants as context:
                {best_grants}

                Your response in 1000 words aproximately, All your response in Spanish, do not mention the response format. Do not make a preamble

                Present all grants in the context and for each include: title, full slug without modification, scope, and brief summary.
                Ask if they would like to know more details about a particular grant.
                Your answer in Markdown format.
                """
                
                response = get_bedrock_response(prompt)
                messages.append({"role": "assistant", "content": response["content"][0]["text"]})
                return {**state, "messages": messages}


        last_message = messages[-1]
        if last_message["role"] == "user":
            if "revisar" in last_message["content"].lower():
                state["find_grants"]= False
                state["discuss_grant"]= True
                return state
                
            dialogue_prompt = f"""
            The user has asked: {last_message['content']}
            Context: {selected_grants}
            
            Please respond in Spanish about this specific question. If the user asks anything not related to the grant, politely conduct the conversation back to the grant.
            Be concise and your answer in Markdown format.

            """
            response = get_bedrock_response(dialogue_prompt)
            response_content = response["content"][0]["text"]
    
            # Update state messages
            state["messages"] = messages + [{"role": "assistant", "content": response_content}]
    
            # Return updated state
            return state
            
      
    

    def review_grant(self, state: State) -> State:
        """Reviews a specific grant in detail based on the slug key."""
        messages = state["messages"]
        
        # First interaction - just show greeting
        if not self.greeting_shown:
            self.greeting_shown = True
            messages.append({"role": "assistant", "content": "Por favor, introduce el slug de la subvención que quieres revisar en detalle:"})
            state["messages"] = messages
            return state
            
        
        # Only proceed if greeting has been shown
        if self.greeting_shown:
            grant_details = state.get("grant_details", None)
            last_message = messages[-1]
            
            if not grant_details:
                # Process BDNS input
                slug = last_message["content"].strip()
                detailed_grant = get_grant_detail(slug)
                
                if detailed_grant:
                    state["grant_details"] = detailed_grant
                    prompt = f"""

                    Please analyze this grant and present the information in a structured way in Spanish and do not make a preamble:

                    Complete grant details:
                    {detailed_grant}

                    Por favor, estructura la respuesta con:
                    1. Resumen ejecutivo
                    2. Requisitos clave
                    3. Proceso de solicitud
                    4. Plazos importantes
                    5. Documentación necesaria

                    Termina preguntando si tiene alguna otra consulta
                    Your answer in Markdown format
                    """
                    
                    response = get_bedrock_response(prompt)
                    response_content = response["content"][0]["text"]
                    messages.append({"role": "assistant", "content": response_content})
                    return {**state, "messages": messages}
                    
                messages.append({
                    "role": "assistant",
                    "content": "No he encontrado una subvención con ese slug. ¿Quieres intentar con otro código?"
                })
                return {**state, "messages": messages}

            # Handle commands and dialogue after grant details are obtained
            
            if "volver" in last_message["content"].lower():
                self.greeting_shown = False  # Reset greeting for potential future use
                state["find_grants"] = True
                state["discuss_grant"] = False
                state["grant_details"] = {}
                messages.append({
                    "role": "assistant",
                    "content": "¡Gracias!. Volvemos a analizar las subvenciones encontradas."
                })
                return {**state, "messages": messages}
            
            # Handle regular dialogue about the grant. For follow-up questions, add more context
            

            dialogue_prompt = f"""
            The user has asked: {last_message['content']}
            Context: {grant_details}
            
            Please respond in Spanish about this specific question. If the user asks anything not related to the grant, politely conduct the conversation back to the grant details.
            Your response in markdown format.
            """
            response = get_bedrock_response(dialogue_prompt)
            response_content = response["content"][0]["text"]
            messages.append({"role": "assistant", "content": response_content})
            return {**state, "messages": messages}
        
        return state
        
