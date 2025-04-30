# writing-enhancement-team

## Overview

**writing-enhancement-team** is a modular LLM-based agent system designed to automatically assess and enhance the quality of written content. It provides an automated pipeline that evaluates user-provided texts, generates targeted improvement suggestions, and applies those improvements to deliver a refined version of the original content.

This project is useful for any application requiring high-quality text production, including content writing, documentation review, AI-generated text validation, and more.

---

## Architecture

The system is composed of two specialized agents:

### 🧠 TextReviewer

**Role**: Evaluates a given text and produces structured improvement suggestions.

- **Responsibilities**:
  - Assess grammar, clarity, tone, structure, and coherence
  - Identify weak or ambiguous phrasing
  - Suggest enhancements for readability and style
  - Output actionable suggestions in a standardized format

- **Input**: Raw user-provided text or text from another agent  
- **Output**: A list of structured suggestions and evaluation notes

---

### ✍️ TextRewriter

**Role**: Applies the suggestions provided by `text_reviewer` agent to improve the original text.

- **Responsibilities**:
  - Rewrite or refine sentences based on the review feedback
  - Ensure the meaning and intent are preserved
  - Produce a clean, coherent, and polished output

- **Input**: Original text + suggestions from `text_reviewer`  
- **Output**: Enhanced version of the original text

---

## Workflow

1. **Input a text** into the pipeline.
2. **TextReviewer** analyzes it and produces detailed suggestions.
3. **TextRewriter** receives both the original text and the suggestions, then rewrites the content accordingly.
4. **Final output** is a polished and improved version of the original input.

