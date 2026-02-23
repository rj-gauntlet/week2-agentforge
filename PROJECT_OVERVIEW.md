# Project Overview: Plain English Breakdown

*This is a simplified, high-level summary of what we are building, who it is for, and how we are implementing it. For technical specifics, always refer to the `PRD.md` and `PRE_SEARCH.md`.*

---

### What is this project?
You are building a **smart healthcare assistant** (an AI "agent"). 

Most AI chatbots (like ChatGPT) just predict the next word based on what they read on the internet. That is dangerous in healthcare because they can confidently make things up (hallucinate). 

An **AI Agent** is different. Instead of just talking, it has "hands" it can use to fetch real data. When you ask it a question, it pauses, decides which tool to use, goes and looks up the real answer, and then summarizes that real data for you.

We are building an agent that can do five specific things:
1. Check if two medications have a bad reaction with each other.
2. Look up a patient's symptoms to suggest how urgent it is.
3. Search a directory for doctors by specialty.
4. Check if a doctor has open appointment slots.
5. Check if a patient's insurance covers a specific procedure.

### Who is it for?
It is designed to be an add-on for **OpenEMR**, which is a popular, free software system that real clinics and hospitals use to manage patient records and scheduling. 

The people using your AI agent would be clinic staff, nurses, or doctors who want a quick way to ask questions (e.g., *"Does Dr. Smith have any openings next Tuesday?"* or *"Do Aspirin and Ibuprofen interact?"*) without having to click through a dozen different menus in the software.

### How are we going to implement it?
We only have a week, so we have to be smart about how we build it. Here is the blueprint in simple terms:

**1. The Brain (The LLM)**
We will use a smart AI model (like Claude or GPT-4o) as the brain. Its only job is to understand the user's question, decide which tool to pick up, and then summarize the answer in plain English.

**2. The Framework (LangChain)**
Think of LangChain as the plumbing. It is just a library of code that connects the "Brain" to the "Tools." It makes it easy to say to the AI: *"Here are 5 tools you can use, here is how you use them, now go answer the user's question."*

**3. The Tools (Real vs. Fake Data)**
Because we only have a week, we cannot hook up to real hospital databases for everything. 
* **The "Hero" Tool:** For the drug interaction checker, we will use a real, curated spreadsheet of drug interactions. When the AI uses this tool, it is reading real facts.
* **The "Mock" Tools:** For things like appointment slots or provider searches, we will just write a small piece of code that returns fake, dummy data (e.g., always saying *"Dr. Smith has an opening at 2 PM"*). This proves your AI *knows how to use the tool*, without us having to build a massive scheduling database.

**4. The Safety Net (Verification)**
Because this is healthcare, the AI cannot give medical advice or diagnose people. We will add strict rules:
* If a user asks *"What is wrong with me?"*, the AI will be forced to add a disclaimer: *"I am an AI, please talk to your doctor."*
* We will force the AI to cite its sources (e.g., *"According to the drug interaction checker..."*). If it can't cite the tool, it isn't allowed to answer.

**5. The Flight Recorder (Observability / LangSmith)**
When an AI makes a mistake, it's hard to know *why* it made the mistake. "Observability" just means installing a flight recorder (a tool called LangSmith). Every time a user asks a question, LangSmith secretly logs exactly what the AI was thinking, which tool it tried to use, how long it took, and what it cost. If the AI breaks, we look at the flight recorder to fix it.

**6. The Report Card (Evals)**
A flashy demo isn't enough; we have to prove it works safely. We will write a "Report Card" (an Evaluation suite) with 50 test questions. 
* 20 normal questions (*"Any appointments on Tuesday?"*)
* 10 tricky questions where data is missing
* 10 "hacker" questions where we try to trick the AI into giving illegal medical advice.

We will run this report card automatically to grade the AI. By the end of the week, your AI needs to score an A (over 80%) on this test to prove it is safe enough for the real world. 

**Summary:** We are connecting a smart AI to 5 specific tools using LangChain, putting up strict safety guardrails, installing a flight recorder to track its thoughts, and grading it against 50 test questions to prove it won't give dangerous medical advice.