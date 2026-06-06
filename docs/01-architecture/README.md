# Architecture Documentation

This directory is the authority for Skill Forge architecture.

## Purpose

Use this directory to describe how Skill Forge is structured, how modules interact, and what architectural boundaries must be preserved during future changes.

## What Belongs Here

- Architecture overview
- Module boundary definitions
- CLI-to-service flow
- Skill generation pipeline
- Validation pipeline
- Storage and provenance contracts
- Platform adapter boundaries
- Architecture decision records

## Recommended Files

- `architecture-overview.md`
- `module-boundaries.md`
- `data-flow.md`
- `storage-contracts.md`
- `cli-architecture.md`
- `validation-architecture.md`
- `adr/`

## What Does Not Belong Here

- Temporary implementation plans
- Phase execution reports
- OpenSpec change artifacts
- Agent workflow rules
- User-facing README content

## Current Rule

Architecture documents in this directory are current authority. Historical architecture drafts should be moved to `../99-archive/` only through a separate cleanup change.
