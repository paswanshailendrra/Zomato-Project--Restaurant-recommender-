# Project Context: AI-Powered Restaurant Recommendation System

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system intelligently suggests restaurants based on user preferences by combining structured data with a Large Language Model (LLM).

---

## Objective

Design and implement an application that:

- Takes user preferences (such as location, budget, cuisine, and ratings)
- Uses a real-world dataset of restaurants
- Leverages an LLM to generate personalized, human-like recommendations
- Displays clear and useful results to the user

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - (and other applicable fields from the dataset)

### 2. User Input

Collect user preferences:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | Low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | User-defined threshold |
| **Additional preferences** | Family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason and rank options

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants
- Provide explanations (why each recommendation fits)
- Optionally summarize choices

### 5. Output Display

Present top recommendations in a user-friendly format:

- **Restaurant Name**
- **Cuisine**
- **Rating**
- **Estimated Cost**
- **AI-generated explanation**

---

## Data Source

- **Dataset:** [Zomato Restaurant Recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) on Hugging Face
- **Provider:** ManikaSaini

---

## Key Technical Components

1. **Data pipeline** — Load, clean, and filter restaurant records from the Hugging Face dataset
2. **Preference matching** — Map user inputs (location, budget, cuisine, rating) to filtered restaurant candidates
3. **LLM integration** — Prompt engineering for ranking, reasoning, and natural-language explanations
4. **Presentation layer** — Display ranked recommendations with structured fields and AI-generated rationale

---

## Success Criteria

- Recommendations are grounded in real dataset entries (not hallucinated restaurants)
- User preferences meaningfully influence filtering and ranking
- LLM output is personalized, readable, and explains *why* each restaurant was suggested
- Results are presented clearly with name, cuisine, rating, cost, and explanation
