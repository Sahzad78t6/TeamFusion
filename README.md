# GrowthOS

A starter project structure for GrowthOS.
# 🚀 GrowthOS
### The AI That Curates Your Future

> **An Agentic AI Growth Curator that helps users become the person they aspire to be by understanding their aspirations, habits, and evolving identity.**

---

# 📌 Problem Statement

Current recommendation systems (YouTube, Instagram, Netflix, LinkedIn, etc.) optimize for **attention**, maximizing watch time and engagement.

Our goal is different.

GrowthOS optimizes for **human potential**.

Instead of recommending random content, GrowthOS continuously understands the user's aspirations, habits, skills, and evolving identity, then curates personalized knowledge, media, and real-world experiences to accelerate personal growth.

---

# 🎯 Our Vision

We are **NOT** building another recommendation system.

We are building an **Agentic AI Growth Operating System**.

GrowthOS continuously:

- Understands who the user wants to become.
- Builds an evolving Identity Twin.
- Detects the gap between the current self and desired self.
- Curates personalized media, knowledge, and experiences.
- Learns from user feedback.
- Adapts recommendations continuously.

---

# 🧠 Core Idea

Every user has an **Identity Twin**.

Instead of storing only profile information, the Identity Twin stores:

- Aspirations
- Skills
- Habits
- Interests
- Reflections
- Progress
- Learning Style
- Growth History
- ML Predictions

The Identity Twin continuously evolves.

---

# ⚙️ High-Level Workflow

```
User
   │
   ▼
Onboarding
   │
   ▼
Identity Twin Creation
   │
   ▼
Gap Analysis
   │
   ▼
AI Curates
• Knowledge
• Media
• Experiences
   │
   ▼
User Feedback
   │
   ▼
ML Predictions
   │
   ▼
Identity Twin Updated
   │
   ▼
Better Recommendations
```

---

# 🏗 Architecture

```
React Frontend

        │

        ▼

FastAPI Backend

        │

        ▼

LangGraph Supervisor

        │

 ┌──────┼─────────────┐

 ▼      ▼             ▼

Agents   Mem0      ML Models

        │

        ▼

Supabase

        │

        ▼

Frontend Dashboard
```

---

# 🛠 Technology Stack

## Frontend

- React
- TypeScript
- Tailwind CSS
- Vite

## Backend

- FastAPI

## Agent Framework

- LangGraph
- LangChain

## Memory

- Mem0

## Database

- Supabase

## Machine Learning

- Scikit-learn

## LLM

- Groq (llama-3.3-70b-versatile)

## Deployment

- Vercel
- Render

---

# 📂 Folder Structure

```
GrowthOS/

frontend/

backend/

ml/

docs/

deployment/

README.md
```

---

# 👥 Team Responsibilities

## 👤 Member 1 — Frontend

Responsible for:

- UI
- Dashboard
- Authentication Pages
- Analytics
- API Integration

Works inside:

```
frontend/
```

---

## 👤 Member 2 — Backend

Responsible for:

- FastAPI
- APIs
- Services
- Database Integration

Works inside:

```
backend/api
backend/services
backend/database
```

---

## 👤 Member 3 — AI

Responsible for:

- LangGraph
- LangChain
- Mem0
- Prompt Engineering
- Agent Logic

Works inside:

```
backend/agents

backend/graph

backend/memory

backend/prompts

backend/llm
```

---

## 👤 Member 4 — ML & Integration

Responsible for:

- Dataset
- Model Training
- Predictions
- Deployment
- Final Integration

Works inside:

```
ml/

deployment/
```

---

# 🤖 AI Agents

GrowthOS uses a multi-agent architecture.

## Supervisor Agent

Decides which agent should execute.

---

## Identity Agent

Creates and updates the Identity Twin.

---

## Planner Agent

Breaks user aspirations into achievable milestones.

---

## Curator Agent

Curates:

- Books
- Videos
- Podcasts
- Communities
- Projects
- Hackathons
- Mentors
- Internships

---

## Mentor Agent

Acts as the user's personal AI mentor.

---

## Reflection Agent

Learns from daily reflections and updates memory.

---

# 🧠 Machine Learning

Current ML models:

- Burnout Prediction
- Identity Drift Prediction
- Growth Prediction

These models continuously update the Identity Twin.

---

# 🌿 Git Workflow

Never push directly to `main`.

Branches:

```
main

develop

frontend

backend

ai

ml

integration
```

Workflow:

```
feature branch

↓

develop

↓

main
```

---

# 📌 Development Priority

## Phase 1

- Project Setup
- Authentication
- Supabase
- Folder Structure

---

## Phase 2

- Identity Twin
- LangGraph
- Supervisor
- Onboarding

---

## Phase 3

- Recommendation Engine
- Reflection
- Dashboard

---

## Phase 4

- ML
- Integration
- Deployment

---

# 🚀 Round 1 Goal

Must have:

- Running frontend
- Running backend
- Supabase connected
- LangGraph workflow
- Identity Twin structure
- Architecture explanation

---

# 🚀 Round 2 Goal

Must have:

- Working prototype
- Identity Twin updates
- AI recommendations
- Reflection
- ML predictions

---

# 🚀 Round 3 Goal

Must have:

- Complete UI
- Live Demo
- PPT
- Deployment
- Stable Application

---

# 📢 Development Rules

- Keep commits small and meaningful.
- Do not modify another member's module without discussion.
- Create reusable components.
- Write clean, modular code.
- Keep APIs RESTful.
- Follow the agreed folder structure.
- Test your module before merging.

---

# 🎯 Project Goal

GrowthOS is not another AI chatbot.

It is an **Agentic AI Growth Operating System** that continuously understands, remembers, predicts, and guides users toward becoming the best version of themselves.

> **"We don't optimize for attention. We optimize for human potential."**