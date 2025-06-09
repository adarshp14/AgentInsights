# InsightFlow - Contextual AI Agent with RAG and LangGraph

A full-stack application showcasing a powerful, contextual AI assistant using **LangChain**, **LangGraph**, and **RAG** (Retrieval Augmented Generation), with a beautiful, interactive UI that visualizes the agent's reasoning process in real-time.

## ✨ Features

- **🧠 LangGraph Agent Orchestration**: Multi-step AI agent with visual flow representation
- **📚 RAG Implementation**: Document retrieval and context-aware responses
- **⚡ Real-time Agent Visualization**: Watch the AI think through your queries step-by-step
- **🛠️ Tool Integration**: Mock tools for weather, email, calculations, and product information
- **🎨 Beautiful UI**: Modern React interface with Tailwind CSS and smooth animations
- **🔧 Debug Mode**: Detailed observability with performance metrics and reasoning traces

## 🏗️ Architecture

### Backend (FastAPI)
- **Agent Orchestration**: LangChain + LangGraph
- **Vector Store**: FAISS with OpenAI embeddings
- **Memory**: Conversational buffer memory
- **Tools**: Extensible tool registry with mock implementations

### Frontend (React + TypeScript)
- **Chat Interface**: Real-time messaging with markdown support
- **Flow Visualizer**: Animated representation of agent processing steps
- **Settings Panel**: Model selection and debug configuration
- **State Management**: Zustand for efficient state handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional for embeddings)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional for basic demo)
cp .env.example .env
# Edit .env with your API keys

# Run the server
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🎯 Usage

1. **Start both servers** (backend on port 8000, frontend on port 5173)
2. **Open your browser** to `http://localhost:5173`
3. **Ask questions** like:
   - "What are the key tax rules for freelancers in Canada?"
   - "How do I calculate quarterly tax payments?"
   - "What business expenses can I deduct?"
4. **Watch the agent flow** in the right panel as it processes your query
5. **Explore settings** to toggle debug mode and see detailed metrics

## 🧪 Agent Flow

The agent processes queries through these steps:

1. **📝 Input Processor**: Parses and cleans the user query
2. **🔍 Retriever**: Searches vector store for relevant documents
3. **🧠 Analyzer**: Analyzes context and formulates reasoning
4. **💬 Responder**: Generates contextual response

Each step is visualized in real-time with status indicators, timing, and debug information.

## 🛠️ Mock Tools

The application includes several mock tools to demonstrate tool calling:

- **🌤️ Weather Tool**: Get weather for any location
- **📧 Email Tool**: Send mock emails
- **📦 Product Tool**: Retrieve product information
- **🧮 Calculator Tool**: Perform mathematical calculations

## 🎨 UI Components

- **Chat Interface**: Clean, WhatsApp-style messaging
- **Agent Flow Visualizer**: Real-time step tracking with animations
- **Settings Modal**: Configuration panel for models and debug options
- **Loading States**: Smooth shimmer effects and progress indicators

## 📊 Debug & Observability

Enable debug mode to see:
- Token usage and cost estimates
- Response latency metrics
- Document retrieval scores
- Agent reasoning traces
- Performance bottlenecks

## 🔧 Configuration

### Backend Configuration
- **Models**: Easily switch between OpenAI, Anthropic, or local models
- **Vector Store**: Configure FAISS parameters or switch to ChromaDB
- **Memory**: Adjust conversation buffer size
- **Tools**: Add custom tools via the ToolRegistry

### Frontend Configuration
- **Themes**: Tailwind CSS with customizable color schemes
- **Animations**: Framer Motion with configurable timing
- **API Endpoints**: Environment-based configuration

## 📂 Project Structure

```
/insightflow
├── backend/
│   ├── main.py              # FastAPI application
│   ├── graphs/
│   │   └── agent_graph.py   # LangGraph agent implementation
│   ├── tools/
│   │   └── mock_tools.py    # Tool implementations
│   ├── retriever/
│   │   └── vector_store.py  # Vector store and RAG logic
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx          # Main application component
    │   ├── components/
    │   │   ├── ChatInterface.tsx
    │   │   ├── AgentFlowVisualizer.tsx
    │   │   └── SettingsModal.tsx
    │   └── index.css        # Tailwind CSS styles
    └── package.json
```

## 🌟 Key Features Demo

### Example Query Flow
```
User: "What are the tax implications for freelancers in Canada?"

Agent Processing:
1. 📝 Input: Parse query about Canadian freelance taxation
2. 🔍 Retrieval: Find 3 relevant tax documents (scores: 0.95, 0.87, 0.72)
3. 🧠 Analysis: Identify taxation topic, assess confidence: 89%
4. 💬 Response: Generate comprehensive answer with citations

Result: Detailed response about business income reporting, 
GST/HST requirements, deductible expenses, and record-keeping.
```

## 🚀 Future Enhancements

- **📄 Document Upload**: Allow users to upload their own documents
- **🗣️ Voice Interface**: Speech-to-text and text-to-speech
- **🤝 Multi-Agent**: Customer service vs. technical support agents
- **📈 Analytics**: Usage patterns and query analysis
- **🔐 Authentication**: User accounts and conversation history
- **☁️ Deployment**: Docker containers and cloud deployment guides

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Built with ❤️ using LangChain, LangGraph, FastAPI, React, and modern web technologies.**