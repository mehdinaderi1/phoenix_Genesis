# V5 Contract Authority Decision

## Status

Accepted

## Scope

This decision establishes the authoritative contracts identified during
the V5 Architecture / Contract Audit.

The purpose is to distinguish active runtime contracts from secondary
bounded-context contracts and legacy/orphan implementations before
any refactoring, deletion, rename, or merge is performed.

---

## Evidence Baseline

Architecture Chain Record:

docs/architecture/architecture_chain_record.md

Baseline verification:

612 tests passed

Architecture audit checkpoint:

eebf7a1

Canonical chain baseline commit:

7d7cf28

---

# Contract Authority Matrix

| Contract | Implementation | Runtime Role | Tests | Classification |
|---|---|---|---|---|
| ExperienceRecord | intelligence.experience_record.ExperienceRecord | Core Intelligence Runtime | Active core flow coverage | LIVE / CORE |
| ExperienceRecord | intelligence.learning.experience_record.ExperienceRecord | Isolated learning subsystem | test_experience_engine.py, test_pattern_detector.py | LEGACY / TEST-BACKED |
| MetaLearningEngine | intelligence.meta.meta_learning_engine.MetaLearningEngine | Core Meta Runtime | test_meta_learning_engine_v2.py, test_meta_learning_feedback_contract.py | LIVE / CORE |
| MetaLearningEngine | intelligence.learning.meta_learning_engine.MetaLearningEngine | Strategy Meta Runtime | test_meta_learning_engine.py, test_meta_learning_flow.py | LIVE / SECONDARY |
| MetaLearning | intelligence.meta.meta_learning.MetaLearning | No active runtime consumer found | test_meta_learning.py | LEGACY / TEST-BACKED |

---

# Evidence

## ExperienceRecord — Core

The authoritative ExperienceRecord is:

intelligence.experience_record.ExperienceRecord

It is consumed by:

- intelligence.memory.experience_memory.ExperienceMemory
- intelligence.performance_learning_adapter.PerformanceLearningAdapter

It is part of the IntelligenceComponents composition root and is
referenced by IntelligenceFlow.

Runtime identity verification established that:

f.experience_memory is f.components.experience_memory

Therefore the core ExperienceMemory contract is owned by the active
composition root.

---

## ExperienceRecord — Legacy

The following implementation exists:

intelligence.learning.experience_record.ExperienceRecord

It is consumed by:

- intelligence.learning.experience_engine.ExperienceEngine
- intelligence.learning.pattern_detector.PatternDetector

However:

- ExperienceEngine is not composed by IntelligenceComponents
- ExperienceEngine is not composed by IntelligenceFlow
- PatternDetector is not composed by IntelligenceComponents
- PatternDetector is not composed by IntelligenceFlow
- Active contract tests exist:
  - tests/test_experience_engine.py
  - tests/test_pattern_detector.py

These tests preserve the isolated learning contract, but no active
composition-root or IntelligenceFlow runtime path was found.

Therefore this implementation is classified as LEGACY / TEST-BACKED.

No deletion is implied by this decision.

---

## MetaLearningEngine — Core

The authoritative Core MetaLearningEngine is:

intelligence.meta.meta_learning_engine.MetaLearningEngine

Contract:

learn(meta_insight)

Its role is:

MetaInsight
? MetaLearningEngine.learn()
? confidence adjustment

It is instantiated by IntelligenceComponents and therefore belongs to
the Core Meta Runtime.

Relevant tests include:

- tests/test_meta_learning_engine_v2.py
- tests/test_meta_learning_feedback_contract.py

Classification:

LIVE / CORE

---

## MetaLearningEngine — Strategy Secondary Context

A second implementation exists:

intelligence.learning.meta_learning_engine.MetaLearningEngine

Its contract is:

analyze(knowledge)

It produces:

MetaLearningInsight

Its runtime path is:

Strategy Context
? MetaLearningFlow
? learning.MetaLearningEngine
? MetaLearningInsight
? EnhancedStrategyContext

Relevant tests include:

- tests/test_meta_learning_engine.py
- tests/test_meta_learning_flow.py

This is not considered a duplicate of the Core MetaLearningEngine.

It belongs to a different bounded context and therefore remains:

LIVE / SECONDARY

---

## MetaLearning — Legacy / Test-Backed

The following implementation exists:

intelligence.meta.meta_learning.MetaLearning

Its contract is:

analyze(meta_insight)

Evidence discovery found:

- no active runtime consumer
- no IntelligenceComponents composition
- no IntelligenceFlow composition
- active contract coverage in tests/test_meta_learning.py

The test preserves the historical MetaLearning behavior, but no active
composition-root or IntelligenceFlow runtime path was found.

Therefore it is classified as:

LEGACY / TEST-BACKED

No deletion is implied by this decision.

---

# Architecture Rules

## Rule 1 — Same Name Does Not Mean Same Contract

Two classes with the same name must not be merged solely because their
class names match.

Contract identity is determined by:

- input type
- output type
- behavior
- runtime ownership
- consumers
- bounded context
- tests

---

## Rule 2 — Runtime Authority Overrides File Similarity

A contract instantiated through the active composition root and consumed
by the active runtime has architectural authority over an equivalent
unused implementation.

---

## Rule 3 — Secondary Live Contracts Must Be Preserved

A contract classified as LIVE / SECONDARY is not legacy merely because
it is outside the Core Runtime.

Secondary bounded contexts remain valid architectural contracts when
their runtime path and tests establish active usage.

---

## Rule 4 — Legacy Does Not Mean Delete Immediately

Legacy classification establishes that an implementation is outside the
current authoritative runtime contract.

Deletion, archival, migration, or replacement requires a separate
decision and evidence.

---

## Rule 5 — Test-Backed Does Not Mean Runtime-Live

A contract may retain active regression coverage while remaining outside
the authoritative runtime composition.

Tests establish preserved behavior.

Runtime authority requires evidence of active composition, ownership,
and execution through the current architecture.

Therefore:

TEST-BACKED != RUNTIME-LIVE

---
# Freeze Decision

The following contracts are frozen as authoritative for V5:

LIVE / CORE:

- intelligence.experience_record.ExperienceRecord
- intelligence.meta.meta_learning_engine.MetaLearningEngine

LIVE / SECONDARY:

- intelligence.learning.meta_learning_engine.MetaLearningEngine

LEGACY:

- intelligence.learning.experience_record.ExperienceRecord — TEST-BACKED
- intelligence.meta.meta_learning.MetaLearning — TEST-BACKED

---

# Refactoring Constraint

Until a separate migration decision is approved:

- Do not delete legacy implementations.
- Do not merge the two MetaLearningEngine implementations.
- Do not merge the two ExperienceRecord implementations.
- Do not rename active contracts.
- Do not change active imports merely for structural cleanup.

Any migration must preserve the active architecture chain and pass the
full regression suite.

---

# Next Phase

V5 Contract Authority
-> Legacy Isolation
-> Contract Freeze
-> Contract Tests
-> Runtime Architecture Verification
-> V5 Learning AI Implementation

