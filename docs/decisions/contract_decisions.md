# Phoenix Genesis — Contract Decisions

## 1. Purpose

This document is the authoritative ledger for Phoenix Genesis contract
classification decisions.

It records:

* Live runtime contracts
* Secondary contracts
* Legacy candidates
* Duplicate contract situations
* Contract ownership
* Contract authority
* Migration decisions
* Explicit non-deletion decisions
* Future validation requirements

This document must not be treated as a class inventory.

Its purpose is to preserve architectural decisions.

توضیح فارسی:

این فایل مرجع رسمی تصمیم‌های Contract در ققنوس است.

هدف آن ثبت این است که کدام Contract واقعاً در Runtime زنده است، کدام Contract ثانویه است، کدام مورد Legacy Candidate است و برای موارد مشابه چه تصمیمی گرفته شده است.

---

# 2. Contract Decision Principles

The following rules govern all contract decisions.

### Rule 1 — Runtime Beats Appearance

Actual runtime usage has higher authority than:

* filename similarity
* class name similarity
* directory location
* implementation age
* visual architecture assumptions

توضیح فارسی:

ملاک اصلی زنده بودن یک Contract، استفاده واقعی در Runtime است.

نام فایل یا محل قرارگیری Class به تنهایی تعیین‌کننده نیست.

---

### Rule 2 — Tests Are Evidence, Not Sole Authority

Tests provide evidence of contract usage.

Tests alone do not prove that a contract is the primary runtime contract.

توضیح فارسی:

Testها شواهد مهمی هستند، اما صرف داشتن Test برای یک Contract به معنی Live بودن آن نیست.

---

### Rule 3 — Producer → Consumer Defines the Contract

A contract is understood through:

Producer
→ Transformation
→ Contract
→ Consumer

توضیح فارسی:

برای تعیین Contract باید مسیر واقعی تولید داده تا مصرف آن بررسی شود.

---

### Rule 4 — No Destructive Cleanup Before Classification

No duplicate contract may be:

* deleted
* merged
* renamed
* replaced

until its runtime dependency and consumer graph have been classified.

توضیح فارسی:

هیچ Contract تکراری قبل از تعیین دقیق Live یا Legacy نباید حذف، Merge، Rename یا Replace شود.

---

### Rule 5 — Preserve State Identity

When a contract belongs to a stateful component, object identity must be
preserved whenever downstream behavior depends on shared state.

توضیح فارسی:

در Componentهای Stateful، فقط یکسان بودن Configuration کافی نیست.

در صورت نیاز معماری باید همان Instance مشترک حفظ شود.

---

# 3. Classification Vocabulary

## LIVE

A contract actively used by the current runtime architecture.

توضیح فارسی:

Contract فعال و مورد استفاده در مسیر اصلی Runtime.

---

## SECONDARY

A valid contract used by a secondary subsystem or parallel path.

توضیح فارسی:

Contract معتبر ولی خارج از مسیر اصلی Runtime یا متعلق به یک Subsystem ثانویه.

---

## LEGACY CANDIDATE

A contract with evidence of historical or isolated usage, but whose future
status has not yet been finalized.

توضیح فارسی:

Contractی که احتمال Legacy بودن آن وجود دارد، اما هنوز تصمیم نهایی برای حذف یا Migration آن گرفته نشده است.

---

## FROZEN

A contract whose architectural role has been explicitly accepted and
should not be changed without a new architecture decision.

توضیح فارسی:

Contractی که نقش معماری آن تثبیت شده و تغییر آن نیازمند تصمیم معماری جدید است.

---

# 4. Live Contract Ledger

| Contract                   | Location                                                    | Classification | Authority                 | Reason                                           |
| -------------------------- | ----------------------------------------------------------- | -------------- | ------------------------- | ------------------------------------------------ |
| ExperienceRecord           | `intelligence.experience_record.ExperienceRecord`           | LIVE           | Core Runtime              | Used by the main experience-learning path        |
| MetaLearningEngine         | `intelligence.meta.meta_learning_engine.MetaLearningEngine` | LIVE           | Runtime Meta Intelligence | Used by the active meta-learning runtime path    |
| StrategyRanker             | `intelligence.learning.strategy_ranker.StrategyRanker`      | LIVE           | Current Runtime Ranking   | Used by the active strategy ranking path         |
| DecisionRecord             | `DecisionRecord` runtime contract                           | LIVE           | Decision Pipeline         | Core decision representation                     |
| OutcomeRecord              | `OutcomeRecord` runtime contract                            | LIVE           | Outcome Layer             | Represents realized outcome                      |
| PerformanceLearningAdapter | `PerformanceLearningAdapter`                                | LIVE           | Learning Boundary         | Converts performance information into experience |
| ExperienceMemory           | `ExperienceMemory`                                          | LIVE           | Experience Layer          | Runtime experience storage boundary              |
| PatternIntelligence        | `PatternIntelligence`                                       | LIVE           | Pattern Layer             | Runtime pattern intelligence                     |
| StrategyLearner            | `StrategyLearner`                                           | LIVE           | Strategy Learning         | Produces learned strategy knowledge              |
| StrategyMemory             | `StrategyMemory`                                            | LIVE           | Strategy Storage          | Stores learned strategy knowledge                |
| StrategyRecall             | `StrategyRecall`                                            | LIVE           | Strategy Retrieval        | Retrieves candidate strategies                   |
| StrategySelector           | `StrategySelector`                                          | LIVE           | Decision Selection        | Selects champion strategy                        |
| DecisionRules              | `DecisionRules`                                             | LIVE           | Decision Gate             | Existing validation gate                         |

توضیح فارسی:

این جدول Contractهای اصلی فعلی را ثبت می‌کند.

سه مورد Duplicate یعنی ExperienceRecord، MetaLearningEngine و StrategyRanker در این مرحله به صورت جداگانه در بخش‌های بعدی ثبت می‌شوند.

---

# 5. ExperienceRecord Contract Decision

## Primary Contract

`intelligence.experience_record.ExperienceRecord`

Classification:

LIVE

Dependency chain:

PerformanceLearningAdapter
→ ExperienceRecord
→ ExperienceMemory
→ PatternIntelligence
→ StrategyLearner

توضیح فارسی:

این ExperienceRecord Contract اصلی مسیر Core Runtime است.

به همین دلیل در حال حاضر Contract مرجع Experience در معماری اصلی محسوب می‌شود.

---

## Secondary Contract

`intelligence.learning.experience_record.ExperienceRecord`

Classification:

SECONDARY / LEGACY CANDIDATE

Known consumers:

`learning/experience_engine.py`

`learning/pattern_detector.py`

Decision:

DO NOT DELETE

DO NOT MERGE YET

DO NOT RENAME YET

Required next action:

Audit the complete learning subsystem dependency graph.

توضیح فارسی:

این نسخه هنوز حذف یا Merge نمی‌شود.

ابتدا باید مشخص شود که Learning Subsystem هنوز یک مسیر معتبر و مستقل دارد یا این Contract صرفاً باقی‌مانده معماری قبلی است.

---

# 6. MetaLearningEngine Contract Decision

## Primary Contract

`intelligence.meta.meta_learning_engine.MetaLearningEngine`

Classification:

LIVE

Primary runtime contract:

`learn(meta_insight)`

Runtime output includes:

* confidence adjustment
* reliability

Dependency chain:

MetaIntelligence
→ MetaInsight
→ MetaLearningEngine
→ Confidence Adjustment
→ IntelligenceFlow

توضیح فارسی:

این نسخه MetaLearningEngine Contract فعال Meta Runtime است.

---

## Secondary Contract

`intelligence.learning.meta_learning_engine.MetaLearningEngine`

Classification:

SECONDARY / LEGACY CANDIDATE

Decision:

DO NOT DELETE

DO NOT MERGE YET

Required next action:

Audit MetaLearningFlow and all consumers of the learning namespace.

توضیح فارسی:

نسخه Learning Contract متفاوتی دارد و فعلاً نباید با نسخه Runtime یکی شود.

---

# 7. StrategyRanker Contract Decision

## Primary Runtime Contract

`intelligence.learning.strategy_ranker.StrategyRanker`

Classification:

LIVE

Current role:

Runtime strategy ranking.

Dependency:

StrategyRecall
→ StrategyRanker
→ StrategySelector

توضیح فارسی:

این نسخه در مسیر فعلی Runtime Ranking استفاده می‌شود.

---

## Alternate Contract

`intelligence.strategy_ranker.StrategyRanker`

Classification:

SECONDARY

Known distinction:

The root implementation exposes a richer ranking-result contract.

Decision:

DO NOT MERGE YET

Required next action:

Compare:

* constructor contract
* input contract
* ranking algorithm
* output contract
* consumers
* tests
* runtime construction path

توضیح فارسی:

دو StrategyRanker صرفاً Duplicate اسمی نیستند.

قرارداد خروجی آنها متفاوت است، بنابراین Merge بدون بررسی Producer و Consumer خطرناک است.

---

# 8. DecisionRecord Contract

Classification:

LIVE

Role:

Primary decision representation.

Primary dependency chain:

Decision Engine
→ DecisionRecord
→ Decision Validation
→ Action Proposal
→ Decision Memory
→ Outcome Processing

Learning dependency:

DecisionRecord
→ DecisionOutcomeBridge
→ OutcomeRecord
→ Performance Learning

توضیح فارسی:

DecisionRecord یکی از مهم‌ترین Contractهای بالادستی سیستم است.

هر تغییر در آن باید Consumerهای مستقیم و غیرمستقیم آن را بررسی کند.

---

# 9. OutcomeRecord Contract

Classification:

LIVE

Role:

Market reality / realized outcome representation.

Dependency:

DecisionRecord
→ DecisionOutcomeBridge
→ OutcomeRecord
→ Performance Processing

Architectural rule:

Decision and Outcome are separate semantic contracts.

توضیح فارسی:

OutcomeRecord نماینده نتیجه تحقق‌یافته است.

نباید DecisionRecord و OutcomeRecord به یک Contract واحد تبدیل شوند.

---

# 10. PerformanceLearningAdapter Contract

Classification:

LIVE

Role:

Learning boundary between performance information and experience.

Dependency:

Performance
→ PerformanceLearningAdapter
→ ExperienceRecord

Required contextual information includes:

* decision context
* strategy identity
* outcome
* confidence
* risk context

توضیح فارسی:

این Adapter مرز تبدیل Performance به Experience است.

اطلاعات Contextual تصمیم باید در این تبدیل از بین نرود.

---

# 11. Strategy Identity Contract

Strategy identity must remain stable across:

StrategyLearner
→ StrategyMemory
→ StrategyRecall
→ StrategyRanker
→ StrategySelector

Classification:

LIVE ARCHITECTURAL RULE

Compatibility layer:

StrategyBridge

توضیح فارسی:

Identity Strategy یک Contract مستقل در سطح معماری است.

نباید در مسیر Learning تا Selection تغییر یا شکسته شود.

---

# 12. Decision Gate Contract

Primary gate:

`DecisionRules`

Classification:

LIVE

Known methods:

`can_long(report)`

`can_short(report)`

`strategy_is_valid(report)`

Dependency:

Champion Strategy
→ DecisionRules
→ Decision Gate

Decision:

REUSE EXISTING GATE

DO NOT CREATE PARALLEL GATE

توضیح فارسی:

Gate فعلی در DecisionRules قرار دارد و باید Reuse شود.

ساخت Gate موازی بدون نیاز معماری مشخص باعث دوگانگی تصمیم‌گیری خواهد شد.

---

# 13. Governance Contract Decisions

## GovernanceMemory

Classification:

LIVE

Role:

Governance state/history.

---

## GovernanceEvolutionMemory

Classification:

LIVE / SEPARATE CONTRACT

Role:

Evolution-specific governance memory.

Decision:

KEEP SEPARATE

توضیح فارسی:

این دو Memory Contractهای متفاوتی هستند.

نباید به دلیل شباهت نام یا حوزه فعالیت، Merge شوند.

---

# 14. Governance Shared State Decision

Verified dependency:

GovernanceMemory
→ GovernanceRecallFlow
→ GovernanceIntelligentGate

Decision:

PRESERVE SHARED INSTANCE

توضیح فارسی:

در جایی که Governance State باید مشترک باشد، همان Instance از GovernanceMemory باید بین Consumerها حفظ شود.

---

# 15. Meta Confidence Contract

## Meta Contract Decisions

### Runtime MetaLearningEngine

```text
intelligence.meta.meta_learning_engine.MetaLearningEngine
→ LIVE
```

توضیح فارسی:

این Contract توسط Composition Root ساخته می‌شود و IntelligenceFlow از همان Instance Runtime استفاده می‌کند.

### Learning MetaLearningEngine

```text
intelligence.learning.meta_learning_engine.MetaLearningEngine
→ SECONDARY / ACTIVE STRATEGY INTELLIGENCE PATH
```

توضیح فارسی:

این Contract توسط MetaLearningFlow در مسیر Strategy Intelligence مصرف می‌شود. این Contract obsolete محسوب نمی‌شود و نباید با Runtime MetaLearningEngine ادغام شود.

### MetaLearning

```text
intelligence.meta.meta_learning.MetaLearning
→ SECONDARY / TEST-BACKED CONTRACT
```

توضیح فارسی:

این Contract در Runtime اصلی استفاده نمی‌شود، اما توسط تست‌ها و Contract موجود پشتیبانی می‌شود. بنابراین فعلاً Legacy محسوب نمی‌شود.

### MetaInsight

```text
MetaInsight
→ LIVE
```

توضیح فارسی:

MetaInsight Contract مشترک بین تولیدکننده و مصرف‌کنندگان Meta Intelligence است.

### MetaLearningInsight

```text
MetaLearningInsight
→ LIVE WITHIN SECONDARY STRATEGY META PATH
```

توضیح فارسی:

این Contract خروجی learning.MetaLearningEngine است و در EnhancedStrategyContext مصرف می‌شود.

### EnhancedStrategyContext

```text
EnhancedStrategyContext
→ LIVE WITHIN SECONDARY STRATEGY META PATH
```

توضیح فارسی:

این Contract حامل نتیجه Meta Learning در مسیر Strategy Intelligence است.

### MetaLearningFlow

```text
MetaLearningFlow
→ LIVE SECONDARY
```

توضیح فارسی:

این Flow فعال است اما بخشی از مسیر اصلی Runtime Meta Learning نیست.

### Canonical Meta Runtime Chain

```text
DecisionMemory
→ MetaIntelligence
→ MetaInsight
→ MetaLearningEngine.learn()
→ Meta Learning Result
→ MetaConfidenceAdapter
→ Adjusted Decision Confidence
→ Next Decision
```

### Canonical Strategy Meta Chain

```text
Strategy Context
→ StrategyIntelligenceService
→ MetaLearningFlow
→ learning.MetaLearningEngine.analyze()
→ MetaLearningInsight
→ EnhancedStrategyContext
→ Strategy Intelligence
```

### Meta Confidence Contract

```text
Meta Learning Result
→ MetaConfidenceAdapter
→ report.confidence
```

توضیح فارسی:

این مسیر Contract واقعی Confidence Adjustment است. Meta Learning Result مستقیماً Adaptive Decision Context تولید نمی‌کند.

### Contract Freeze Decision

```text
NO DELETE
NO MERGE
NO RENAME
NO MIGRATION
```

توضیح فارسی:

تا زمانی که V5 Contract Boundary تعریف و تأیید نشده است، هیچ Contract موازی حذف، ادغام، تغییر نام یا مهاجرت داده نمی‌شود.

### Contract Authority

```text
Runtime Composition
→ Runtime Consumer
→ Producer
→ Contract
→ Tests
→ Historical / Structural Evidence
```

توضیح فارسی:

این ترتیب مرجع نهایی تعیین Live، Secondary و Legacy Candidate است.

---

# 16. Adaptive Context Timing Decision

Current architecture:

Previous Knowledge
→ Adaptive Context
→ Current Decision

Current-cycle learning:

Current Decision
→ Outcome
→ Performance
→ Experience
→ Pattern
→ Meta Learning

Classification:

KNOWN ARCHITECTURAL DEBT

Decision:

DO NOT REFACTOR DURING CONTRACT FREEZE

توضیح فارسی:

در حال حاضر Adaptive Context پیش از تکمیل Learning همان چرخه ساخته می‌شود.

این Debt ثبت شده ولی در مرحله Contract Freeze نباید برای اصلاح آن Refactor گسترده انجام شود.

---

# 17. Synthetic Outcome Decision

Current observation:

Some outcome-related values remain synthetic.

Classification:

KNOWN ARCHITECTURAL DEBT

Decision:

DOCUMENT

DO NOT HIDE

DO NOT REDEFINE OUTCOME CONTRACT

Future boundary:

Real market outcome integration.

توضیح فارسی:

برخی مقادیر Outcome هنوز Synthetic هستند.

این مسئله باید شفاف ثبت شود، اما نباید با تغییر تعریف OutcomeRecord پنهان شود.

---

# 18. Duplicate Contract Policy

Known duplicate contract groups:

### Group A

`intelligence.experience_record.ExperienceRecord`

`intelligence.learning.experience_record.ExperienceRecord`

Current decision:

LIVE + SECONDARY / LEGACY CANDIDATE

---

### Group B

`intelligence.meta.meta_learning_engine.MetaLearningEngine`

`intelligence.learning.meta_learning_engine.MetaLearningEngine`

Current decision:



---

### Group C

`intelligence.learning.strategy_ranker.StrategyRanker`

`intelligence.strategy_ranker.StrategyRanker`

Current decision:

LIVE + SECONDARY

توضیح فارسی:

این سه گروه Duplicateهای شناخته‌شده فعلی هستند.

هیچ‌کدام هنوز مشمول حذف یا Merge نیستند.

---

# 19. Contract Migration Rule

Before migrating a secondary contract into the primary runtime contract,
the following must be verified:

1. All runtime consumers
2. All secondary consumers
3. Constructor compatibility
4. Input compatibility
5. Output compatibility
6. State ownership
7. Test compatibility
8. Composition-root wiring
9. Backward compatibility
10. Regression stability

توضیح فارسی:

Migration فقط زمانی مجاز است که کل زنجیره Contract بررسی شده باشد.

---

# 20. Contract Authority Hierarchy

The current authority hierarchy is:

Runtime Composition
↓
Runtime Consumer
↓
Producer
↓
Contract
↓
Tests
↓
Historical / Structural Evidence

توضیح فارسی:

Runtime و Consumer واقعی بالاترین وزن را در تعیین Contract Authority دارند.

Testها و ساختار Repository شواهد مهم هستند، اما به تنهایی تعیین‌کننده نیستند.

---

# 21. No-Deletion Decisions

The following are explicitly protected from destructive cleanup:

* duplicate ExperienceRecord
* duplicate MetaLearningEngine
* alternate StrategyRanker
* compatibility aliases
* compatibility bridges

until their dependency graph has been fully classified.

توضیح فارسی:

این موارد تا پایان Contract Audit نباید حذف یا Merge شوند.

هدف این تصمیم جلوگیری از شکستن مسیرهای قدیمی یا Secondary قبل از شناخت کامل آنهاست.

---

# 22. V5 Contract Freeze Boundary

The intended V5 boundary is:

Identify Runtime Contracts
→ Classify Live / Secondary / Legacy
→ Verify Ownership
→ Verify State Identity
→ Freeze Contracts
→ Define V5 Learning AI Contracts
→ Implement V5

توضیح فارسی:

ابتدا باید Contractهای موجود تثبیت شوند.

بعد از Freeze می‌توان Contractهای V5 Learning AI را تعریف کرد و سپس Implementation را آغاز کرد.

---

# 23. Audit Procedure

For every future contract change:

Current Contract
→ Producer
→ Consumer
→ Runtime Path
→ State Ownership
→ Tests
→ Classification
→ Decision
→ Documentation
→ Regression

توضیح فارسی:

هیچ Contract جدید یا تغییر Contract نباید مستقیماً وارد Refactor شود.

ابتدا باید مسیر واقعی آن مشخص و سپس تصمیم معماری ثبت شود.

---

# 24. Current Contract Ledger Summary

Current primary runtime contracts:

DecisionRecord
→ OutcomeRecord
→ PerformanceLearningAdapter
→ ExperienceRecord
→ ExperienceMemory
→ PatternIntelligence
→ StrategyLearner
→ StrategyMemory
→ StrategyRecall
→ StrategyRanker
→ StrategySelector
→ DecisionRules

Parallel runtime contracts:

GovernanceMemory
→ GovernanceRecallFlow
→ GovernanceIntelligentGate

Meta runtime contracts:

MetaIntelligence
→ MetaLearningEngine
→ MetaConfidenceAdapter

Secondary / Legacy candidate contracts:

learning.ExperienceRecord
learning.MetaLearningEngine
root StrategyRanker

توضیح فارسی:

این Summary وضعیت فعلی Contractهای اصلی و Secondary را در یک نگاه نشان می‌دهد.

---

# 25. Contract Decision Chain Record

Primary:

DecisionRecord
→ OutcomeRecord
→ Performance Learning
→ ExperienceRecord
→ ExperienceMemory
→ PatternIntelligence
→ StrategyLearner
→ StrategyMemory
→ StrategyRecall
→ StrategyRanker
→ StrategySelector
→ DecisionRules
→ Decision

Meta:

Decision
→ Outcome
→ Meta Feedback
→ MetaIntelligence
→ MetaLearningEngine
→ Confidence Adjustment
→ Next Decision

Evolution:

Strategy Performance
→ Evolution Decision
→ Governance
→ Strategy Evolution
→ StrategyMemory
→ StrategyRecall
→ StrategyRanking
→ StrategySelection

توضیح فارسی:

این سه Chain Record مرجع سریع برای Contract Architecture هستند.

هر Audit آینده باید ابتدا این زنجیره‌ها را بررسی کند و فقط در صورت مشاهده تغییر، Delta مربوط به آن بخش را Audit کند.

---

# 26. Current Status

Architecture Phase:

V5 Contract / Architecture Audit

Latest Known Commit:

eebf7a1

Latest Tag:

v5-contract-architecture-audit

Latest Known Full Regression:

612 passed

Working Tree:

Clean

توضیح فارسی:

این Ledger بر اساس آخرین وضعیت تأییدشده پروژه نوشته شده است.

هر تصمیم جدید باید در همین فایل ثبت شود تا Architecture Memory پروژه به صورت پایدار حفظ شود.


# Contract Decisions — Final Duplicate Contract Verdict

## ExperienceRecord

### Primary Runtime Contract

`intelligence.experience_record.ExperienceRecord`

Classification:

LIVE

Runtime chain:

PerformanceLearningAdapter
→ ExperienceRecord
→ ExperienceMemory
→ PatternIntelligence
→ StrategyLearner

Reason:

The Core Runtime explicitly imports and constructs the core ExperienceRecord
through PerformanceLearningAdapter.

---

### Secondary Contract

`intelligence.learning.experience_record.ExperienceRecord`

Classification:

SECONDARY / LEGACY CANDIDATE

Known consumers:

learning/experience_engine.py

learning/pattern_detector.py

Decision:

DO NOT DELETE

DO NOT MERGE

DO NOT RENAME

Required future action:

Audit the complete Learning Subsystem before any migration decision.

توضیح فارسی:

نسخه Core قرارداد اصلی Runtime است.

نسخه Learning در یک مسیر جداگانه استفاده می‌شود و هنوز وضعیت نهایی آن مشخص نیست.

---

# MetaLearningEngine

### Primary Runtime Contract

`intelligence.meta.meta_learning_engine.MetaLearningEngine`

Classification:

LIVE

Construction:

IntelligenceComponents

Runtime ownership:

IntelligenceComponents

Runtime consumer:

IntelligenceFlow

Runtime identity:

IntelligenceFlow receives the same instance from
IntelligenceComponents.

Contract:

learn(meta_insight)

Runtime output:

confidence_adjustment

reliability

Runtime chain:

MetaIntelligence
→ MetaInsight
→ MetaLearningEngine
→ Confidence Adjustment
→ IntelligenceFlow

توضیح فارسی:

این نسخه به صورت مستقیم در Composition Root ساخته می‌شود و IntelligenceFlow همان Instance را مصرف می‌کند.

بنابراین Live بودن آن با Construction و End-to-End Runtime Usage تأیید شده است.

---

### Secondary Contract

`intelligence.learning.meta_learning_engine.MetaLearningEngine`

Classification:

SECONDARY

Contract:

analyze(knowledge)

Output:

MetaLearningInsight

Known path:

MetaLearningFlow
→ MetaLearningEngine
→ MetaLearningInsight

Decision:

KEEP SEPARATE

DO NOT MERGE

DO NOT DELETE

Reason:

The Learning contract and Runtime contract have different APIs,
different inputs, different outputs, and different dependency paths.

توضیح فارسی:

این دو فقط دو پیاده‌سازی از یک Contract نیستند.

آن‌ها دو مسئولیت متفاوت دارند و فعلاً باید جدا باقی بمانند.

---

# StrategyRanker

### Primary Runtime Contract

`intelligence.learning.strategy_ranker.StrategyRanker`

Classification:

LIVE

Construction:

IntelligenceComponents

Runtime ownership:

IntelligenceComponents

Runtime consumer:

IntelligenceFlow

Downstream consumer:

StrategySelector

Runtime dependency:

StrategyRecall
→ StrategyRanker
→ StrategySelector

توضیح فارسی:

این نسخه Ranker فعال Runtime است.

IntelligenceFlow مستقیماً Instance جدید نمی‌سازد و Instance ساخته‌شده در Composition Root را مصرف می‌کند.

---

### Secondary Contract

`intelligence.strategy_ranker.StrategyRanker`

Classification:

SECONDARY

Known contract:

rank()
→ list

rank_with_result()
→ StrategyRankingResult

best()
→ dict

Known distinction:

The root implementation exposes a richer ranking-result contract.

Decision:

KEEP SEPARATE

DO NOT MERGE

DO NOT DELETE

Reason:

The root implementation is not constructed by the current
IntelligenceComponents composition root.

Its contract is also structurally different from the current runtime
ranking path.

توضیح فارسی:

نسخه Root فعلاً در مسیر اصلی Runtime ساخته نمی‌شود.

با این حال چون Contract متفاوتی دارد، صرفاً به دلیل نام مشابه نباید Legacy فرض شود.

---

# Final Duplicate Contract Matrix

| Contract Family    | Primary Runtime                                             | Secondary                                                       | Final Classification                |
| ------------------ | ----------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------- |
| ExperienceRecord   | `intelligence.experience_record.ExperienceRecord`           | `intelligence.learning.experience_record.ExperienceRecord`      | LIVE + SECONDARY / LEGACY CANDIDATE |
| MetaLearningEngine | `intelligence.meta.meta_learning_engine.MetaLearningEngine` | `intelligence.learning.meta_learning_engine.MetaLearningEngine` | LIVE + SECONDARY                    |
| StrategyRanker     | `intelligence.learning.strategy_ranker.StrategyRanker`      | `intelligence.strategy_ranker.StrategyRanker`                   | LIVE + SECONDARY                    |

توضیح فارسی:

در هر سه خانواده، Contract اصلی Runtime اکنون مشخص است.

هیچ Merge یا Delete در این مرحله انجام نمی‌شود.

---

# Runtime Authority Rule

For these three contract families, runtime authority is determined by:

Composition Root
→ Runtime Instance
→ IntelligenceFlow
→ Actual Consumer

not by:

* filename
* class name
* directory location
* test existence
* implementation richness

توضیح فارسی:

این Audit یک قاعده مهم برای آینده ققنوس تثبیت کرد:

مرجع تشخیص Live Contract مسیر واقعی Runtime است، نه ظاهر Repository.

---

# Additional Architecture Debt

Observed in IntelligenceFlow:

Direct imports exist for runtime component classes, while the actual runtime
instances are obtained from IntelligenceComponents.

Observed imports include:

`intelligence.meta.meta_learning_engine.MetaLearningEngine`

`intelligence.learning.strategy_ranker.StrategyRanker`

Current decision:

DOCUMENT ONLY

NO CLEANUP DURING CONTRACT FREEZE

Future action:

Verify whether these imports are unused and remove them only during an
explicit cleanup/refactoring stage.

توضیح فارسی:

این موارد احتمالاً Importهای غیرضروری هستند.

اما در مرحله Contract Freeze نباید صرفاً برای تمیزکاری حذف شوند.

---

# Final Architecture Chain Record

Composition Root
→ Runtime Instance
→ IntelligenceFlow
→ Runtime Consumer
→ Contract Authority
→ Live / Secondary Classification

Duplicate Contract Audit:

ExperienceRecord
→ Core Runtime / Learning Runtime
→ LIVE / SECONDARY CANDIDATE

MetaLearningEngine
→ Meta Runtime / Learning Analysis
→ LIVE / SECONDARY

StrategyRanker
→ Runtime Ranking / Alternate Ranking
→ LIVE / SECONDARY

توضیح فارسی:

این Chain Record نتیجه نهایی Audit سه خانواده Contract است و باید به عنوان نقطه شروع Auditهای بعدی حفظ شود.
