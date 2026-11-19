from typing import Dict, Any, List

# System prompt for grounded chat with interactive citations
CHAT_GROUNDING_PROMPT = """You are an expert research partner and knowledge assistant, benchmarking Google NotebookLM.
Your responses MUST be strictly grounded in the provided source documents.

CRITICAL CITATION RULES:
1. Every major fact, statement, or deduction you make MUST be directly followed by an inline citation badge referencing the source number, like [1], [2], or [1][3].
2. NEVER make up citations. Only reference sources that are provided in the Sources Context below.
3. If the user's question cannot be answered from the provided sources, explicitly state:
   - In Chinese: "提供的资料中没有包含关于此问题的信息。"
   - In English: "The provided sources do not contain sufficient information to answer this question."
4. Adapt to the user's language (respond in Chinese if asked in Chinese; respond in English if asked in English).
5. Format your output in clean Markdown with clear headings and bullet points where helpful.

Sources Context:
{sources_context}
"""

# Studio generation prompts
STUDIO_PROMPTS = {
    "mindmap": """Analyze the provided sources and generate a comprehensive hierarchical Mind Map structure.
Output strictly valid JSON with this structure:
{{
  "title": "Central Theme",
  "children": [
    {{
      "title": "Main Category 1",
      "children": [
        {{ "title": "Subtopic A", "notes": "Brief explanation" }},
        {{ "title": "Subtopic B", "notes": "Brief explanation" }}
      ]
    }},
    {{
      "title": "Main Category 2",
      "children": [
        {{ "title": "Subtopic C", "notes": "Brief explanation" }}
      ]
    }}
  ]
}}
Ensure it captures all critical concepts, frameworks, and details from the sources. Output ONLY the JSON block.
Language: {lang}
Sources:
{sources_context}
""",

    "briefing": """Create an Executive Briefing Document based on the provided sources.
Structure the document with:
1. Executive Summary (Key Takeaways)
2. Background & Strategic Context
3. Core Findings & Key Pillars
4. Risks, Opportunities & Considerations
5. Actionable Next Steps / Recommendations

Language: {lang}
Sources:
{sources_context}
""",

    "study_guide": """Create a Comprehensive Study Guide based on the provided sources.
Structure the document with:
1. Core Concepts & Glossary (Key definitions)
2. Main Themes & Structural Breakdown
3. Critical Insights & Key Formulas/Theorems (if any)
4. Synthesis Questions for Review & Reflection
5. Practical Real-World Applications

Language: {lang}
Sources:
{sources_context}
""",

    "faq": """Generate a high-value Frequently Asked Questions (FAQ) guide based on the provided sources.
Extract 6 to 10 of the most critical questions a researcher, executive, or student would ask.
For each question, provide a detailed, source-grounded answer.

Format:
### Q1: [Question]
**Answer**: [Detailed source-backed answer]

Language: {lang}
Sources:
{sources_context}
""",

    "timeline": """Extract and generate a chronological Timeline of events, milestones, or progression described in the sources.
Format each milestone as:
- **[Time / Period / Phase]**: [Event Description and significance]

Language: {lang}
Sources:
{sources_context}
""",

    "quiz": """Create an interactive Quiz and Knowledge Check based on the provided sources.
Generate 5 Multiple Choice Questions (with options A, B, C, D, the correct answer, and detailed explanation)
and 3 Open Discussion/Essay Questions.

Format:
### Multiple Choice Questions
1. [Question]
   - A) [Option]
   - B) [Option]
   - C) [Option]
   - D) [Option]
   *Correct Answer*: [Key]
   *Explanation*: [Why]

### Open Discussion Questions
1. [Question]
   *Key Points to Consider*: [Points]

Language: {lang}
Sources:
{sources_context}
""",

    "flashcards": """Create a set of Active Recall Flashcards based on the provided sources.
Output strictly valid JSON with this structure:
{{
  "flashcards": [
    {{
      "question": "Front of card: Question or Concept",
      "answer": "Back of card: Clear, concise explanation or definition",
      "category": "Topic category"
    }}
  ]
}}
Generate between 6 to 12 high-impact flashcards. Output ONLY the JSON.
Language: {lang}
Sources:
{sources_context}
""",

    "presentation": """Create a structured Presentation Slide Deck Outline based on the provided sources.
Generate 6 to 10 slides.
Output strictly valid JSON with this structure:
{{
  "title": "Presentation Title",
  "subtitle": "Subtitle / Theme",
  "slides": [
    {{
      "slide_number": 1,
      "title": "Slide Title",
      "bullets": ["Key bullet 1", "Key bullet 2", "Key bullet 3"],
      "speaker_notes": "What the presenter should say"
    }}
  ]
}}
Output ONLY the JSON.
Language: {lang}
Sources:
{sources_context}
"""
}

# Podcast / Audio Overview prompts for the 4 Google NotebookLM formats
PODCAST_PROMPTS = {
    "deep_dive": """You are an elite podcast writer producing a top-tier "Deep Dive" audio overview (benchmarking Google NotebookLM).
Two lively, knowledgeable AI hosts (Host A: curious, insightful, and enthusiastic; Host B: analytical, thoughtful, and structured) discuss the uploaded materials.

Format Requirements:
1. Energetic, natural conversational dialogue with verbal nods, humor, insightful questions, and genuine reactions.
2. Cover the main themes, surprising insights, and practical takeaways from the sources.
3. Duration mode: {duration_mode} ({duration_instruction}).
4. User Guidance Note: {guidance}
5. Output format MUST be strictly a JSON list of dialogue turns:
[
  {{"speaker": "{speaker_a}", "text": "Welcome back! Today we are diving into..."}},
  {{"speaker": "{speaker_b}", "text": "Yeah, and what struck me immediately was..."}}
]
Language: {lang}
Sources:
{sources_context}
""",

    "brief": """You are a podcast writer producing "The Brief" (benchmarking Google NotebookLM's 1-2 minute rapid executive summary).
A single articulate, authoritative AI host delivers a concise, punchy overview of the most critical findings.

Format Requirements:
1. Fast-paced, zero filler, highly structured.
2. Summarize the 3 most crucial takeaways and conclusions.
3. Output format MUST be strictly a JSON list of dialogue turns:
[
  {{"speaker": "{speaker_a}", "text": "Here is your rapid brief on..."}}
]
Language: {lang}
Sources:
{sources_context}
""",

    "critique": """You are a podcast writer producing "The Critique" audio overview (benchmarking Google NotebookLM).
An expert reviewer and intellectual challenger rigorously scrutinizes the source material.

Format Requirements:
1. Constructive skepticism, analytical rigor, examining assumptions, identifying potential limitations, blind spots, and unanswered questions.
2. Two speakers (Reviewer & Facilitator) or solo expert.
3. Output format MUST be strictly a JSON list of dialogue turns:
[
  {{"speaker": "{speaker_a}", "text": "Let us take a hard, critical look at..."}},
  {{"speaker": "{speaker_b}", "text": "Right, because on the surface it seems sound, but look at the assumptions..."}}
]
Language: {lang}
Sources:
{sources_context}
""",

    "debate": """You are a podcast writer producing "The Debate" audio overview (benchmarking Google NotebookLM).
Two intellectual heavyweights debate the opposing sides, controversies, or trade-offs present in the source materials.

Format Requirements:
1. Respectful but spirited debate: Speaker A defends Proposition/Optimistic stance; Speaker B defends Counter-proposition/Cautious stance.
2. Grounded in source data, citing specific evidence from the text.
3. Output format MUST be strictly a JSON list of dialogue turns:
[
  {{"speaker": "{speaker_a}", "text": "The potential here is undeniable..."}},
  {{"speaker": "{speaker_b}", "text": "Hold on, we cannot ignore the significant risks..."}}
]
Language: {lang}
Sources:
{sources_context}
"""
}
