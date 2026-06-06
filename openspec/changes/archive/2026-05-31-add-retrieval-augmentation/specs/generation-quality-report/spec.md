## ADDED Requirements

### Requirement: Quality metrics support RAG comparison
The system SHALL expose deterministic content quality metrics that allow LLM-assisted generation with retrieval context to be compared against LLM-assisted generation without retrieval context.

#### Scenario: Compare with and without retrieval context
- **WHEN** the same requirement is generated through LLM-assisted generation with retrieval context and without retrieval context
- **THEN** both generated packages SHALL expose workflow specificity, constraint verifiability, and quality gate clarity metrics
- **AND** those metrics SHALL be usable to compare whether retrieval augmentation improved content quality

#### Scenario: RAG does not change validation scoring rules
- **WHEN** a generated package was created with retrieval augmentation
- **THEN** the generation quality report SHALL use the same validation status and deterministic score calculation rules used by non-RAG generation
