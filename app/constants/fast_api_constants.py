class FastAPIConstants:
    TITLE = "PicksieAI | Server"
    DESCRIPTION = """
### Project Description: PicksieAI

#### Overview
**PicksieAI** is a server-side backend project designed to facilitate advanced document management and interaction through the use of modern AI technologies. The system offers features such as creating embeddings, searching within embeddings, deleting embeddings, and enabling chat functionalities on ingested documents.

#### Key Features
- **Conversational Chatbot:** Enables interactive chat functionalities, allowing users to converse and extract information from the ingested documents seamlessly.

#### Technology Stack
- **Programming Language:** Python
- **Framework:** FastAPI

#### Team Members
- **Developer:** Khursheed, Nooman, Rahul
- **Manager:** Musse, Zaki

This project leverages the capabilities of FastAPI to ensure a high-performance, scalable, and robust backend infrastructure, supporting the AI-driven features that make document management and interaction more intuitive and powerful.
    """
    SUMMARY = "Project Summary"
    VERSION = "1.0.0"
    T_N_C = "http://PicksieAI-project.com/terms-and-conditions"
    CONTACT = {
        "name": "Khursheed Gaddi",
        "url": "https://PicksieAI-project.com",
        "email": "gaddi33khursheed@gmail.com",
    }
    LICENSE_INFO = {
        "name": "PicksieAI",
        "url": "http://PicksieAI-project.com/license",
    }

    OPENAPI_TAGS_METADATA = [
        {
            "name": "API Testings",
            "description": "Provides a route to run tests at deployment time."
        },
        {
            "name": "Health",
            "description": "Check health of the server"
        },
        {
            "name": "Chat",
            "description": "Conversational chatbot with RAG"
        },
    ]
