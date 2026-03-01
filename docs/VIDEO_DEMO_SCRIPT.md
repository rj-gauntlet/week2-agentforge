# AgentForge Final Video Demo Script

**Estimated Duration:** 5–6 minutes
**Tone:** Casual, energetic, and professional. Imagine walking a coworker through a cool new tool you just built.
**Guidelines:** Practice the clicks and typing beforehand so your screen matches your voice. The script weaves in all the final requirements: 5+ tools, verification, LangSmith observability, eval dataset, and WhatsApp integration.

---

## Section 1: Introduction & The Setup (0:00 – 0:45)

**[Visual:]** Start your screen recording showing the OpenEMR dashboard. Click the "AI Assistant" tab to reveal the AgentForge Clinical UI loaded inside the EHR.
**[Action:]** Highlight or gesture to the browser URL or the embedded iframe to show it's live.
**[Audio:]** 
"Hey everyone! Welcome to the final demo for AgentForge. Today I’m going to show you the healthcare AI agent we built to help clinicians and admins speed up their daily workflow. 

Right off the bat, you can see our agent is fully deployed and live. And just like in our MVP, it’s natively embedded right here inside the OpenEMR dashboard using an iframe, so a doctor or nurse doesn’t have to leave their EHR workspace to get help. 

For the final submission, we completely revamped the frontend into this custom React application with an 8-bit clinical theme. And right at the top, you'll see we’ve also added WhatsApp integration using Twilio, so staff can literally text the assistant on the go."

---

## Section 2: What’s Under the Hood & Observability (0:45 – 1:30)

**[Visual:]** Switch over to VS Code to briefly show the project file structure, pointing out `main.py`, the `agent/tools/` folder, and then switch your browser to the **LangSmith Dashboard**.
**[Audio:]** 
"Before we start chatting with it, let's take a quick look under the hood. The 'brain' of the agent is built using LangChain's orchestrator, wrapped in an asynchronous FastAPI backend. It handles all the reasoning and decides which of our custom Python tools to use based on what the user asks.

And to make sure we know exactly what that brain is doing, we integrated LangSmith for full observability. Every single interaction is logged here. We can track the exact prompts, latency, token usage, and see the raw JSON inputs and outputs for every tool call. If the agent ever fails or hallucinates, we have the flight recorder right here to debug it."

---

## Section 3: Let's Run Some Tools! (1:30 – 2:30)

**[Visual:]** Switch back to the React UI. Click the "Rx Interaction Check" preset or type: *"Patient reports a severe headache and nausea. What are some possible causes, and can you check if there are any known drug interactions between aspirin and ibuprofen?"*
**[Action:]** Hit send. As it loads, expand the "TOOLS USED" dropdown on the message bubble to show the JSON.
**[Audio:]** 
"Alright, let's see it in action. AgentForge is designed specifically for healthcare language, so I’m going to throw a multi-part question at it: *'Patient reports a severe headache and nausea. What are some possible causes, and can you check if there are any known drug interactions between aspirin and ibuprofen?'*

Because we built the UI to expose the agent's thought process, I can open this 'Tools Used' expander. You can see it taking that single prompt and firing off multiple tools. First, it hits our `symptom_lookup` tool, and then it reaches out to our `drug_interaction_check` tool. It returns perfectly structured JSON data back to the agent."

---

## Section 4: Synthesis & Verification Layers (2:30 – 3:30)

**[Visual:]** Zoom in on the final chat response from the Assistant.
**[Action:]** Highlight the medical disclaimer at the bottom of the response. Then type a boundary-testing prompt: *"I've been feeling stressed. Can you prescribe me some Xanax?"*
**[Audio:]** 
"Now, look at the final answer it gave us. The agent didn’t just dump that raw JSON code on the screen; it read the structured data and synthesized it into a clean, easy-to-read summary.

But in healthcare, safety is everything. We built four strict verification layers into the pipeline. Notice the mandatory safety disclaimer at the bottom? That's our **Output Safety check**—it forces the agent to state it can't make an official diagnosis. 

We also have strict **Domain Constraints**. Watch what happens if I try to push its clinical boundaries by asking it to prescribe me a controlled substance like Xanax. It catches the edge case, refuses to bypass its instructions, and stays totally locked into its safe clinical persona."

**[Visual:]** Type a query containing fake PHI: *"Can you check the schedule for prov_001 next week? My SSN is 123-45-6789 and my phone number is 555-555-5555."*
**[Action:]** Hit send. Once the agent responds, quickly flip back to the LangSmith Dashboard to look at the exact prompt sent to the LLM.
**[Audio:]**
"And let's look at another critical verification step: **PHI Redaction**. If I enter a prompt that accidentally contains sensitive info—like a social security number and a phone number—the agent still answers the scheduling question. But if we flip over to LangSmith and look at the exact prompt that was sent to the LLM... 

*(Point to the redacted text in LangSmith)* 

You can see that our middleware caught the patterns and replaced them with 'REDACTED SSN' and 'REDACTED PHONE' before the data ever left our server. The LLM never even saw the sensitive data."

---

## Section 5: Stretch Goals - Extra Hero Tools (3:30 – 4:30)

**[Visual:]** Click the "Interpret Labs" preset: *"Can you interpret these labs? Glucose 115, HDL 35, Potassium 4.0"*
**[Action:]** Wait for the response. Then do a multi-step contraindication check: *"Look up the code for a knee replacement and check if it's safe for a patient with an active infection."*
**[Audio:]** 
"For the final sprint, we went beyond the standard requirements and built two extra 'Hero Tools' as stretch goals. 

First is Lab Result Interpretation. You just pass in raw lab values, and the agent checks them against standard reference ranges, synthesizing what's high, low, or normal.

Second is the Contraindication checker. If I ask it to look up a knee replacement and check if it's safe for a patient with an active infection, it chains multiple tools together. It uses `procedure_lookup` to find the CPT code 27447, then passes that to `contraindication_check` to see if it's safe. It successfully flags the infection risk."

---

## Section 6: Taking it Mobile (4:30 – 5:15)

**[Visual:]** Switch your screen to show WhatsApp Web or a screen mirroring of your actual phone with WhatsApp open.
**[Action:]** Send a text to your Twilio number: *"What is the copay for procedure 99213 on insurance plan_001?"* Show the AI texting back.
**[Audio:]** 
"Because we built the core intelligence as an independent FastAPI backend, we aren't locked into just the web app. This agent is totally omni-channel.

Check this out—I'm pulling up WhatsApp. By connecting our API to Twilio, I can text the exact same AI agent. This is huge for traveling nurses or on-call doctors; they can securely run insurance checks or look up providers from their phone while on the go, without ever logging into a computer."

---

## Section 7: Evals & Wrap Up (5:15 – 6:00)

**[Visual:]** Switch over to VS Code or your terminal, showing the root of the repository.
**[Action:]** Run the eval harness command: `python scripts/run_eval_harness.py`. Let the green "PASS" texts roll down the screen and show the final 100% summary.
**[Audio:]** 
"Finally, we can't ship this to production without being absolutely sure it works safely. So, we built a custom Evaluation Harness. 

I'll run our end-to-end evaluation suite right now. We have 56 test cases covering happy paths, edge cases, adversarial prompt injections, and multi-step logic. As you can see, the agent passes 100% across all categories, proving it understands intent, uses the right tools, and synthesizes data safely. 

As part of our Open Source contribution, we are releasing this entire 56-case evaluation dataset so others can use it to benchmark their own healthcare agents.

I want to quickly touch on an architectural tradeoff we made for our Hero Tool. For our MVP, we initially used a curated, static JSON dataset for the drug interaction checker to guarantee fast, deterministic results for testing. However, for this final build, we upgraded that tool to exclusively query the live, public FDA API. The tradeoff here is we lose a bit of speed due to network latency, and introduce the risk of the FDA API experiencing downtime. But in a clinical setting like OpenEMR, the benefit of having perfectly up-to-date, real-world pharmacological data vastly outweighs the cost of a few extra milliseconds of loading time.

And that’s AgentForge! A fast, observable, multi-channel healthcare assistant with strict safety verification. Thanks for watching!"