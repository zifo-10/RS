# Recommendation System

## Overview
This project is a **Recommendation System** that allows users to:
1. **Insert** product data into MongoDB and Qdrant vector database.
2. **Search** for similar products using vector-based similarity search.
3. **Filter** results based on attributes like color and price.
4. **Analyze Transactions** to suggest related products based on purchasing behavior.
5. **Search Online** for related items from Amazon using Tavily API.

---

## Features
- **MongoDB Integration**: Stores product and transaction data.
- **Vector Search with Qdrant**: Embeds product descriptions and enables similarity-based retrieval.
- **User Transactions Analysis**: Identifies frequently bought-together items.
- **Tavily Web Search**: Fetches related product listings from Amazon.
- **FastAPI Backend**: Provides endpoints for inserting data, searching, and recommendations.

---

## Tech Stack
- **FastAPI** - Backend framework
- **MongoDB** - NoSQL database for storing products & transactions
- **Qdrant** - Vector database for similarity search
- **Tavily API** - Online search integration
- **Python 3.12** - Programming language

---

## Installation
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/yourusername/recommendation-system.git
cd recommendation-system
```

### 2️⃣ Set Up Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

---

## Configuration
### 1️⃣ Set Up Environment Variables
Create a `.env` file in the root directory:
```ini
QDRANT_URI="https://"
QDRANT_API_KEY="euJhbGc**************"
MONGO_URI="mongodb://"
COHERE_API_KEY="vrx0*****************"
VECTOR_DB_PORT=6***
VECTOR_DB_URI="http:/"
TAVILYAPI_KEY="tvly-dev-*************"
MONGO_DB_NAME=""
```

### 2️⃣ Start MongoDB & Qdrant
Make sure MongoDB and Qdrant are running locally or on your cloud provider.

### 3️⃣ Run the Application
```sh
uvicorn app.main:app --reload
```

---

## API Endpoints
### 1️⃣ Insert Item
```http
POST /insert_item
```
#### Request Body (JSON):
```json
{
  "name": "Yale Forklift",
  "description": "رافعات شوكية لنقل المواد الثقيلة",
  "material": "Metal",
  "color": "Yellow",
  "price": 250000.0,
  "related_items": ["Pallet Jack", "Digital Scale"],
  "category": "Heavy Machinery"
}
```

### 2️⃣ Search for Similar Items
```http
GET /search?query=Forklift&filter_color=Yellow&filter_price_max=300000
```

### 3️⃣ Get Related Items from Transactions
```http
GET /related_items/{item_id}
```

### 4️⃣ Search Amazon for Related Products
```http
GET /web_search?query=Forklift site:amazon.com
```

---
## Future Enhancements:

- 🔹 **Enhance Recommendation Algorithms**: Implement collaborative filtering techniques to offer more personalized product suggestions based on user behavior.
  
- 🔹 **ML-Powered Product Prediction**: Develop a machine learning model to predict and recommend products to users based on their preferences and historical data.
  
- 🔹 **Front-End Integration**: Build and integrate a user-friendly interface to display recommendations and interact with the system seamlessly.
  
- 🔹 **Support Multiple Languages**: Add multi-language support to broaden accessibility and make the platform user-friendly across different regions.



