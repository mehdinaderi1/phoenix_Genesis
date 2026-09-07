# Phoenix Genesis — Architecture Decisions

## 1. Purpose

This document records the architectural decisions that define the current Phoenix Genesis runtime.

Its purpose is to preserve the reasoning behind the architecture.

It answers:

Why is a component owned by a specific layer?

Why is a boundary preserved?

Why are apparently duplicate contracts kept separate?

Why is state identity important?

Why are certain responsibilities intentionally separated?

This document records architectural decisions.

Runtime contract classification is maintained separately in:

docs/decisions/contract_decisions.md

توضیح فارسی:

این فایل دلیل و منطق تصمیم‌های معماری ققنوس را ثبت می‌کند.

Contract classification در فایل جداگانه Contract Decisions نگهداری می‌شود.

---

# 2. Decision Principles

The current architecture follows these principles:

Runtime Beats Appearance

Producer → Consumer Defines Contract

Composition Root Owns Shared Construction

State Identity Must Be Preserved When Required

Semantic Boundaries Must Remain Explicit

Responsibilities Must Not Be Silently Combined

Compatibility Must Be Preserved Until Replacement Is Validated

No Destructive Cleanup Before Contract Classification

توضیح فارسی:

معماری فعلی بر اساس رفتار واقعی Runtime، مسیر Producer تا Consumer، مالکیت Composition Root، حفظ State Identity و جداسازی مسئولیت‌های معنایی شکل گرفته است.

---

# 3. Composition Root Decision

Decision:

IntelligenceComponents is the primary Composition Root for shared runtime intelligence components.

Rationale:

Shared and stateful dependencies require centralized construction and ownership.

This prevents multiple independent instances from being created unintentionally.

Runtime consumers should receive authoritative instances from the Composition Root.

Primary owner:

intelligence.components.intelligence_components.IntelligenceComponents

Primary orchestrator:

intelligence.flow.IntelligenceFlow

توضیح فارسی:

IntelligenceComponents نقطه اصلی ساخت و مالکیت Componentهای مشترک Runtime است.

IntelligenceFlow مسئول هماهنگی Runtime است اما مالک مستقل تمام Componentها نیست.

این تصمیم برای جلوگیری از ایجاد Instanceهای مستقل و از بین رفتن State مشترک اتخاذ شده است.

---

# 4. IntelligenceFlow Responsibility Decision

Decision:

IntelligenceFlow is the primary runtime orchestration boundary.

It coordinates intelligence processing but should not independently construct duplicate stateful components already owned by IntelligenceComponents.

Rationale:

Orchestration and component ownership are separate responsibilities.

This separation preserves dependency identity and makes runtime composition explicit.

توضیح فارسی:

IntelligenceFlow مرکز هماهنگی Runtime است، نه Composition Root مستقل.

اگر Componentی توسط IntelligenceComponents ساخته شده باشد، Flow باید همان Instance را مصرف کند.

---

# 5. DecisionRecord Boundary Decision

Decision:

DecisionRecord remains the primary structured contract at the Decision boundary.

Rationale:

Multiple downstream systems depend on decision context.

The decision context must be preserved when entering:

Validation

Action Proposal

Decision Memory

Outcome processing

Performance learning

Meta intelligence

توضیح فارسی:

DecisionRecord به عنوان Contract اصلی Decision حفظ می‌شود زیرا چندین بخش پایین‌دست به Context تصمیم وابسته هستند.

هر تغییر در این Contract می‌تواند اثر زنجیره‌ای روی چند لایه داشته باشد.

---

# 6. Decision and Outcome Separation

Decision:

Decision and Outcome remain separate semantic contracts.

Decision describes what the intelligence system decided.

Outcome describes what happened afterward in market reality.

The bridge between them is:

DecisionOutcomeBridge

Rationale:

A prediction or decision must not be confused with its realized result.

توضیح فارسی:

Decision و Outcome نباید یکی شوند.

Decision مربوط به تصمیم سیستم است و Outcome مربوط به واقعیت تحقق‌یافته بعد از تصمیم.

DecisionOutcomeBridge مرز بین این دو مفهوم است.

---

# 7. Outcome as Market Reality

Decision:

OutcomeRecord is the semantic boundary for realized outcome information.

Rationale:

Performance and learning systems must consume realized outcome information rather than redefine it independently.

This prevents multiple layers from creating competing interpretations of market reality.

توضیح فارسی:

OutcomeRecord مرجع نتیجه تحقق‌یافته است.

Performance و Learning باید نتیجه واقعی را مصرف کنند و نباید هرکدام تعریف مستقلی از Outcome ایجاد کنند.

---

# 8. Performance Learning Boundary

Decision:

PerformanceLearningAdapter is the primary transformation boundary between performance information and the core learning experience contract.

Flow:

Outcome / Performance

↓

PerformanceLearningAdapter

↓

ExperienceRecord

Rationale:

Performance representation and learning experience have different responsibilities.

The adapter preserves required decision and strategy context during transformation.

توضیح فارسی:

Performance و Experience دو مفهوم متفاوت هستند.

PerformanceLearningAdapter وظیفه تبدیل Performance به Experience را دارد و باید Context لازم مانند Strategy، Decision، Regime، Signal، Risk و Confidence را حفظ کند.

---

# 9. Core ExperienceRecord Decision

Decision:

The authoritative core runtime ExperienceRecord is:

intelligence.experience_record.ExperienceRecord

Rationale:

This contract is produced by PerformanceLearningAdapter and enters the core learning lifecycle through ExperienceMemory.

The learning experience contract must carry contextual learning information without redefining market outcome semantics.

توضیح فارسی:

ExperienceRecord اصلی Runtime در مسیر Core قرار دارد.

این Contract توسط PerformanceLearningAdapter تولید می‌شود و از طریق ExperienceMemory وارد چرخه Learning می‌شود.

---

# 10. ExperienceMemory Boundary

Decision:

ExperienceMemory remains the storage boundary for contextual learning experience.

Rationale:

Pattern recognition should consume stored learning experience rather than bypassing the ExperienceMemory boundary.

This creates a clear separation between:

Experience creation

Experience storage

Pattern recognition

Strategy learning

توضیح فارسی:

ExperienceMemory مرز ذخیره‌سازی Experience است.

Pattern Recognition نباید این مرز را دور بزند و مستقیماً از Producer اولیه Experience تغذیه شود.

---

# 11. Pattern Intelligence Decision

Decision:

PatternIntelligence operates downstream of stored experience.

Flow:

ExperienceMemory

↓

PatternRecognizer

↓

PatternCluster

↓

PatternIntelligence

Rationale:

Pattern intelligence is a transformation of accumulated experience, not an alternative experience storage system.

Composite contextual identity must survive this transformation.

توضیح فارسی:

PatternIntelligence باید بر اساس Experience ذخیره‌شده ساخته شود.

هویت ترکیبی Strategy و Context باید در تمام این Transformation حفظ شود.

---

# 12. Strategy Identity Decision

Decision:

Strategy identity must remain stable across the strategy intelligence lifecycle.

Required path:

StrategyLearner

↓

StrategyMemory

↓

StrategyRecall

↓

StrategyRanking

↓

StrategySelection

↓

Decision

Rationale:

A strategy can be learned, stored, recalled, ranked, and selected only if its identity remains compatible across these boundaries.

StrategyBridge may provide compatibility or canonicalization where required.

توضیح فارسی:

هویت Strategy یک قرارداد معماری در کل چرخه Strategy است.

اگر Identity در یکی از مراحل تغییر کند، Ranking، Selection یا Decision ممکن است روی Strategy اشتباه عمل کنند.

---

# 13. Strategy Memory Boundary

Decision:

StrategyMemory is the storage boundary for learned strategy knowledge.

StrategyMemory is not responsible for:

Ranking

Selection

Decision Gate

Rationale:

Separating persistence, ranking, and selection prevents responsibilities from becoming coupled.

توضیح فارسی:

StrategyMemory فقط مرز ذخیره دانش Strategy است.

Ranking متعلق به Ranker و Selection متعلق به Selector است.

این تفکیک برای جلوگیری از ترکیب مسئولیت‌ها حفظ می‌شود.

---

# 14. Strategy Recall Decision

Decision:

StrategyRecall is responsible for retrieving candidate strategies.

It must not silently become:

StrategyRanker

StrategySelector

Decision Gate

Rationale:

Retrieval, ranking, and selection represent different semantic responsibilities.

توضیح فارسی:

StrategyRecall فقط Strategyهای Candidate را بازیابی می‌کند.

نباید مسئول Ranking یا Selection شود.

---

# 15. Strategy Ranking Decision

Decision:

The current runtime StrategyRanker is:

intelligence.learning.strategy_ranker.StrategyRanker

It is owned and constructed by:

IntelligenceComponents

Its downstream consumer is:

StrategySelector

Rationale:

Runtime construction and producer-consumer dependency establish this implementation as the current runtime contract.

توضیح فارسی:

StrategyRanker موجود در مسیر Learning، Contract فعال Runtime است.

Composition Root آن را می‌سازد و StrategySelector مصرف‌کننده آن است.

---

# 16. Alternate StrategyRanker Decision

Decision:

The root implementation:

intelligence.strategy_ranker.StrategyRanker

remains separate from the runtime ranker.

Classification:

SECONDARY CONTRACT

Rationale:

It exposes a different and richer ranking-result contract.

Similarity of implementation or naming is insufficient evidence for merging.

No deletion or merge occurs without explicit contract migration analysis.

توضیح فارسی:

نسخه Root یک Contract ثانویه است.

با وجود شباهت نام و عملکرد کلی، Contract آن متفاوت است.

تا زمانی که مسیر Migration و Compatibility مشخص نشده باشد، حذف یا Merge انجام نمی‌شود.

---

# 17. Strategy Ranking and Selection Separation

Decision:

StrategyRanker ranks.

StrategySelector selects.

Flow:

StrategyRecall

↓

StrategyRanker

↓

StrategySelector

↓

Champion Strategy

Rationale:

Ranking and selection are distinct responsibilities.

The Ranker must not silently become the Selector.

توضیح فارسی:

Ranker فقط Candidateها را مقایسه و رتبه‌بندی می‌کند.

Selector Champion را انتخاب می‌کند.

این دو مسئولیت عمداً جدا باقی می‌مانند.

---

# 18. Decision Gate Reuse

Decision:

DecisionRules remains the authoritative strategy validity gate.

Flow:

Champion Strategy

↓

DecisionRules

↓

Decision Gate

↓

Validated Decision

Rationale:

A working validation boundary already exists.

Creating a parallel gate would duplicate responsibility and create competing validation contracts.

توضیح فارسی:

Gate فعلی در DecisionRules قرار دارد و باید Reuse شود.

تا زمانی که تصمیم معماری جدیدی وجود نداشته باشد، ساخت Gate موازی ممنوع است.

---

# 19. Strategy Evolution Separation

Decision:

Strategy Evolution remains a separate lifecycle from ordinary Strategy Selection.

Evolution decisions:

KEEP

RETIRE

IMPROVE

Flow:

Strategy Performance

↓

Performance Analysis

↓

Evolution Decision

↓

Governance

↓

Strategy Evolution

↓

Strategy Memory

Rationale:

Strategy selection answers which strategy should be used.

Strategy evolution answers whether a strategy should remain, retire, or improve.

توضیح فارسی:

Selection و Evolution دو سؤال متفاوت را پاسخ می‌دهند.

Selection انتخاب Strategy مناسب برای Decision است.

Evolution درباره آینده خود Strategy تصمیم می‌گیرد.

---

# 20. Governance Boundary Decision

Decision:

Governance remains an explicit control boundary for sensitive strategy evolution operations.

GovernanceMemory and GovernanceEvolutionMemory remain distinct.

Rationale:

Governance state and evolution-specific governance information have different semantic scopes.

They must not be treated as interchangeable storage contracts.

توضیح فارسی:

Governance یک مرز مستقل برای کنترل Evolution است.

GovernanceMemory و GovernanceEvolutionMemory دو Contract متفاوت هستند و نباید صرفاً به دلیل شباهت نام یکی فرض شوند.

---

# 21. Governance State Identity Decision

Decision:

When multiple governance consumers require shared state, the same GovernanceMemory instance must be propagated.

Verified active relationship:

GovernanceMemory

↓

GovernanceRecallFlow

↓

GovernanceIntelligentGate

Rationale:

Shared state requires shared object identity, not merely equivalent configuration.

توضیح فارسی:

هرجا چند Consumer به State مشترک Governance نیاز دارند، باید همان Instance از GovernanceMemory استفاده شود.

این Identity در مسیر فعال Strategy Evolution بررسی و تأیید شده است.

---

# 22. Meta Intelligence Layer Decision

Decision:

Meta Intelligence operates above ordinary Strategy Learning.

Flow:

Decision / Outcome / Performance

↓

Meta Feedback

↓

MetaIntelligence

↓

MetaLearningEngine

↓

Confidence Adjustment

↓

Next Decision

Rationale:

Meta Intelligence evaluates and influences the intelligence process itself rather than simply learning another strategy.

توضیح فارسی:

Meta Intelligence در سطح بالاتری از Strategy Learning قرار دارد.

هدف آن فقط یادگیری Strategy نیست؛ بلکه بررسی و تنظیم رفتار Intelligence در Decisionهای آینده است.

---

# 23. Runtime MetaLearningEngine Decision

Decision:

The authoritative runtime MetaLearningEngine is:

intelligence.meta.meta_learning_engine.MetaLearningEngine

Runtime contract:

learn(meta_insight)

Rationale:

This implementation is constructed by IntelligenceComponents and consumed through IntelligenceFlow.

توضیح فارسی:

MetaLearningEngine موجود در مسیر `intelligence.meta` قرارداد فعال Runtime است.

قرارداد اصلی آن `learn(meta_insight)` است.

---

# 24. Secondary MetaLearningEngine Decision

Decision:

The implementation:

intelligence.learning.meta_learning_engine.MetaLearningEngine

remains separate.

Classification:

SECONDARY CONTRACT

Contract:

analyze(knowledge) → MetaLearningInsight

Rationale:

It represents a different learning-analysis contract.

Class name similarity is not sufficient evidence for merging.

توضیح فارسی:

نسخه موجود در مسیر Learning یک Contract ثانویه با قرارداد متفاوت است.

این دو Engine نباید صرفاً به دلیل نام یکسان Merge شوند.

---

# 25. Adaptive Intelligence Timing Decision

Decision:

Current adaptive context timing remains unchanged during architecture documentation and contract freeze.

Current characteristic:

Previous Knowledge

↓

Adaptive Context

↓

Current Decision

while current-cycle learning continues later:

Current Decision

↓

Outcome

↓

Performance

↓

Experience

↓

Pattern

↓

Meta Learning

Rationale:

This timing is known architectural debt.

Changing it during documentation work would mix architectural cleanup with documentation and contract stabilization.

توضیح فارسی:

زمان‌بندی فعلی Adaptive Context یک Debt معماری شناخته‌شده است.

اما در مرحله Documentation و Contract Freeze نباید تغییر کند.

ابتدا باید Architecture تثبیت شود و سپس این Debt به صورت مستقل بررسی شود.

---

# 26. Stateful Component Identity Decision

Decision:

Stateful components must preserve object identity whenever semantic state continuity is required.

General rule:

Owner

↓

Shared Instance

↓

Consumer A

↓

Consumer B

Rationale:

Two separately constructed objects with identical configuration are not equivalent when state is part of the contract.

توضیح فارسی:

در Componentهای Stateful، یکسان بودن Configuration به معنی یکسان بودن State نیست.

اگر معماری به State مشترک نیاز داشته باشد، باید همان Object Instance منتقل شود.

---

# 27. Compatibility Decision

Decision:

Compatibility aliases, wrappers, and secondary contracts must remain until replacement has been explicitly validated.

Rationale:

Removing compatibility before downstream consumers are migrated can break hidden or indirect dependencies.

Migration requires:

Producer validation

Consumer validation

Contract compatibility

State identity validation

Regression validation

توضیح فارسی:

Compatibility نباید زودتر از موعد حذف شود.

قبل از جایگزینی یک Contract باید Producer، Consumer، Compatibility، State Identity و Regression بررسی شوند.

---

# 28. Duplicate Contract Decision

Decision:

Duplicate contracts are not automatically technical errors requiring immediate deletion.

Classification must precede cleanup.

Required classification:

LIVE

SECONDARY

LEGACY CANDIDATE

FROZEN

Rationale:

Repository appearance does not establish runtime authority.

Runtime construction, ownership, producer-consumer relationships, and state usage provide stronger evidence.

توضیح فارسی:

وجود دو Class مشابه به‌تنهایی به معنی خطای معماری نیست.

ابتدا باید مشخص شود کدام Contract در Runtime فعال است و کدام مسیر Secondary یا Legacy است.

---

# 29. No Destructive Cleanup Decision

Decision:

No duplicate contract is deleted, merged, or renamed solely during the architecture audit.

Rationale:

Architecture stabilization and code cleanup are separate activities.

Destructive cleanup requires an explicit migration decision.

توضیح فارسی:

هدف Audit فعلی تثبیت Architecture است، نه پاکسازی تهاجمی Repository.

حذف، Merge یا Rename فقط پس از مشخص شدن Migration Path انجام می‌شود.

---

# 30. Documentation Architecture Decision

Decision:

Phoenix Genesis architecture memory is maintained through layered documentation.

Primary layers:

docs/phoenix_map.md

docs/architecture/current_architecture.md

docs/architecture/data_flow.md

docs/architecture/dependency_map.md

docs/decisions/architecture_decisions.md

docs/decisions/contract_decisions.md

docs/versions/

docs/checkpoints/latest_state.md

Rationale:

A single document cannot efficiently preserve global architecture, runtime data flow, dependencies, contracts, decisions, and historical evolution simultaneously.

توضیح فارسی:

حافظه معماری ققنوس به صورت چندلایه نگهداری می‌شود.

هر فایل مسئول یک نوع اطلاعات است تا برای ادامه پروژه نیاز به Remap کامل Repository نباشد.

---

# 31. Delta Audit Decision

Decision:

Future architecture audits should be delta-based.

Recommended process:

Global Architecture Map

↓

Current Version Record

↓

Latest Checkpoint

↓

Changed Components

↓

Changed Contracts / Dependencies

↓

Targeted Audit

↓

Documentation Update

↓

Regression Validation

Rationale:

A stable architecture should not require complete remapping after every incremental change.

Full remapping is reserved for major architectural breaks or introduction of a new intelligence layer that invalidates the existing map.

توضیح فارسی:

پس از Freeze معماری، Auditهای آینده باید بر اساس تغییرات انجام شوند.

Remap کامل فقط زمانی لازم است که یک تغییر بزرگ ساختار فعلی را بی‌اعتبار کند.

---

# 32. Architecture Freeze Boundary

Decision:

The current V5 architecture will be considered frozen after consistency validation across:

phoenix_map.md

current_architecture.md

data_flow.md

dependency_map.md

architecture_decisions.md

contract_decisions.md

Rationale:

All architecture documents must describe the same runtime reality before V5 implementation begins.

توضیح فارسی:

Freeze معماری زمانی معتبر است که تمام سندهای اصلی یک Runtime واحد را توصیف کنند.

پس از آن می‌توان Contractهای V5 Learning AI را تعریف و Implementation را آغاز کرد.

---

# 33. V5 Learning AI Boundary

Decision:

V5 Learning AI implementation must begin only after the current runtime architecture and contract boundaries are explicit.

Required prerequisites:

Runtime ownership identified

Live contracts identified

Secondary contracts identified

State identity boundaries identified

Data flow documented

Dependency map documented

Architecture decisions documented

Contract decisions documented

توضیح فارسی:

V5 نباید قبل از تثبیت مرزهای معماری و Contractها وارد Implementation شود.

ابتدا باید بدانیم چه چیزی Live است، چه چیزی Secondary است و Ownership و State Identity در کجا قرار دارند.

---

# 34. Current Architectural Position

Current phase:

V5 Contract / Architecture Audit

Latest known regression:

612 passed

Latest commit:

eebf7a1

Latest tag:

v5-contract-architecture-audit

Current objective:

Freeze V4.9 / V5 architecture

↓

Define V5 Learning AI contracts

↓

Begin V5 implementation

توضیح فارسی:

پروژه در مرز بین Architecture Audit و V5 Learning AI قرار دارد.

ابتدا باید Consistency تمام سندهای معماری تکمیل شود.

پس از Freeze، تعریف Contractهای V5 انجام می‌شود و سپس Implementation آغاز خواهد شد.

---

# 35. Architecture Decision Chain Record

The architectural reasoning can be summarized as:

Runtime Reality

→ Composition Root Ownership

→ Explicit Contracts

→ Semantic Boundaries

→ State Identity

→ Responsibility Separation

→ Live / Secondary Classification

→ Compatibility Preservation

→ Architecture Freeze

→ V5 Learning AI Contracts

→ V5 Implementation

توضیح فارسی:

این Chain Record منطق اصلی تصمیم‌های معماری فعلی ققنوس را نشان می‌دهد.

ابتدا Runtime واقعی مشخص می‌شود، سپس Ownership و Contractها تثبیت می‌شوند، State Identity و مرز مسئولیت‌ها حفظ می‌شوند، Contractهای Live و Secondary طبقه‌بندی می‌شوند و بعد از Freeze معماری، V5 وارد مرحله تعریف Contract و Implementation می‌شود.
