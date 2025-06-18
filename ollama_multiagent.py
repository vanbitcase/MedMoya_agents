"""
Multi-agent system using Ollama and Moya framework.
Demonstrates the use of multiple specialized agents for different tasks.
"""

import sys
import json
import time
import threading
import re
from datetime import datetime
from winotify import Notification, audio
from moya.agents.base_agent import AgentConfig
from moya.agents.ollama_agent import OllamaAgent
from moya.classifiers.llm_classifier import LLMClassifier
from moya.orchestrators.multi_agent_orchestrator import MultiAgentOrchestrator
from moya.registry.agent_registry import AgentRegistry
from moya.tools.ephemeral_memory import EphemeralMemory
from moya.memory.in_memory_repository import InMemoryRepository
from moya.tools.tool_registry import ToolRegistry
import http.client
from urllib.parse import quote


def setup_memory_components():
    """Set up memory components for the agents."""
    tool_registry = ToolRegistry()
    EphemeralMemory.configure_memory_tools(tool_registry)
    return tool_registry

def web(product):
    conn = http.client.HTTPSConnection("real-time-amazon-data.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "a025dae6c5msh67115b295390413p1a6a28jsn188a027e4f40",
        'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
    }

    # Encode the product string for safe URL usage
    search_term = quote(product)

    url = f"/search?query={search_term}&page=1&country=US&sort_by=RELEVANCE&product_condition=ALL&is_prime=True&deals_and_discounts=NONE"

    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read()

    # Convert bytes to JSON
    json_data = json.loads(data.decode("utf-8"))

    # Get products list
    products = json_data.get("data", {}).get("products", [])

    # Extract required fields
    result = []
    for item in products:
        product_info = {
            "product_title": item.get("product_title"),
            "product_price": item.get("product_price"),
            "product_url": item.get("product_url"),
            "sales_volume": item.get("sales_volume")
        }
        result.append(product_info)

    return result

def create_medvisor_agent(tool_registry):
    
    agent_config = AgentConfig(
        agent_name="Medvisor",
        agent_type="ChatAgent",
        description="Give Temporary advice for the medications and possible ways to get relief at that moment of time.",
        system_prompt="""You are medical advisor who give advice based on the patients input. First you give the possible home remidies then the relates advice also tells about the product domain for related problem like skinny issue so eat protein.""",
        tool_registry=tool_registry,
        llm_config={
            'model_name': "gemma3:4b",
            'temperature': 0.7,
            'base_url': "http://localhost:11434",
            'context_window': 4096
        }
    )
    return OllamaAgent(agent_config)


def create_product_agent(tool_registry):
   
    agent_config = AgentConfig(
        agent_name="Product agent",
        agent_type="AmazonProductAgent",
        description="based on the medadvisor bot you will going to present the Amazon product on healthcare.",
        system_prompt="""You are the pharma guy who brings the medicine from amazon , their is an informative product data will be provided when the prompt is given. 
        You have to give suggestion with the product based in health care.""",
        tool_registry=tool_registry,
        llm_config={
            'model_name': "gemma3:4b",
            'temperature': 0.8,
            'base_url': "http://localhost:11434",
            'context_window': 4096
        }
    )
    return OllamaAgent(agent_config)


def create_reminder_agent(tool_registry):
    """Create a reminder-focused Ollama agent."""
    agent_config = AgentConfig(
        agent_name="Reminder agent",
        agent_type="personalAgent",
        description="An agent which set the reminder for the patient",
        system_prompt="""You are an agent who set the reminder based on the input prompt you give a structure format serating the message purpose and remind_at in just three variable 
        like this json format:
        {
          "message": "",
        "purpose": "",
        "reminder_at": ""
        } note give json format only single time"""  ,
        tool_registry=tool_registry,
        llm_config={
            'model_name': "gemma3:4b",
            'temperature': 0.6,
            'base_url': "http://localhost:11434",
            'context_window': 4096
        }
    )
    return OllamaAgent(agent_config)
"""
def create_product_name(tool_registry):
    
    agent_config = AgentConfig(
        agent_name="Extract Product name",
        agent_type="Product_name",
        description="Task is to extract the needed product",
        system_prompt= You are an agent how extract the name of the product from the prompt,
        tool_registry=tool_registry,
        llm_config={
            'model_name': "gemma3:4b",
            'temperature': 0.3,
            'base_url': "http://localhost:11434",
            'context_window': 4096
        }
    )
    return OllamaAgent(agent_config)
"""


def create_classifier_agent(tool_registry):
    """Create a classifier agent for task detection."""
    agent_config = AgentConfig(
        agent_name="classifier",
        agent_type="AgentClassifier",
        description="Task classifier for routing messages to appropriate agents",
        system_prompt="""You are a classifier. Your job is to determine the best agent based on the user's message:
        1. If the message is about disease or any taking information regarding disease.'
        2. If the message is about the healthcare product or any pharma related product you exatract the product name and give it to the product agent'
        3. If the message is about setting an reminder on a time for a given purpose.'
        4. If user ask for health related product give on the product name  
        5. For any other topics, return 'medvisor' as default
        
        Analyze both the topic and intent of the message.
        Return only the agent name as specified above.""",
        tool_registry=tool_registry,
        llm_config={
            'model_name': "gemma3:4b",
            'temperature': 0.3,
            'base_url': "http://localhost:11434",
            'context_window': 4096
        }
    )
    return OllamaAgent(agent_config)


def setup_orchestrator():
    """Set up the multi-agent orchestrator with all components."""
    # Set up shared components
    tool_registry = setup_memory_components()

    # Create agents
    medvisor_agent = create_medvisor_agent(tool_registry)
    product_agent = create_product_agent(tool_registry)
    reminder_agent = create_reminder_agent(tool_registry)
    classifier_agent = create_classifier_agent(tool_registry)

    # Set up agent registry
    registry = AgentRegistry()
    registry.register_agent(medvisor_agent)
    registry.register_agent(product_agent)
    registry.register_agent(reminder_agent)

    # Create and configure the classifier
    classifier = LLMClassifier(classifier_agent, default_agent="Medvisor")

    # Create the orchestrator
    orchestrator = MultiAgentOrchestrator(
        agent_registry=registry,
        classifier=classifier,
        default_agent_name="Medvisor"
    )

    return orchestrator


def format_conversation_context(messages):
    """Format conversation history for context."""
    context = "\nPrevious conversation:\n"
    for msg in messages:
        sender = "User" if msg.sender == "user" else "Assistant"
        context += f"{sender}: {msg.content}\n"
    return context


def print_conversation_history(thread):
    """Print the entire conversation history in a formatted way."""
    print("\n" + "="*50)
    print("Conversation History:")
    print("="*50)
    
    messages = thread.get_messages()
    for msg in messages:
        sender = "User" if msg.sender == "user" else "Assistant"
        print(f"\n{sender}: {msg.content}")
    
    print("\n" + "="*50)


def set_reminder(message, purpose, remind_at):
    """Set a reminder notification for the specified time."""
    def reminder_thread():
        while True:
            now = datetime.now().strftime("%H:%M")
            if now == remind_at:
                toaster = Notification(app_id="MedGen", title=message, msg=purpose, duration="short")
                toaster.set_audio(audio.LoopingAlarm, loop=True)
                toaster.show()
                break
            time.sleep(15)
    
    # Start the reminder in a background thread
    reminder_thread = threading.Thread(target=reminder_thread, daemon=True)
    reminder_thread.start()
    return reminder_thread


def process_reminder_response(response):
    """Process the reminder agent's response and set the reminder."""
    try:
        # Extract JSON from the response
        json_str = response.split('```json')[1].split('```')[0].strip()
        reminder_data = json.loads(json_str)
        
        # Convert time to 24-hour format if needed
        reminder_time = reminder_data['reminder_at']
        if 'PM' in reminder_time:
            hour = int(reminder_time.split(':')[0])
            if hour != 12:
                hour += 12
            reminder_time = f"{hour}:{reminder_time.split(':')[1].split(' ')[0]}"
        elif 'AM' in reminder_time and reminder_time.split(':')[0] == '12':
            reminder_time = f"00:{reminder_time.split(':')[1].split(' ')[0]}"
        else:
            reminder_time = reminder_time.split(' ')[0]
        
        # Set the reminder in background
        reminder_thread = set_reminder(
            message=reminder_data['message'],
            purpose=reminder_data['purpose'],
            remind_at=reminder_time
        )
        return True, reminder_thread
    except Exception as e:
        print(f"Error setting reminder: {str(e)}")
        return False, None


def extract_product_names(text):
    """Extract potential product names from text."""
    # Common product-related keywords
    product_keywords = [
        'medicine', 'medication', 'pill', 'tablet', 'capsule', 'spray', 'cream',
        'ointment', 'syrup', 'drops', 'powder', 'supplement', 'vitamin'
    ]
    
    # Look for patterns like "product name" or product name
    product_patterns = [
        r'"([^"]*?(?:' + '|'.join(product_keywords) + r')[^"]*?)"',  # "product name"
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' + '|'.join(product_keywords) + r'))',  # Product Name
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:medicine|medication|pill|tablet))'  # Generic medicine names
    ]
    
    found_products = []
    for pattern in product_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            product = match.group(1).strip()
            if product and len(product) > 3:  # Avoid very short matches
                found_products.append(product)
    
    return list(set(found_products))  # Remove duplicates

def get_amazon_results(product_name):
    """Get and format Amazon results for a product."""
    try:
        results = web(product_name)
        if not results:
            return None
        
        formatted_results = []
        for p in results[:3]:  # Get top 3 results
            formatted_results.append(
                f"Product: {p['product_title']}\n"
                f"Price: {p['product_price']}\n"
                f"Sales Volume: {p['sales_volume']}\n"
                f"URL: {p['product_url']}\n"
            )
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error searching for {product_name}: {str(e)}"

def main():
    # Set up the orchestrator and all components
    orchestrator = setup_orchestrator()
    thread_id = "multi_agent_chat"
    active_reminders = []  # Keep track of active reminder threads

    print("Welcome to the Multi-Agent Chat System! (Type 'exit' to quit)")
    print("You can ask about:")
    print("1. Healthcare and Home remedies")
    print("2. Find Product regarding the discussion")
    print("3. Set an reminder for your medicine intake.")
    print("-" * 50)

    def stream_callback(chunk):
        print(chunk, end="", flush=True)

    EphemeralMemory.store_message(thread_id=thread_id, sender="system", content=f"thread ID: {thread_id}")

    while True:
        # Get user input
        user_message = input("\nYou: ").strip()

        # Check for exit condition
        if user_message.lower() == 'exit':
            print("\nGoodbye!")
            # Get and print the conversation history
            thread = EphemeralMemory.get_thread(thread_id)
            print_conversation_history(thread)
            break

        # Get available agents
        agents = orchestrator.agent_registry.list_agents()
        if not agents:
            print("\nNo agents available!")
            continue

        # Store the user message
        EphemeralMemory.store_message(thread_id=thread_id, sender="user", content=user_message)

        # Get conversation context
        session_summary = EphemeralMemory.get_thread_summary(thread_id)
        enriched_input = f"{session_summary}\nCurrent user message: {user_message}"

        # Print Assistant prompt and get response
        print("\nAssistant: ", end="", flush=True)
        response = orchestrator.orchestrate(
            thread_id=thread_id,
            user_message=enriched_input,
            stream_callback=stream_callback
        )
        print(response)
        
        # Check if this is a reminder response and set the reminder
        if "Reminder agent" in response and "```json" in response:
            success, reminder_thread = process_reminder_response(response)
            if success:
                active_reminders.append(reminder_thread)
                print("\nReminder has been set successfully! You can continue with your next query.")
            else:
                print("\nFailed to set reminder. Please try again.")
        
        # Check for product names in the response
        if "Medvisor" in response or "Product agent" in response:
            product_names = extract_product_names(response)
            if product_names:
                print("\nFound related products on Amazon:")
                for product in product_names:
                    print(f"\nSearching for: {product}")
                    amazon_results = get_amazon_results(product)
                    if amazon_results:
                        print(amazon_results)
                    else:
                        print(f"No results found for {product}")
        
        print()  # New line after response
        EphemeralMemory.store_message(thread_id=thread_id, sender="system", content=response)


if __name__ == "__main__":
    main() 