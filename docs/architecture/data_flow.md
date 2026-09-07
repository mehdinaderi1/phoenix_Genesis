# Phoenix Genesis — Runtime Data Flow

## 1. Purpose

This document describes how information moves through the current
Phoenix Genesis runtime.

The focus is on:

Producer
→ Transformation
→ Contract
→ Consumer

It is not a complete class inventory.

Its purpose is to make future contract audits delta-based.

توضیح فارسی:

این فایل مسیر حرکت اطلاعات در Runtime فعلی ققنوس را ثبت می‌کند.

تمرکز اصلی روی رابطه بین Producer، Transformation، Contract و Consumer است.

این فایل فهرست تمام Classهای Repository نیست.

هدف اصلی آن این است که Auditهای آینده بر اساس تغییرات انجام شوند و نیازی به بازسازی کامل Data Flow نباشد.

---

# 2. Global Data Lifecycle

Market Data
↓
Market Context
↓
Market Intelligence
↓
Signal / Regime / Risk
↓
Decision Context
↓
Decision
↓
Outcome
↓
Performance Learning
↓
Experience
↓
Pattern
↓
Strategy Learning
↓
Strategy Memory
↓
Strategy Recall
↓
Strategy Ranking
↓
Strategy Selection
↓
Next Decision

توضیح فارسی:

این زنجیره چرخه اصلی حرکت اطلاعات از Market Data تا Decision بعدی را نشان می‌دهد.

در این چرخه، نتیجه Decision دوباره به Learning و Strategy Intelligence برمی‌گردد و در نهایت روی Decisionهای آینده اثر می‌گذارد.

---

# 3. Market → Decision Flow

Market data enters the intelligence pipeline as market context.

Conceptual transformation:

Market Data
→ Market Analysis
→ Signal Generation
→ Multi-Timeframe Context
→ Consensus
→ Market Regime
→ Risk Assessment
→ Reasoning
→ Decision Engine

The resulting intelligence context is used to construct/validate a
Decision.

توضیح فارسی:

Market Data ابتدا به Market Context تبدیل می‌شود.

سپس Market Analysis، Signal، Multi-Timeframe Context، Consensus، Regime و Risk ساخته می‌شوند و در نهایت اطلاعات وارد Reasoning و Decision Engine می‌شوند.

خروجی این مسیر برای ساخت و اعتبارسنجی Decision استفاده می‌شود.

---

# 4. Decision Contract Boundary

Primary object:

DecisionRecord

Conceptual producer:

Decision Engine / Decision Flow

Conceptual consumers:

* Decision Validation
* Action Proposal
* Decision Memory
* Outcome processing
* Performance learning
* Meta intelligence

DecisionRecord is therefore an upstream contract for the post-decision
learning lifecycle.

توضیح فارسی:

DecisionRecord قرارداد بالادستی چرخه‌ای است که بعد از Decision آغاز می‌شود.

مصرف‌کنندگان آن شامل Validation، Action Proposal، Decision Memory، Outcome Processing، Performance Learning و Meta Intelligence هستند.

---

# 5. Decision → Outcome

The decision becomes the source context for outcome tracking.

Flow:

DecisionRecord
↓
DecisionOutcomeBridge
↓
OutcomeRecord

Semantic rule:

Decision describes what the intelligence system decided.

Outcome describes what actually happened afterward.

These are different semantic contracts.

توضیح فارسی:

Decision بیان می‌کند سیستم چه تصمیمی گرفته است.

Outcome بیان می‌کند بعد از آن تصمیم در بازار چه اتفاقی افتاده است.

این دو Contract از نظر معنایی متفاوت هستند و نباید با یکدیگر ادغام شوند.

---

# 6. Outcome → Performance

OutcomeRecord represents realized result information.

Flow:

OutcomeRecord
↓
Performance Processing
↓
Performance Learning

Performance learning converts realized outcome information into a form
usable by learning systems.

The learning layer must not independently redefine the realized outcome.

توضیح فارسی:

OutcomeRecord نماینده نتیجه تحقق‌یافته است.

Performance Learning اطلاعات این نتیجه را برای سیستم‌های Learning آماده می‌کند.

Learning نباید تعریف مستقلی از نتیجه واقعی بازار ایجاد کند.

---

# 7. Performance → Experience

Primary bridge:

PerformanceLearningAdapter

Flow:

Outcome / Performance
↓
PerformanceLearningAdapter
↓
ExperienceRecord
↓
ExperienceMemory

The adapter is responsible for converting performance information into
the core learning experience contract.

Relevant contextual information includes:

* regime
* signal
* risk
* success
* score
* decision
* strategy
* confidence
* trace
* champion strategy

توضیح فارسی:

PerformanceLearningAdapter پل اصلی بین Performance و Experience است.

این Adapter باید اطلاعات لازم برای Learning را منتقل کند و در این تبدیل Context مهم Decision و Strategy از بین نرود.

---

# 8. ExperienceRecord — Core Contract

Authoritative core runtime contract:

intelligence.experience_record.ExperienceRecord

Producer:

PerformanceLearningAdapter

Primary consumer:

ExperienceMemory

Downstream consumers:

Pattern Recognition

Strategy learning

Strategy identity learning

The core ExperienceRecord enters the learning lifecycle through ExperienceMemory.

Pattern recognition consumes the stored experience representation rather than bypassing the ExperienceMemory boundary.

The contract carries contextual learning information rather than redefining market outcome semantics.

توضیح فارسی:

ExperienceRecord اصلی Runtime توسط PerformanceLearningAdapter تولید می‌شود و مصرف‌کننده مستقیم آن ExperienceMemory است.

بعد از ذخیره‌سازی، اطلاعات Experience وارد مسیر Pattern Recognition و سپس Strategy Learning می‌شود.

بنابراین PatternRecognizer نباید به عنوان مصرف‌کننده مستقیم Core ExperienceRecord ثبت شود.

---

# 9. Experience → Pattern

Flow:

ExperienceMemory
↓
PatternRecognizer
↓
PatternCluster
↓
PatternIntelligence

Pattern recognition transforms stored experience into recurring
contextual structures.

Important rule:

Composite strategy identity must survive this transformation.

Historical issue:

Composite keys based on underscore splitting could incorrectly break
regime values such as:

TRENDING_BULLISH

This was corrected so the complete contextual identity is preserved.

توضیح فارسی:

Pattern Recognition تجربه‌های ذخیره‌شده را به ساختارهای تکرارشونده Contextual تبدیل می‌کند.

هویت ترکیبی Strategy باید در این Transformation کاملاً حفظ شود.

در گذشته Split کردن کلیدها بر اساس Underscore می‌توانست مقدارهایی مانند Regimeهای ترکیبی را خراب کند.

این مشکل اصلاح شده است و Context کامل باید حفظ شود.

---

# 10. Pattern → Strategy Learning

Flow:

PatternIntelligence
↓
StrategyLearner
↓
Learned Strategy
↓
StrategyMemory

StrategyLearner transforms pattern/experience information into a
learned strategy representation.

The strategy representation must preserve identity/context required by
downstream consumers.

توضیح فارسی:

StrategyLearner اطلاعات Pattern و Experience را به Strategy یادگرفته‌شده تبدیل می‌کند.

Identity و Context مربوط به Strategy باید برای مصرف‌کنندگان بعدی حفظ شود.

---

# 11. Strategy Memory → Recall

Flow:

StrategyMemory
↓
StrategyRecall
↓
Candidate Strategies

StrategyMemory is the storage boundary.

StrategyRecall is the retrieval boundary.

Recall should not become the ranking or selection boundary.

توضیح فارسی:

StrategyMemory مرز ذخیره‌سازی Strategy است.

StrategyRecall مرز بازیابی Strategy است.

Recall نباید به صورت پنهان مسئول Ranking یا Selection شود.

---

# 12. Recall → Ranking

Flow:

Candidate Strategies

↓

intelligence.learning.strategy_ranker.StrategyRanker

↓

Strategy Ranking

Current runtime ranker:

intelligence.learning.strategy_ranker.StrategyRanker

Classification:

LIVE RUNTIME CONTRACT

Ownership:

IntelligenceComponents

Runtime consumer:

StrategySelector

A second ranker exists:

intelligence.strategy_ranker.StrategyRanker

Classification:

SECONDARY CONTRACT

The secondary ranker is not constructed by the current Composition Root.

The two contracts must remain separate until an explicit future contract decision establishes a migration or replacement path.

توضیح فارسی:

StrategyRanker نسخه موجود در مسیر Learning، Contract فعال Runtime است.

این Component توسط IntelligenceComponents ساخته و به StrategySelector متصل می‌شود.

نسخه موجود در مسیر root یک Contract ثانویه است و در Composition Root فعلی ساخته نمی‌شود.

این دو Contract فعلاً باید جدا باقی بمانند و حذف یا Merge کردن آنها نیازمند تصمیم معماری مستقل است.

---

# 13. Ranking → Selection

Flow:

Strategy Ranking
↓
StrategySelector
↓
Champion Strategy

Semantic responsibility:

Ranker:
Compare and order candidates.

Selector:
Choose the champion.

The two responsibilities must remain distinct.

توضیح فارسی:

Ranker مسئول مقایسه و مرتب‌سازی Candidateها است.

Selector مسئول انتخاب Champion است.

این دو مسئولیت باید جدا باقی بمانند.

---

# 14. Champion → Decision Gate

Flow:

Champion Strategy
↓
DecisionRules
↓
Decision Gate
↓
Validated Decision

DecisionRules contains the current strategy validity gate.

The existing gate is the authoritative validation boundary unless a
future architecture decision explicitly replaces it.

توضیح فارسی:

DecisionRules شامل Gate فعلی اعتبار Strategy است.

این Gate مرز معتبر فعلی برای Validation محسوب می‌شود.

تا زمانی که تصمیم معماری جدیدی گرفته نشده، نباید Gate موازی دیگری ساخته شود.

---

# 15. Strategy Evolution Data Flow

Strategy evolution operates on strategy performance.

Flow:

Strategy Performance
↓
Performance Analyzer
↓
Evolution Decision
↓
Governance
↓
Strategy Evolution
↓
Strategy Memory

Possible evolution decisions:

KEEP
RETIRE
IMPROVE

Evolution therefore feeds back into the strategy knowledge base.

توضیح فارسی:

Evolution بر اساس Performance Strategy عمل می‌کند.

نتیجه می‌تواند KEEP، RETIRE یا IMPROVE باشد.

نتیجه Evolution دوباره وارد StrategyMemory می‌شود و دانش Strategy را به‌روزرسانی می‌کند.

---

# 16. Governance Data Flow

Governance controls sensitive evolution operations.

Conceptual flow:

Evolution Candidate
↓
Governance Analysis / Gate
↓
Governance Decision
↓
Approved Evolution
↓
Strategy Evolution

Governance memory is separate from strategy memory.

Important distinction:

GovernanceMemory
≠
GovernanceEvolutionMemory

They must not be treated as interchangeable contracts.

توضیح فارسی:

Governance روی عملیات حساس Evolution کنترل و محدودیت اعمال می‌کند.

GovernanceMemory و GovernanceEvolutionMemory دو Contract متفاوت هستند و نباید به عنوان یک Memory واحد در نظر گرفته شوند.

---

# 17. Governance Memory Identity

Where multiple governance consumers require shared state:

GovernanceMemory
↓
GovernanceRecallFlow
↓
GovernanceIntelligentGate

The same memory instance must be propagated when state continuity is
required.

This identity sharing has been verified in the active strategy
evolution architecture.

توضیح فارسی:

هرجا چند Consumer به State مشترک Governance نیاز دارند، همان Instance از GovernanceMemory باید به آنها منتقل شود.

اشتراک Identity این Memory در Architecture فعال Strategy Evolution بررسی و تأیید شده است.

---

# 18. Meta Feedback Flow

The meta layer consumes information about the intelligence process.

Conceptual flow:

Meta intelligence operates above ordinary strategy learning.

توضیح فارسی:

Meta Intelligence در سطحی بالاتر از Strategy Learning عمل می‌کند.

این لایه اطلاعات مربوط به عملکرد خود فرآیند Intelligence را دریافت کرده و می‌تواند روی Confidence و Decisionهای آینده اثر بگذارد.

---

# 19. Runtime MetaLearningEngine

Authoritative runtime contract:

intelligence.meta.meta_learning_engine.MetaLearningEngine

Producer:

MetaIntelligence / MetaInsight

Consumer:

IntelligenceFlow

Contract:

learn(meta_insight)

Output includes information such as:

* confidence_adjustment
* reliability

Current implementation primarily uses MetaInsight reliability/sample
information for confidence adjustment.

توضیح فارسی:

این نسخه MetaLearningEngine قرارداد فعال Runtime است.

MetaIntelligence یا MetaInsight اطلاعات را تولید می‌کند و IntelligenceFlow مصرف‌کننده اصلی نتیجه است.

در Implementation فعلی، Confidence Adjustment عمدتاً بر Reliability و Sample اطلاعات MetaInsight متکی است.

---

# 20. Meta Confidence Flow

## Meta Intelligence Flow

### Main Runtime Flow

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

توضیح فارسی:

MetaIntelligence از DecisionMemory داده دریافت می‌کند و MetaInsight تولید می‌کند. MetaLearningEngine این Insight را یاد می‌گیرد و نتیجه یادگیری توسط MetaConfidenceAdapter مصرف می‌شود تا confidence تصمیم تنظیم شود.

### Secondary Strategy Meta Flow

```text
Strategy Context
→ StrategyIntelligenceService
→ MetaLearningFlow
→ learning.MetaLearningEngine.analyze()
→ MetaLearningInsight
→ EnhancedStrategyContext
→ Strategy Intelligence
```

توضیح فارسی:

این مسیر مربوط به Strategy Intelligence است و از Runtime Meta Learning اصلی مستقل است. خروجی آن MetaLearningInsight است که داخل EnhancedStrategyContext قرار می‌گیرد.

### Meta Confidence Contract

```text
Meta Learning Result
→ MetaConfidenceAdapter
→ report.confidence
```

توضیح فارسی:

MetaLearningEngine مستقیماً Adaptive Decision Context تولید نمی‌کند. خروجی آن توسط MetaConfidenceAdapter مصرف می‌شود و confidence گزارش تصمیم را تنظیم می‌کند.

### Meta Contracts

```text
MetaInsight
→ LIVE

MetaLearningInsight
→ LIVE WITHIN SECONDARY STRATEGY META PATH

EnhancedStrategyContext
→ LIVE WITHIN SECONDARY STRATEGY META PATH

MetaLearningFlow
→ LIVE SECONDARY
```

توضیح فارسی:

این Contractها باید به‌عنوان اجزای مستقل معماری مستند شوند و نباید صرفاً به‌عنوان جزئیات داخلی یک MetaLearningEngine واحد نمایش داده شوند.

### MetaLearning Contract

```text
intelligence.meta.meta_learning.MetaLearning
→ SECONDARY / TEST-BACKED CONTRACT
```

توضیح فارسی:

این Contract در Runtime اصلی IntelligenceFlow قرار ندارد، اما توسط تست‌ها و مسیرهای موجود پشتیبانی می‌شود؛ بنابراین فعلاً Legacy یا قابل حذف محسوب نمی‌شود.

---

# 21. Adaptive Context Timing

Current architecture contains an important timing characteristic.

Some adaptive confidence context is calculated before all information
from the current learning cycle has become available.

Conceptually:

Previous Knowledge
↓
Adaptive Context
↓
Current Decision

while some current-cycle learning occurs later:

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

This is documented architectural debt.

It should not be changed during documentation work.

توضیح فارسی:

در معماری فعلی بخشی از Adaptive Context قبل از کامل شدن اطلاعات Learning همان چرخه محاسبه می‌شود.

بنابراین بخشی از اطلاعاتی که در Current Cycle تولید شده‌اند ممکن است در همان Decision هنوز وارد Adaptive Context نشده باشند.

این مورد به عنوان Architectural Debt ثبت می‌شود و در مرحله مستندسازی نباید تغییر کند.

---

# 22. Decision Memory Flow

Flow:

Decision
↓
DecisionMemory

DecisionMemory preserves historical decision information.

It is semantically distinct from:

ExperienceMemory
StrategyMemory
GovernanceMemory
MetaMemory

توضیح فارسی:

DecisionMemory برای نگهداری سابقه Decision استفاده می‌شود.

این Memory از ExperienceMemory، StrategyMemory، GovernanceMemory و MetaMemory مستقل است.

---

# 23. Memory Boundaries

## DecisionMemory

Input:

Decision

Purpose:

Decision history.

---

## ExperienceMemory

Input:

ExperienceRecord

Purpose:

Contextual learning experience.

---

## StrategyMemory

Input:

Learned Strategy

Purpose:

Learned strategy knowledge.

---

## GovernanceMemory

Input:

Governance state / records

Purpose:

Governance history and state.

---

## GovernanceEvolutionMemory

Input:

Evolution-specific governance information

Purpose:

Evolution governance memory.

---

## MetaMemory

Input:

Meta feedback

Purpose:

Meta-level feedback/history.

توضیح فارسی:

هر Memory یک مسئولیت معنایی مشخص دارد.

DecisionMemory برای Decision History است.

ExperienceMemory برای تجربه قابل یادگیری است.

StrategyMemory برای دانش Strategy است.

GovernanceMemory برای State و History مربوط به Governance است.

GovernanceEvolutionMemory برای اطلاعات Governance مخصوص Evolution است.

MetaMemory برای Feedback و History سطح Meta است.

این Memoryها Storage Containerهای قابل جایگزینی نیستند.

---

# 24. Contract Transformation Chain

The most important transformation chain is:

DecisionRecord
↓
OutcomeRecord
↓
Performance Representation
↓
ExperienceRecord
↓
Pattern Representation
↓
Learned Strategy
↓
Stored Strategy
↓
Recalled Strategy
↓
Ranked Strategy
↓
Champion Strategy
↓
Decision

Each transformation represents a semantic boundary.

توضیح فارسی:

این مهم‌ترین زنجیره Transformation در Runtime است.

هر مرحله یک مرز معنایی مستقل دارد و در Audit باید Contract ورودی و خروجی هر مرحله مشخص باشد.

---

# 25. Producer → Consumer Rules

Every contract audit should identify:

1. Who produces the object?
2. What transformation occurs?
3. Who consumes it?
4. Is the consumer runtime or secondary?
5. Is state shared?
6. Is identity preserved?
7. Is backward compatibility required?

A class should not be classified as a runtime contract merely because
it exists or is tested.

توضیح فارسی:

در هر Contract Audit باید مشخص شود چه کسی Object را تولید می‌کند، چه Transformationای رخ می‌دهد، چه کسی آن را مصرف می‌کند، Consumer فعال است یا Secondary، آیا State مشترک است، آیا Identity حفظ شده و آیا Compatibility لازم است.

صرف وجود یک Class یا حتی Test شدن آن، برای Runtime Contract بودن کافی نیست.

---

# 26. Duplicate Contract Data Flows

## ExperienceRecord

### Core Runtime

PerformanceLearningAdapter
↓
intelligence.experience_record.ExperienceRecord
↓
ExperienceMemory / Pattern / Strategy Learning

توضیح فارسی:

این مسیر، ExperienceRecord فعال در Core Runtime را نشان می‌دهد.

### Secondary Learning Contract

learning subsystem
↓
intelligence.learning.experience_record.ExperienceRecord
↓
learning/experience_engine.py
learning/pattern_detector.py

These flows are currently treated as separate.

توضیح فارسی:

این نسخه در مسیر Learning ثانویه دیده می‌شود.

دو مسیر فعلاً جدا در نظر گرفته می‌شوند و تا پایان Contract Audit نباید Merge یا Delete شوند.

---

# 27. Duplicate MetaLearningEngine Flows

## Runtime

MetaIntelligence

↓

intelligence.meta.meta_learning_engine.MetaLearningEngine

↓

IntelligenceFlow

Contract:

learn(meta_insight)

Classification:

LIVE RUNTIME CONTRACT

توضیح فارسی:

این نسخه MetaLearningEngine قرارداد فعال Runtime است.

IntelligenceFlow نتیجه Meta Learning را از طریق قرارداد learn(meta_insight) مصرف می‌کند.

---

## Secondary

MetaLearningFlow

↓

intelligence.learning.meta_learning_engine.MetaLearningEngine

↓

Secondary learning analysis

Contract:

analyze(knowledge) → MetaLearningInsight

Classification:

SECONDARY CONTRACT

These are separate contracts.

The secondary learning engine must not be merged into the runtime MetaLearningEngine without explicit producer, consumer, contract, and compatibility analysis.

توضیح فارسی:

نسخه موجود در مسیر Learning یک Contract ثانویه است.

این نسخه قرارداد متفاوتی دارد و از analyze(knowledge) برای تولید MetaLearningInsight استفاده می‌کند.

یکسان بودن نام Class دلیل کافی برای Merge کردن این دو Contract نیست.

---

# 28. StrategyRanker Data Flows

## Current Runtime

StrategyRecall
↓
intelligence.learning.strategy_ranker.StrategyRanker
↓
StrategySelector

توضیح فارسی:

این StrategyRanker در مسیر فعلی Runtime قرار دارد.

## Secondary / Alternate

Candidate Strategies
↓
intelligence.strategy_ranker.StrategyRanker
↓
Richer ranking result contract

Replacement/merging requires explicit contract analysis.

توضیح فارسی:

نسخه دیگر Contract خروجی غنی‌تری دارد.

هرگونه Replacement یا Merge باید بعد از بررسی دقیق Contract و Dependency انجام شود.

---

# 29. State Identity Rule

Whenever a stateful component is passed between flows:

Producer

↓

Shared Instance

↓

Consumer A

↓

Consumer B

the architecture should preserve object identity when shared state is semantically required.

This rule applies to:

GovernanceMemory

StrategyMemory

ExperienceMemory

shared intelligence components

The current architecture explicitly verifies shared GovernanceMemory identity in the active strategy evolution path.

Other stateful components must be evaluated according to their actual ownership and dependency path rather than assumed to be shared.

توضیح فارسی:

هرگاه یک Component دارای State بین چند Flow یا Consumer استفاده شود، در صورتی که معماری به State مشترک نیاز داشته باشد باید Identity همان Instance حفظ شود.

اشتراک Identity برای GovernanceMemory در مسیر فعال Strategy Evolution بررسی و تأیید شده است.

برای سایر Componentهای Stateful نباید بدون بررسی Dependency و Ownership فرض کنیم که Instance آنها حتماً مشترک است.

---

# 30. Current End-to-End Flow

Market
↓
Intelligence
↓
Decision
↓
Outcome
↓
Performance Learning
↓
Experience
↓
Pattern
↓
Strategy Learning
↓
Strategy Memory
↓
Strategy Recall
↓
Strategy Ranking
↓
Strategy Selection
↓
Decision Gate
↓
Validated Decision
↓
Meta Feedback
↓
Meta Intelligence
↓
Meta Learning
↓
Confidence Adaptation
↓
Next Decision

توضیح فارسی:

این زنجیره End-to-End، چرخه اصلی Runtime از Market تا Decision بعدی را نشان می‌دهد.

Parallel:

Strategy Performance
↓
Evolution
↓
Governance
↓
Strategy Memory

Experience / Pattern
↓
Meta Intelligence
↓
Meta Learning
↓
Confidence Adaptation
↓
Next Decision

توضیح فارسی:

در کنار مسیر اصلی، دو مسیر مهم وجود دارند.

مسیر Evolution از Strategy Performance شروع شده و از Governance عبور می‌کند و دوباره به StrategyMemory برمی‌گردد.

مسیر Meta از Experience و Pattern تغذیه می‌شود و از طریق Meta Learning روی Confidence تصمیم آینده اثر می‌گذارد.

---

# 31. Audit Usage

Future contract audits should begin by locating the contract in this
data flow.

Then inspect only:

Producer
→ Transformation
→ Consumer

If the flow is unchanged, no full remap is required.

If the flow changes, update this document and the relevant version
record.

توضیح فارسی:

در Auditهای آینده ابتدا باید Contract موردنظر در همین Data Flow پیدا شود.

سپس فقط Producer، Transformation و Consumer بررسی شوند.

اگر Flow تغییر نکرده باشد، Remap کامل Repository لازم نیست.

اگر Flow تغییر کرده باشد، این فایل و Version Record مربوطه باید به‌روزرسانی شوند.

---

# 32. Current Status

Architecture Phase:

V5 Contract / Architecture Audit

Latest Known Regression:

612 passed

Latest Commit:

eebf7a1

Latest Tag:

v5-contract-architecture-audit

توضیح فارسی:

این فایل وضعیت Data Flow را در آخرین Checkpoint معماری ثبت می‌کند.

در حال حاضر پروژه در مرحله V5 Contract / Architecture Audit قرار دارد و آخرین Regression ثبت‌شده 612 تست موفق بوده است.

Commit فعلی eebf7a1 و Tag فعلی v5-contract-architecture-audit هستند.

