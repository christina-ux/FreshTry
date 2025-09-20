# IC Agent Packs: Non‑Content Signal Monitor & AI Job Market Radar

This repository contains two configurable agent packs designed to run on serverless platforms (e.g., Vercel Edge Functions) that monitor complex phenomena without exposing private data. Each pack includes training summaries, trip‑wire definitions, crosswalks between observations and actions, data points to collect, operational instructions and example prompts. They can be deployed as stand‑alone modules or combined within a larger orchestration framework.

## Overview

1. **Non‑Content Signal Monitor (IC_Attention_Surface_v1)** – focuses on non‑verbal and non‑semantic aspects of communication. It measures timing patterns, structural features of messages, physiological responses and environmental cues to infer agitation, coercion or optimal cognitive states. The underlying theory draws on *entrainment*, the tendency of interacting systems to synchronise rhythms. By quantifying subtle shifts, the agent can surface covert manipulation and suggest calibrated interventions (e.g. boundary scripts, breathing resets, clarity windows).

2. **AI Job Market Radar** – analyses labour‑market disruptions caused by rapid artificial‑intelligence adoption. It synthesises trends across unemployment statistics, sectoral shifts, hiring intentions, wage and productivity data, policy responses and public sentiment. The agent functions as a self‑evolving monitor, updating predictive models as new data arrives and issuing alerts when thresholds or correlations suggest accelerating displacement. It emphasises evidence‑backed insights and rejects hype or unfounded claims.

## Conceptual Foundations

### Non‑Content Signals and Entrainment

Humans convey intent through more than words. Micro‑timing (latency between messages, punctuation runs, emoji density), conversational structure (question stacking, urgency tokens), physiological responses (exhale length, shoulder shrug rate), energy economics (context switching, recovery time) and environmental factors (ambient light, sound and caffeine) all provide objective windows into underlying cognitive and emotional states. These non‑content signals are governed by **entrainment**, a phenomenon whereby independent rhythmic processes synchronise through interaction. When entrainment patterns break (e.g. a 1.5σ shift in response latency or a 25 % drop in the Somatic Anchor Drift Index), it often signals agitation, coercion or boundary violations.

### AI‑Driven Labour Disruption

Artificial intelligence is transforming the labour market. Highly exposed white‑collar occupations are experiencing elevated unemployment, while new roles have not yet materialised at scale. Entry‑level career ladders are collapsing, leaving young workers without traditional on‑ramps. Policy‑driven sectoral shifts create winners (defence, fossil fuels, infrastructure) and losers (renewables, certain tech sectors), amplifying regional disparities. Safety nets and retraining programmes lag behind the pace of disruption. The gains from AI accrue to a narrow set of stakeholders, increasing inequality and social strain. Monitoring these dynamics requires tracking a broad set of indicators (unemployment rates by occupation and age, AI adoption, job cuts, wages and productivity, policy changes, public sentiment) and updating predictive models as new information emerges.

## Repository Structure

```
ic_agent_packs/
├── README.md                 ← this overview
├── non_content_signals_agent.json  ← configuration for the non‑content signal monitor
├── ai_job_market_agent.json        ← configuration for the AI job market radar
```

Each JSON file contains keys for `name`, `description`, `training`, `trip_wires`, `crosswalks`, `data_points`, `instructions` and `prompts`. These are intended to be loaded by your orchestration layer and executed within serverless functions or long‑running agents. Modify thresholds, metrics or prompts as appropriate for your deployment.