📊 AI-Powered Data Analyst Copilot

Natural Language → Safe SQL → Cloud PostgreSQL → Visualization → Business Insights

An end-to-end AI-powered analytics application that allows users to ask business questions in plain English and automatically receive:

Schema-aware PostgreSQL queries

Live database results

Automated visualizations

Grounded business insights

Read-only and validated SQL execution

🔗 Live Demo:
https://ai-data-analyst-copilot-9dmnh4izbccbpgpuyur8e2.streamlit.app

📸 Application Screenshots

1. Application Overview



2. AI Business Insights



3. Automated Visualization



4. Query Result Data



5. Generated SQL Query



💼 Why This Project?

Business teams frequently need quick answers from their data, but answering even simple questions may require:

Understanding the database structure

Writing SQL

Validating the query

Extracting the data

Building a visualization

Interpreting the result

This project demonstrates how an AI-assisted analytics workflow can combine these steps into one interactive application.

A user can simply ask:

"Which product categories generate the highest merchandise sales?"

and the Copilot automatically generates SQL, validates it, queries the database, creates a chart and explains the result.

⚡ Business Value

Self-Service Analytics — users can explore data using natural-language questions instead of manually writing SQL.

Faster Data Exploration — SQL generation, query execution, visualization and first-level interpretation happen in one workflow.

Automated Decision Support — query outputs are converted into readable visualizations and concise business insights.

Consistent Metrics — a semantic layer defines important business concepts such as merchandise sales, unique customers and delivery performance.

Controlled AI Access — generated SQL is validated and executed through a dedicated read-only PostgreSQL role.

📦 Dataset

The application uses the Brazilian Olist E-commerce dataset, transformed into a PostgreSQL analytical warehouse.

Metric

Value

Orders

99,441

Unique Customers

96,096

Products

32,951

Sellers

3,095

Transaction Period

2016–2018

The analytical warehouse contains customer, product, seller and date dimensions alongside order, order-item, payment and review fact tables.

🤖 How It Works

flowchart TD
    A[Business Question in Plain English]
    B[Database Schema + Semantic Layer]
    C[Gemini / Groq LLM]
    D[PostgreSQL Query Generation]
    E[SQL Safety Validator]
    F[Supabase PostgreSQL - Read Only]
    G[Query Result DataFrame]
    H[Automatic Visualization]
    I[Grounded AI Business Insights]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I

🧠 Schema-Aware SQL Generation

The Copilot receives context about:

Tables and columns

Primary and foreign-key relationships

Table grain

Business metric definitions

Analytical guardrails

This helps reduce invalid joins and incorrect metric calculations.

📐 Business Semantic Layer

The semantic layer defines important analytical concepts.

Merchandise Sales

For order-level analysis:

SUM(fact_orders.merchandise_value)

For product/category/seller analysis:

SUM(fact_order_items.price)

Unique Customers

The system uses:

customer_unique_id

instead of treating every customer_id as a separate real-world customer.

Payment Analysis

fact_payments is payment-grain data, so:

COUNT(DISTINCT order_id)

is used when counting orders.

🔒 SQL Safety Layer

The application allows read-only analytical SQL such as:

SELECT
WITH

and blocks destructive operations such as:

INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
COPY
CALL
EXECUTE
MERGE
VACUUM

The validator also blocks multiple SQL statements and unsafe commands.

🛡️ Database-Level Protection

The deployed application connects through a dedicated read-only PostgreSQL role:

ai_analyst_ro

Permissions:

SELECT  ✅
INSERT  ❌
UPDATE  ❌
DELETE  ❌

The role also uses:

default_transaction_read_only = ON

This provides an additional database-level safety layer.

⏱️ Query Guardrails

Query timeout: 10 seconds

Maximum returned rows: 500

Safe SQL is wrapped and controlled before execution.

📈 Automated Visualization

The application automatically selects a useful visualization based on returned data, including:

Bar charts

Time-series line charts

Scatter plots

No chart when a visualization would not add value

Visualizations are created using Plotly.

💡 Grounded AI Insights

AI-generated insights are based on the actual SQL result returned by the database.

The insight layer is instructed not to invent causes, campaigns, seasonality, strategies or external events unless supported by the query result.

💬 Example Questions

What are the top 5 product categories by merchandise sales?

Which customer states have the highest late delivery rate?

How does customer review score differ between late and on-time deliveries?

What are the most commonly used payment methods and their total payment value?

How have merchandise sales changed month by month?

How many unique customers made repeat purchases?

Which sellers generate the highest merchandise sales and how many orders do they handle?

🔄 Multi-Provider LLM Architecture

The application supports:

Primary: Google Gemini

Fallback: Groq

This improves resilience compared with relying on a single LLM provider.

🧰 Tech Stack

Layer

Technology

Frontend

Streamlit

Language

Python

Database

PostgreSQL

Cloud Database

Supabase

Database Connection

SQLAlchemy

AI Providers

Gemini + Groq

Data Processing

Pandas

Visualization

Plotly

SQL Validation

sqlparse

Testing

Pytest

Deployment

Streamlit Community Cloud

Monitoring

UptimeRobot

Version Control

Git + GitHub

☁️ Deployment Architecture

User / Recruiter
       ↓
Streamlit Community Cloud
       ↓
Gemini / Groq
       ↓
SQL Safety Validator
       ↓
Read-Only Database Role
       ↓
Supabase PostgreSQL
       ↓
Analytics Schema

🟢 Availability Monitoring

Two UptimeRobot monitors are used:

Streamlit application monitor

Supabase lightweight keepalive endpoint monitor

The Supabase health check exposes no sensitive business data.

🧪 Automated Tests

Run:

pytest tests -v

Current suite:

SQL Validator      11 tests
Query Executor      6 tests
Visualizer          7 tests
---------------------------
Total              24 tests

Current result:

24 passed

📁 Project Structure

ai-data-analyst-copilot/
│
├── app/
│   ├── app.py
│   ├── analyzer.py
│   ├── database.py
│   ├── insight_generator.py
│   ├── llm.py
│   ├── query_executor.py
│   ├── schema.py
│   ├── semantic_layer.py
│   ├── sql_generator.py
│   ├── sql_validator.py
│   └── visualizer.py
│
├── tests/
│   ├── test_query_executor.py
│   ├── test_sql_validator.py
│   └── test_visualizer.py
│
├── prompts/
├── config/
├── images/
├── documentation/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

🚀 Run Locally

1. Clone the repository

git clone https://github.com/Rishabh11122001/ai-data-analyst-copilot.git
cd ai-data-analyst-copilot

2. Create and activate a virtual environment

python -m venv .venv

Windows:

.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create a .env file using .env.example as the template.

Required configuration includes:

Gemini and/or Groq API keys

PostgreSQL host

PostgreSQL port

Database name

Database user

Database password

SSL mode

Never commit .env or real credentials to GitHub.

5. Start Streamlit

streamlit run app/app.py

🔐 Secrets Management

Local development uses:

.env

Production deployment uses:

Streamlit Secrets

The repository contains only placeholder configuration through .env.example.

🎯 What This Project Demonstrates

SQL

PostgreSQL

Data modeling

Dimensional modeling

Business metric definition

Natural-language analytics

Generative AI

Prompt engineering

SQL validation

Database security

Data visualization

Cloud databases

Application deployment

Automated testing

Monitoring

Rather than acting as a simple chatbot, the application integrates AI into a controlled analytical workflow connected to a real relational data warehouse.

🔗 Links

🌐 Live Application

https://ai-data-analyst-copilot-9dmnh4izbccbpgpuyur8e2.streamlit.app

💻 GitHub Repository

https://github.com/Rishabh11122001/ai-data-analyst-copilot

👤 Author

Rishabh

Data Analytics | SQL | Python | Power BI | AI-Assisted Analytics