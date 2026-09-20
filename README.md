# ContextLoss

## Context Integrity System for Human Handoffs

> **The world's workflows don't lose data. They lose context.**

ContextLoss is a context-analysis system that detects important information that gets **lost, changed, or contradicted** when work moves from one person or stage to another.

---

## 🚨 Problem

In real-world workflows, information is frequently passed between:

* Employees
* Support teams
* Maintenance teams
* Departments
* Managers
* Customers
* Operations teams

During these handoffs, important details can disappear or change.

### Example

**Original request**

> Repair machine X before Friday. It overheats after 2 hours at the college factory.

**Handoff**

> Repair machine X. Customer reports overheating.

The main task is still present, but important context has disappeared:

* Deadline: before Friday
* Time condition: after 2 hours
* Location: college
* Location: factory

A basic text-similarity system may still consider these messages related.

**ContextLoss looks beyond simple text similarity.**

---

# 💡 Solution

ContextLoss compares the original request with the handoff and identifies three types of context problems.

### 🔴 LOST

Important information exists in the original request but is missing from the handoff.

ContextLoss currently analyzes information such as:

* Deadlines
* Time conditions
* Locations
* Conditions
* Priorities
* Quantities

### 🟡 CHANGED

Important information exists in both messages but has changed.

**Example:**

> Original: Repair 5 machines.

> Handoff: Repair 3 machines.

ContextLoss detects:

> Quantity changed: 5 machines → 3 machines

### 🟠 CONFLICTING

Information in the handoff contradicts information in the original request.

**Example:**

> Original: Urgent repair required before Friday.

> Handoff: Routine repair can be handled next week.

ContextLoss detects a priority conflict.

---

# 📊 Context Integrity

ContextLoss generates a **Context Integrity score** representing how much important context was preserved during the handoff.

Example:

```text
Context Integrity: 40%
Risk Level: MEDIUM
```

The system also provides an **Integrity Breakdown** explaining why the score changed.

For example:

```text
4 important context elements were lost

- Deadline: before Friday
- Time condition: after 2 hours
- Location: college
- Location: factory
```

This makes the result explainable instead of returning only a numerical score.

---

# 🔎 Historical Case Search

ContextLoss uses **OpenSearch** to retrieve previously analyzed cases with related context.

This allows users to compare a current handoff with historical examples.

For example, a current case may be compared with previous cases involving:

* Similar conditions
* Similar locations
* Similar priorities
* Similar quantities
* Similar wording

The historical results include:

* Risk level
* Context Integrity
* Text Similarity
* Original request
* Handoff

This provides additional context when reviewing a new handoff.

---

# ⚙️ How It Works

```text
Original Request
       ↓
Handoff Context
       ↓
Context Extraction
       ↓
Compare Important Information
       ↓
┌─────────────────────────────┐
│ LOST                        │
│ CHANGED                     │
│ CONFLICTING                 │
└─────────────────────────────┘
       ↓
Context Integrity Score
       ↓
Risk Level
       ↓
Historical Case Search
       ↓
Explainable Dashboard
```

---

# 🧠 Context Analysis

The analyzer extracts structured information from the text.

### Information currently analyzed

| Context Type   | Examples                         |
| -------------- | -------------------------------- |
| Deadline       | before Friday, within 2 days     |
| Time condition | after 2 hours, during heavy rain |
| Location       | college, factory, hostel, office |
| Condition      | overheating, leaking, broken     |
| Priority       | urgent, routine, critical        |
| Quantity       | 5 machines, 3 vehicles           |

The extracted information is then compared between the original request and the handoff.

---

# 📈 Example Results

### Example 1 — Lost Context

**Original**

```text
Repair machine X before Friday.
It overheats after 2 hours at the college factory.
```

**Handoff**

```text
Repair machine X.
Customer reports overheating.
```

Result:

```text
Text Similarity: 53.23%
Context Integrity: 40%
Risk Level: MEDIUM
```

Lost context:

```text
Deadline: before Friday
Time condition: after 2 hours
Location: college
Location: factory
```

---

### Example 2 — Conflicting Context

**Original**

```text
Urgent repair required before Friday.
```

**Handoff**

```text
Routine repair can be handled next week.
```

Result:

```text
Risk Level: CRITICAL
```

The system identifies a conflict between the original **urgent** priority and the handoff's **routine** priority.

---

### Example 3 — Changed Context

**Original**

```text
Repair 5 machines before Friday at the college factory.
```

**Handoff**

```text
Repair 3 machines before Friday at the college factory.
```

Result:

```text
Context Integrity: 90%
Text Similarity: 100%
```

The system detects:

```text
Quantity changed: 5 machines → 3 machines
```

This demonstrates why text similarity alone is not enough.

---

# 🔍 Why OpenSearch?

OpenSearch is used as the historical search layer of ContextLoss.

When a new case is analyzed, ContextLoss searches previously stored cases for related requests and handoffs.

The system combines text similarity with important context overlap to identify useful historical cases.

OpenSearch is an **AWS open-source technology** and is the main AWS open-source component used in this project.

The project runs OpenSearch locally, so an AWS cloud account or payment card is not required for the current implementation.

---

# 🏗️ Architecture

```text
                User
                 │
                 ▼
        ┌─────────────────┐
        │ Flask Dashboard │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Context Analyzer│
        └────────┬────────┘
                 │
        ┌────────┴─────────┐
        ▼                  ▼
 Context Comparison   Context Scoring
        │                  │
        └────────┬─────────┘
                 ▼
        Context Integrity
                 │
        ┌────────┴─────────┐
        ▼                  ▼
    SQLite            OpenSearch
   Case Storage      Historical Search
```

---

# 🛠️ Tech Stack

### Application

* Python
* Flask
* HTML
* CSS
* JavaScript

### Analysis

* Python-based context extraction
* Text similarity
* Rule-based context comparison
* Explainable integrity scoring

### Storage

* SQLite
* OpenSearch

### Development

* Git
* GitHub
* Docker
* Docker Desktop

### AWS Technology

* OpenSearch

---

# 📁 Project Structure

```text
ContextLoss/
│
├── app.py
├── analyzer.py
├── database.py
├── opensearch_db.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── index.html
│   └── cases.html
│
├── static/
│   └── style.css
│
└── test_cases/
    └── cases.json
```

---

# 🚀 Running Locally

## 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd ContextLoss
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Start OpenSearch

Make sure Docker Desktop is running.

```powershell
docker run -d --name contextloss-opensearch -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" -e "DISABLE_SECURITY_PLUGIN=true" opensearchproject/opensearch:latest
```

Verify:

```powershell
curl.exe http://localhost:9200
```

## 5. Start ContextLoss

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🔐 Privacy

The current project is designed to run locally.

The application stores analyzed cases locally using SQLite and OpenSearch.

No external AI API is required for the current context-analysis implementation.

---

# 🎯 Why ContextLoss?

Traditional text comparison mainly asks:

> **"Are these two texts similar?"**

ContextLoss asks a more useful question:

> **"Did the important information survive the handoff?"**

Two messages can have high textual similarity while still losing critical operational information.

ContextLoss makes those differences visible and explainable.

---

# 📚 What I Learned

Building ContextLoss helped me work with:

* Context extraction from natural language
* Text similarity
* Explainable scoring
* Risk classification
* Conflict detection
* SQLite persistence
* OpenSearch indexing
* Historical search
* Flask application development
* Docker
* Git/GitHub
* Building an explainable dashboard
* Designing a project around a real workflow problem

---

# ⚠️ Current Limitations

ContextLoss currently relies on predefined context patterns and rule-based extraction.

It may not understand every possible natural-language expression or complex business context.

The current version is a working prototype rather than a production workflow system.

---

# 🔮 Future Scope

Possible future improvements include:

* LLM-based context extraction
* Agent-based workflow analysis
* More domain-specific context types
* Multi-language support
* Real-time workflow integrations
* Role-based access control
* Cloud deployment
* Advanced semantic search
* Automated alerts for high-risk handoffs

These are future possibilities and are **not part of the current implementation**.

---

# 🏆 Hackathon

Built for:

**WeMakeDevs × AWS — First Commit**

**Bharat Builds Tour 2026**

The project uses **OpenSearch**, an AWS open-source technology, as its historical context search layer.

---

# 🤖 AI Development Disclosure

AI coding assistants were used during development for:

* Debugging
* Code suggestions
* Documentation
* UI improvements
* Development guidance

The project was tested and integrated manually as part of the development process.

---

# 📌 Project Status

**Working prototype**

Current working flow:

```text
Original Request
        ↓
Handoff
        ↓
Context Analysis
        ↓
Lost / Changed / Conflicting Detection
        ↓
Context Integrity
        ↓
Risk Level
        ↓
Historical OpenSearch Search
        ↓
Dashboard
```

> **ContextLoss — because a successful handoff should preserve more than just the words.**
