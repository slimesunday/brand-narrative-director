# Brand Narrative Director

A Streamlit app that collects brand data through a guided wizard and generates narrative concepts + full storyboards for 10-12 second brand messaging videos, powered by Claude.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

## Run

```bash
streamlit run brand_narrative_app.py
```

## What It Does

**7-Step Wizard:**
1. **Brand Identity** — Name, URL, category, description + auto-research via LLM
2. **Audience** — Psychographic profile, adjacent brands, platform selection
3. **Brand Personality** — 6 spectrum sliders (Exclusive↔Accessible, Serious↔Playful, etc.)
4. **Emotional Territory** — Desired feeling, rejected feeling, movie scene metaphor
5. **Visual Direction** — Style picker (12 options), color palette, production parameters
6. **Review** — Complete brand profile with auto-classified maturity mode (Discovery/Amplification/Evolution)
7. **Generate** — 3 narrative concepts → select one → full storyboard with keyframe + animation prompts

**Output:** Pipeline-ready JSON containing:
- Brand profile
- Selected narrative concept (with human truth / insight)
- 5 keyframe descriptions with camera, lighting, composition, emotion
- 5 NanoBanana Pro image generation prompts (with consistent style suffix)
- 4 Veo 3.1 animation/transition prompts
- Creative director notes

## Architecture

- The app uses `brand_narrative_system_prompt.md` as the system prompt for narrative generation
- Brand maturity is auto-classified based on data density (Discovery → Amplification → Evolution)
- If the Anthropic API is unavailable, the app falls back to demo concepts for UI testing
- The JSON export is designed to pipe directly into the NanoBanana Pro → Veo 3.1 pipeline

## File Structure

```
brand_narrative_app.py          # Main Streamlit app
brand_narrative_system_prompt.md # System prompt for the narrative LLM
requirements.txt                 # Python dependencies
```
