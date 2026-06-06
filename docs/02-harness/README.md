# AI Harness Documentation

This directory defines the project-level AI Harness rules for Skill Forge.

## Purpose

Use this directory to define how AI agents should work in this repository. These rules constrain Codex, Claude Code, opencode, and any other implementation or planning agent.

## What Belongs Here

- Agent workflow rules
- Coding standards for AI-generated changes
- Verification policy
- Context ingestion policy
- Modification scope rules
- Evidence recording rules
- Checklist for implementation agents

## Recommended Files

- `harness-overview.md`
- `agent-workflow.md`
- `coding-standards.md`
- `verification-policy.md`
- `context-ingestion-policy.md`
- `checklist.md`

## What Does Not Belong Here

- Product roadmap
- OpenSpec schema files
- Superpowers skill explanations
- Business domain rules
- Runtime troubleshooting notes

## Current Rule

Harness rules are mandatory for non-trivial AI-assisted changes. If a rule conflicts with a one-off prompt, the repository rule wins unless the user explicitly overrides it.
