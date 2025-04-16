from fastapi import FastAPI, Request
from openai import OpenAI
import dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from a .env file
dotenv.load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Create FastAPI app with metadata
app = FastAPI(
    title="Semantic Fashion Recommendation System",  # Application title
    description="A semantic search API for fashion recommendations.",      # Application description
    version="1.0.0"                                  # Application version
)

# Add middleware to handle Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define an endpoint to get recommendations
@app.post("/recommendations")
async def get_user_query(request: Request):
    try:
        # Parse the JSON body of the request
        body = await request.json()
        query = body.get("query")  # Extract the 'query' parameter from the JSON body
        print(query)

        if query:
            # Generate embedding using OpenAI API
            response = client.embeddings.create(
                input=query,                      # Input text for embedding
                model="text-embedding-3-small"   # Model used for embedding
            )
            # Extract the embedding from the response
            embedding = response.data[0].embedding
            # Return the user query and its embedding
            return {"ok": True, "user_query": query, "embedding": embedding}
        else:
            # Return an error if the 'query' parameter is missing
            return {"ok": False, "error": "Query parameter is missing"}
    except Exception as e:
        # Handle and return any errors that occur
        return {"ok": False, "error": f"An error occurred: {str(e)}"}