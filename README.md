![](./chatbotgrants.png)

An intelligent chat system for grant identification and evaluation, designed to help sales representatives and customers find and assess funding opportunities.

## 🎯 Main Objective

Develop an intelligent chat system that allows sales representatives and clients to:
- Identify available grants
- Evaluate eligibility for specific projects
- Determine the suitability of grants
- Maximize possible financing returns
- Interact naturally with queries about grants

## 🏗️ Architecture

The system consists of the following main components:

### Frontend
- Interactive chat interface
- Developed in React with Material Tailwind
- Responsive design
- Authentication system
- Markdown rendering for rich responses

### Backend
- FastAPI containerized services
- Integration with Fandit grants API
- LangGraph state machine for conversation flow
- ETL system for data management
- Intermediate database for efficient filtering

### AWS Services
- **Bedrock**: AI engine for natural language processing
- **DynamoDB**: High-speed database for chat history
- **Aurora**: MySQL database for grant information
- **EC2**: Instances for service deployment

## ⚡ Key Features

1. **Intelligent Chat Interface**
   - Natural language interaction
   - Contextualized responses
   - Automatic eligibility assessment
   - Conversation history

2. **Data Management**
   - Integration with Fandit API
   - Intermediate database for efficient filtering
   - Automatic information updates via ETL
   - TTL-based expiration for conversation data

3. **Grant Analysis**
   - Filtering by region, company type, and budget
   - Detailed grant information
   - Eligibility criteria matching
   - Grant comparison

4. **Session Management**
   - Concurrent user sessions
   - Conversation persistence
   - Automatic cleanup of inactive sessions
   - Chat history retrieval

## 🚀 Technical Requirements

### Functional
- User authentication
- Natural language interaction
- Advanced filtering system
- Intermediate database
- Query processing
- Conversation management

### Non-Functional
- High availability
- Optimized performance
- Responsive design
- Data security
- Scalability

## 💻 Technologies

- **Frontend**: React, Material Tailwind, Markdoc
- **Backend**: Python, FastAPI, LangGraph
- **AI**: AWS Bedrock
- **Databases**: Aurora MySQL, DynamoDB
- **ETL**: Custom Python pipeline
- **Authentication**: Context-based with JWT
- **Containers**: Docker
- **Deployment**: Docker Compose

## 🛠️ Installation and Development

### Prerequisites
- AWS Account
- Docker and Docker Compose
- Node.js and npm
- Python 3.9+
- Git

### Environment Configuration
1. Clone the repository
   ```bash
   git clone https://github.com/AI-School-F5-P3/ChatbotGrants.git
   cd ChatbotGrants
   ```

2. Configure environment variables
   ```bash
   # In backend directory
   cp .env.example .env
   # Edit .env with your credentials

   # In etl_fandit directory
   cp .env.example .env
   # Edit .env with your Fandit API credentials
   ```

3. Start the services
   ```bash
   docker-compose up -d
   ```

### Project Structure
```
ChatbotGrants/
├── README.md                   # This documentation
├── docker-compose.yml          # Main Docker composition file
├── requirements.txt            # Root level dependencies
│
├── backend/                    # Backend Python code
│   ├── aws_connect.py          # AWS services connection module
│   ├── Dockerfile              # Backend container definition
│   ├── dynamodb.py             # DynamoDB integration for chat history
│   ├── grants_bot.py           # Core chatbot logic using LangGraph
│   ├── main.py                 # FastAPI application with endpoints
│   ├── requirements.txt        # Backend dependencies
│   └── tools_aurora.py         # Database operations for grants
│
├── frontend/                   # React application
│   ├── Dockerfile              # Frontend container definition
│   ├── package.json            # Frontend dependencies
│   ├── public/                 # Static assets
│   │   └── img/                # Image assets
│   └── src/                    # Source code
│       ├── components/         # UI components
│       ├── context/            # React contexts
│       ├── pages/              # Application pages
│       ├── services/           # API services
│       └── assets/             # Styles and images
│
└── etl_fandit/                 # ETL system for Fandit API
    ├── clase_apifandit.py      # Fandit API client
    ├── db_setup.py             # Database initialization
    ├── etl_fandit.py           # Main ETL process implementation
    ├── Dockerfile              # ETL container definition
    ├── requirements.txt        # ETL dependencies
    ├── README.md               # ETL documentation
    └── tests/                  # ETL test directory
```

## 📝 API and Resources

### Fandit API
- Endpoint: `https://ayming.api.fandit.es/api/v2`
- Update frequency: Daily
- Grant filters supported:
  - is_open
  - start_date
  - end_date
  - provinces
  - communities
  - action_items
  - activities
  - region_types

### Backend API Endpoints
- `/start_session`: Initialize a chat session
- `/chat`: Process messages
- `/end_session/{user_id}`: End a user session
- `/save_chat`: Save conversation to DynamoDB
- `/get_chat_messages`: Get messages for a conversation
- `/get_user_conversations/{user_id}`: List user conversations

## 🔄 Workflow

1. **User Input**
   - Natural language query
   - Basic information collection
   - Grant selection

2. **Processing**
   - Query analysis
   - Database search
   - Eligibility evaluation
   - LangGraph state transitions

3. **Response**
   - Relevant grants
   - Suitability analysis
   - Recommendations
   - Rich text formatting

## 📊 Monitoring and Maintenance

- System logs
  - Backend logs
  - ETL process logs
  - DynamoDB TTL enforcement
- API quota control
- Database backups
- Inactive session cleanup

## 👥 Team and Support

- Frontend Development
- Backend Development
- DevOps
- Business Team

## 📫 Contact and Help

For support and inquiries:
- Create an issue in the repository
- Contact the development team
- Consult internal documentation

## 📜 License

This is a public educational project.