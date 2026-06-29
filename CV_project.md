# Movie Discovery & Recommendation Platform

GitHub: https://github.com/DoVanMinhTai/Movie-Discovery-Recommendation-Platform

## Description
A smart movie website that gives each user personal movie picks and has a fast AI chatbot. It mixes a large movie database with live data like trailers and posters for a smooth experience.

## My Responsibilities
- Built the main backend with Spring Boot as a safe middle layer that handles user login (Spring Security + JWT) and sends requests to the Python AI services.
- Made 30+ REST APIs with one shared error handler and 20+ standard response codes, plus API docs (Swagger), so the system stays stable and easy to use.
- Mixed two ways to suggest movies (user ratings + movie details) with a 40/60 weighted blend to give better picks and fix the new user/movie "Cold Start" problem.
- Built an AI chatbot using a RAG flow: it finds movie data with Elasticsearch, then uses the Groq API (LLM) to give smart answers in real time.
- Used Sentence-Transformers to turn movie details into vectors, enabling smart search in Elasticsearch (keyword + k-NN vector search).
- Used batch insert to save millions of similar-movie pairs into PostgreSQL fast, and added Redis cache to make repeat requests quicker.
- Packed the whole project (Java, Python, databases) into 9 Docker services with Docker Compose, so it runs the same on any machine.

## Key Technologies
Java 21, Spring Boot 3.4, Spring Security (JWT), REST API, PostgreSQL, Redis, Elasticsearch (Vector Search), Docker, Docker Compose, Python (FastAPI), RAG, Groq API (LLM), Sentence-Transformers.

---

# Version 2 — Fullstack Developer (Java + React)

## Description
A smart movie website that gives each user personal movie picks and has a fast AI chatbot. It mixes a large movie database with live data like trailers and posters for a smooth experience.

## My Responsibilities
- Built the backend with Spring Boot, with user login (Spring Security + JWT) and 30+ REST APIs that the frontend calls.
- Built the frontend with React and TypeScript, using Redux Toolkit for app state and TanStack Query to fetch and cache API data.
- Made the UI with TailwindCSS and React Router, with pages for home, search, movie details, watchlist, profile, and an admin panel.
- Added a chat box on the frontend that talks to the AI chatbot in real time.
- Mixed two ways to suggest movies (user ratings + movie details) with a 40/60 weighted blend to fix the new user/movie "Cold Start" problem.
- Built an AI chatbot using a RAG flow: it finds movie data with Elasticsearch, then uses the Groq API (LLM) to answer in real time.
- Used Redis cache and batch insert in PostgreSQL to keep the app fast.
- Packed the whole project (Java, Python, databases) into 9 Docker services with Docker Compose.

## Key Technologies
Java 21, Spring Boot 3.4, Spring Security (JWT), REST API, React 19, TypeScript, Redux Toolkit, TanStack Query, TailwindCSS, Vite, PostgreSQL, Redis, Elasticsearch, Docker, Docker Compose, Python (FastAPI), RAG, Groq API (LLM).
