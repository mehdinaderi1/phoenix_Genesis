# Phoenix Genesis — Runtime Dependency Map

## 1. Purpose

This document describes the known runtime dependency and ownership
relationships in Phoenix Genesis.

Its purpose is to answer:

Who owns the component?

Who constructs the component?

Who consumes the component?

Which components share state?

Which contracts are runtime contracts?

Which contracts are secondary or legacy candidates?

This is not a complete repository import graph.

It is an architecture-oriented dependency map.

توضیح فارسی:

این فایل Dependency Map معماری فعلی ققنوس است.

هدف آن نمایش تمام Importهای Repository نیست.

تمرکز آن روی Ownership، Construction، Consumption، Shared State و Contract Authority در Runtime است.

---

# 2. Global Ownership Model

The primary ownership hierarchy is:

IntelligenceComponents
↓
IntelligenceFlow
↓
Specialized Flows / Services
↓
Memory / Learning / Intelligence Consumers

توضیح فارسی:

IntelligenceComponents نقطه اصلی مالکیت Componentهای مشترک است.

IntelligenceFlow مصرف‌کننده و هماهنگ‌کننده اصلی این Componentهاست.

Flowها و Serviceهای تخصصی باید از Instanceهای معتبر استفاده کنند و نباید بدون دلیل نسخه مستقل از Componentهای Stateful بسازند.

---

# 3. Composition Root

Primary composition root:

intelligence.components.intelligence_components.IntelligenceComponents

Primary responsibility:

Construct and own shared intelligence components.

توضیح فارسی:

IntelligenceComponents مرجع اصلی Construction و Ownership برای Componentهای مشترک Runtime است.

این مرز باید تا حد امکان تنها نقطه ایجاد Instanceهای Shared و Stateful باشد.

---

# 4. Primary Runtime Orchestrator

Primary runtime orchestrator:

intelligence.flow.IntelligenceFlow

Dependency role:

Consumes shared components from IntelligenceComponents.

Coordinates:

* market intelligence
* signal generation
* regime analysis
* risk analysis
* reasoning
* decision generation
* decision validation
* strategy selection
* outcome processing
* performance learning
* experience/pattern learning
* strategy learning
* meta intelligence
* meta learning
* confidence adaptation
* decision memory

توضیح فارسی:

IntelligenceFlow مرکز هماهنگی Runtime است.

اما مالک مستقل تمام Componentها نیست.

وقتی Componentی در IntelligenceComponents ساخته شده و Shared است، IntelligenceFlow باید همان Instance را مصرف کند.

---

# 5. Shared Component Identity

Architectural rule:

A stateful shared component must preserve object identity when multiple
consumers depend on the same state.

Conceptual dependency:

IntelligenceComponents
↓
Shared Instance
↓
IntelligenceFlow
↓
Specialized Consumer

توضیح فارسی:

اگر چند بخش سیستم به State مشترک نیاز داشته باشند، مهم فقط یکسان بودن Configuration نیست.

باید در صورت نیاز معماری، همان Object Instance بین مصرف‌کنندگان Share شود.

---

# 6. Verified Shared Identity

The following identity relationships were verified during the
architecture audit:

f.strategy_council
is
f.components.strategy_council

f.performance_feedback
is
f.components.performance_feedback

توضیح فارسی:

این بررسی‌ها نشان دادند که در این موارد IntelligenceFlow و IntelligenceComponents به همان Instance مشترک متصل هستند.

این نوع Identity Check در Auditهای آینده نیز باید برای Componentهای Stateful حساس استفاده شود.

---

# 7. Decision Runtime Dependencies

Primary decision dependency chain:

Market Context
↓
Market Intelligence
↓
Signal Generation
↓
Multi-Timeframe Analysis
↓
Consensus
↓
Market Regime
↓
Risk Assessment
↓
Reasoning Engine
↓
Decision Engine
↓
Decision Validation
↓
Action Proposal
↓
Decision

توضیح فارسی:

این زنجیره Dependency اصلی تولید Decision را نشان می‌دهد.

هر مرحله باید Contract مورد انتظار مرحله بعدی را تولید کند.

---

# 8. Decision Contract Dependencies

Primary contract:

DecisionRecord

Primary downstream consumers:

* Decision Validation
* Action Proposal
* Decision Memory
* Outcome processing
* Performance learning
* Meta intelligence

Dependency direction:

Decision Engine
↓
DecisionRecord
↓
Post-Decision Consumers

توضیح فارسی:

DecisionRecord یک Contract بالادستی است.

بنابراین تغییر آن می‌تواند روی چندین بخش پایین‌دست اثر بگذارد و هر تغییر در آن باید با بررسی Consumerها انجام شود.

---

# 9. Decision → Outcome Dependencies

Primary bridge:

DecisionOutcomeBridge

Dependency chain:

DecisionRecord
↓
DecisionOutcomeBridge
↓
OutcomeRecord

Semantic dependency:

Decision
≠
Outcome

توضیح فارسی:

DecisionOutcomeBridge Context تصمیم را به مسیر Outcome منتقل می‌کند.

Decision و Outcome از نظر معنایی وابسته‌اند اما یک Contract واحد نیستند.

---

# 10. Outcome → Performance Dependencies

Dependency chain:

OutcomeRecord
↓
Performance Processing
↓
Performance Learning

Primary rule:

The learning layer consumes realized outcome information.

It must not independently redefine the realized outcome.

توضیح فارسی:

Outcome مرجع نتیجه تحقق‌یافته است.

Performance و Learning باید Outcome را مصرف کنند، نه اینکه هرکدام نتیجه بازار را به شکل مستقل تعریف کنند.

---

# 11. Performance → Experience Dependencies

Primary adapter:

PerformanceLearningAdapter

Dependency chain:

Outcome / Performance
↓
PerformanceLearningAdapter
↓
ExperienceRecord
↓
ExperienceMemory

توضیح فارسی:

PerformanceLearningAdapter مرز اصلی تبدیل Performance به Experience است.

---

# 12. Live ExperienceRecord Dependency

Authoritative runtime contract:

intelligence.experience_record.ExperienceRecord

Primary producer:

PerformanceLearningAdapter

Primary consumer:

ExperienceMemory

Downstream consumers:

Pattern Recognition

Strategy learning

Strategy identity learning

Dependency chain:

PerformanceLearningAdapter

↓

intelligence.experience_record.ExperienceRecord

↓

ExperienceMemory

↓

Pattern Intelligence

↓

Strategy Learning

The core ExperienceRecord enters the downstream learning architecture through ExperienceMemory.

Pattern recognition and strategy learning consume the stored experience representation rather than bypassing the ExperienceMemory boundary.

توضیح فارسی:

ExperienceRecord اصلی Runtime توسط PerformanceLearningAdapter تولید می‌شود و مصرف‌کننده مستقیم آن ExperienceMemory است.

پس از ذخیره‌سازی، Experience وارد مسیر Pattern Intelligence و سپس Strategy Learning می‌شود.

بنابراین PatternRecognizer و PatternIntelligence نباید به عنوان Consumer مستقیم Core ExperienceRecord ثبت شوند.

---

# 13. Secondary ExperienceRecord Dependency

Secondary implementation:

intelligence.learning.experience_record.ExperienceRecord

Known consumers:

learning/experience_engine.py
learning/pattern_detector.py

Dependency chain:

Learning Subsystem
↓
intelligence.learning.experience_record.ExperienceRecord
↓
learning/experience_engine.py
learning/pattern_detector.py

توضیح فارسی:

این نسخه در مسیر Learning ثانویه مشاهده شده است.

در Audit فعلی، این Contract هنوز حذف یا Merge نمی‌شود.

وجود Test برای آن به تنهایی به معنی Live Runtime بودن آن نیست.

---

# 14. Experience → Pattern Dependencies

Dependency chain:

ExperienceMemory
↓
PatternRecognizer
↓
PatternCluster
↓
PatternIntelligence

توضیح فارسی:

Pattern Intelligence از Experience ذخیره‌شده تغذیه می‌شود.

در این مسیر باید Context و Strategy Identity حفظ شوند.

Historical identity issue:

TRENDING_BULLISH

توضیح فارسی:

مشکل تاریخی Split کردن کلیدها بر اساس Underscore باعث آسیب‌پذیری برای Contextهای مرکب شده بود.

این مشکل اصلاح شده و Identity کامل باید حفظ شود.

---

# 15. Pattern → Strategy Dependencies

Dependency chain:

PatternIntelligence
↓
StrategyLearner
↓
StrategyMemory

توضیح فارسی:

StrategyLearner وابسته به خروجی Pattern Intelligence است و Strategy یادگرفته‌شده را به StrategyMemory منتقل می‌کند.

---

# 16. Strategy Identity Dependency

Strategy identity must survive:

StrategyLearner
↓
StrategyMemory
↓
StrategyRecall
↓
StrategyRanker
↓
StrategySelector
↓
Decision

توضیح فارسی:

هویت Strategy یک Dependency معماری در سراسر این زنجیره است.

اگر Strategy در یکی از این مراحل تغییر شکل دهد یا Identity آن از بین برود، Consumerهای پایین‌دست ممکن است رفتار نادرست داشته باشند.

StrategyBridge provides compatibility/canonicalization where required.

---

# 17. Strategy Memory Dependencies

StrategyMemory is the storage boundary.

Dependency direction:

StrategyLearner
↓
StrategyMemory
↓
StrategyRecall

توضیح فارسی:

StrategyMemory بین Learning و Recall قرار دارد.

StrategyMemory نباید مسئول Ranking یا Selection شود.

---

# 18. Strategy Recall Dependencies

Dependency direction:

StrategyMemory
↓
StrategyRecall
↓
Candidate Strategies

توضیح فارسی:

StrategyRecall مسئول Retrieval است.

انتخاب Champion متعلق به StrategySelector است.

---

# 19. Strategy Ranking Dependencies

Current runtime ranker:

intelligence.learning.strategy_ranker.StrategyRanker

Classification:

LIVE RUNTIME CONTRACT

Owner:

IntelligenceComponents

Construction:

IntelligenceComponents constructs the runtime StrategyRanker.

Dependency chain:

StrategyRecall

↓

intelligence.learning.strategy_ranker.StrategyRanker

↓

StrategySelector

Runtime rule:

StrategyRanker ranks candidate strategies.

StrategySelector consumes the ranking and selects the champion.

The runtime ranker must remain distinct from the alternate root StrategyRanker contract.

توضیح فارسی:

StrategyRanker موجود در مسیر Learning، Contract فعال Runtime است.

این Component توسط IntelligenceComponents ساخته و مالکیت آن در Composition Root قرار دارد.

StrategySelector مصرف‌کننده Ranking است و انتخاب Champion را انجام می‌دهد.

نسخه Root همچنان Contract ثانویه است و نباید بدون تصمیم معماری مستقل جایگزین یا Merge شود.

---

# 20. Alternate StrategyRanker Dependency

Alternate implementation:

intelligence.strategy_ranker.StrategyRanker

Classification:

SECONDARY CONTRACT

Known architectural distinction:

The root implementation exposes a richer ranking-result contract.

Current runtime status:

It is not constructed by the current Composition Root.

It is not the authoritative runtime StrategyRanker.

Replacement, wrapping, or migration requires explicit:

Producer analysis

Consumer analysis

Contract compatibility analysis

State / ownership validation

Until such a decision is made, the alternate implementation must remain separate.

توضیح فارسی:

نسخه Root یک Contract ثانویه است.

این نسخه در Composition Root فعلی ساخته نمی‌شود و StrategyRanker فعال Runtime محسوب نمی‌شود.

هرگونه Replacement، Wrapper یا Migration باید پس از بررسی Producer، Consumer، Compatibility و Ownership انجام شود.

تا آن زمان این Contract نباید حذف یا با نسخه Runtime ادغام شود.

---

# 21. Strategy Selection Dependencies

Dependency direction:

StrategyRecall
↓
StrategyRanking
↓
StrategySelector
↓
Champion Strategy

توضیح فارسی:

StrategySelector مصرف‌کننده Ranking است و Champion را انتخاب می‌کند.

Ranker و Selector دو مسئولیت مستقل دارند.

---

# 22. Decision Gate Dependency

Current gate:

DecisionRules

Dependency direction:

StrategySelector
↓
Champion Strategy
↓
DecisionRules
↓
Decision Gate
↓
Validated Decision

توضیح فارسی:

DecisionRules مرز فعلی Gate است.

این Gate باید تا زمان تصمیم معماری جدید حفظ و Reuse شود.

ساختن Gate موازی بدون نیاز معماری مشخص ممنوع است.

---

# 23. Strategy Evolution Dependencies

Primary evolution dependency chain:

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

Possible decisions:

KEEP
RETIRE
IMPROVE

توضیح فارسی:

Strategy Evolution از Performance Strategy تغذیه می‌شود.

بعد از تحلیل Performance، تصمیم Evolution گرفته می‌شود، Governance آن را کنترل می‌کند و نتیجه دوباره وارد StrategyMemory می‌شود.

---

# 24. StrategyEvolutionFlow Dependencies

StrategyEvolutionFlow coordinates:

* performance analysis
* evolution decision
* governance
* strategy evolution
* strategy memory

Known constructor-level dependencies include:

performance_analyzer
evolution_decision
governance_evolution
governance_gate
governance_memory
governance_recall_flow
governance_intelligent_gate
evolution_memory

توضیح فارسی:

StrategyEvolutionFlow چند Dependency مهم را مستقیماً دریافت می‌کند.

این موارد باید در Auditهای آینده از نظر Ownership و Identity بررسی شوند.

---

# 25. Governance Memory Dependencies

Important distinction:

GovernanceMemory
≠
GovernanceEvolutionMemory

توضیح فارسی:

این دو Memory Contract متفاوت هستند.

نباید صرفاً به دلیل شباهت نام یا حوزه کاری، یکی جایگزین دیگری فرض شود.

---

# 26. Governance Shared Identity

Dependency chain:

GovernanceMemory
↓
GovernanceRecallFlow
↓
GovernanceIntelligentGate

Identity rule:

The same GovernanceMemory instance must be propagated when shared state
is required.

توضیح فارسی:

در مسیر فعال Strategy Evolution، اشتراک GovernanceMemory بررسی و تأیید شده است.

بنابراین در صورت نیاز به State مشترک، همان Instance باید به Recall و Gate منتقل شود.

---

# 27. Governance Recall Construction

Required dependency relationship:

GovernanceRecallFlow
↓
GovernanceMemory

The memory dependency must be supplied through the appropriate
memory contract.

توضیح فارسی:

در Audit مشخص شد که GovernanceRecallFlow باید Memory مربوط به خود را به شکل صحیح دریافت کند.

استفاده از آرگومان اشتباه یا Positional در این نقطه می‌تواند Dependency را به Component دیگری متصل کند.

---

# 28. GovernanceIntelligentGate Dependency

Conceptual dependency:

GovernanceIntelligentGate
↓
GovernanceIntelligence
↓
GovernanceRecall
↓
GovernanceMemory

توضیح فارسی:

GovernanceIntelligentGate برای دسترسی به Governance State از زنجیره Governance Intelligence و Governance Recall استفاده می‌کند.

در صورت نیاز به State مشترک، این زنجیره باید به همان GovernanceMemory متصل باشد.

---

# 29. GovernanceEvolutionMemory Dependency

GovernanceEvolutionMemory is distinct from GovernanceMemory.

Its dependency scope is evolution-specific governance information.

توضیح فارسی:

GovernanceEvolutionMemory برای اطلاعات مخصوص Evolution است و نباید با GovernanceMemory عمومی یکی فرض شود.

---

# 30. Meta Intelligence Dependencies

Primary runtime chain:

Decision
↓
Outcome
↓
Performance Learning
↓
Experience / Pattern
↓
Meta Feedback
↓
MetaIntelligence
↓
MetaLearningEngine
↓
MetaConfidenceAdapter
↓
Next Decision

توضیح فارسی:

Meta Intelligence در سطح بالاتر از Strategy Learning قرار دارد و از اطلاعات حاصل از چرخه Intelligence برای تنظیم رفتار آینده استفاده می‌کند.

---

# 31. Live MetaLearningEngine Dependency

Authoritative runtime contract:

intelligence.meta.meta_learning_engine.MetaLearningEngine

Runtime dependency:

MetaIntelligence
↓
MetaInsight
↓
intelligence.meta.meta_learning_engine.MetaLearningEngine
↓
MetaConfidenceAdapter
↓
IntelligenceFlow

Contract:

learn(meta_insight)

توضیح فارسی:

این نسخه MetaLearningEngine قرارداد فعال Runtime است.

IntelligenceFlow به این Contract وابسته است.

---

# 32. Secondary MetaLearningEngine Dependency

Secondary implementation:

intelligence.learning.meta_learning_engine.MetaLearningEngine

Secondary dependency:

MetaLearningFlow
↓
intelligence.learning.meta_learning_engine.MetaLearningEngine
↓
Secondary Learning Analysis

توضیح فارسی:

این نسخه به مسیر Learning ثانویه تعلق دارد.

یکسان بودن نام Class باعث نمی‌شود Dependency آنها یکی باشد.

تا زمان تصمیم معماری صریح، این دو Contract جدا باقی می‌مانند.

---

# 33. Adaptive Intelligence Dependencies

Current adaptive dependency chain:

MetaInsight
↓
MetaLearningEngine
↓
Confidence Adjustment
↓
MetaConfidenceAdapter
↓
Adaptive Decision Context
↓
Next Decision

توضیح فارسی:

Adaptive Intelligence از خروجی Meta Learning برای تنظیم Context و Confidence تصمیم آینده استفاده می‌کند.

---

# 34. Adaptive Timing Dependency

Current timing:

Previous Knowledge
↓
Adaptive Context
↓
Current Decision

Current-cycle learning occurs later:

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

توضیح فارسی:

بخشی از Adaptive Context قبل از تکمیل Learning چرخه جاری ساخته می‌شود.

این یک Debt معماری است و فعلاً نباید در مرحله مستندسازی یا Contract Freeze تغییر کند.

---

# 35. DecisionMemory Dependency

Dependency:

Decision
↓
DecisionMemory

توضیح فارسی:

DecisionMemory فقط مسئول نگهداری سابقه Decision است.

این Memory با ExperienceMemory، StrategyMemory، GovernanceMemory و MetaMemory متفاوت است.

---

# 36. Memory Dependency Map

DecisionMemory
→ Decision history

ExperienceMemory
→ Contextual learning experience

StrategyMemory
→ Learned strategy knowledge

GovernanceMemory
→ Governance state/history

GovernanceEvolutionMemory
→ Evolution-specific governance memory

MetaMemory
→ Meta-level feedback/history

توضیح فارسی:

هر Memory یک مسئولیت معنایی مشخص دارد.

این Memoryها نباید صرفاً به دلیل اینکه همگی Storage هستند، interchangeable در نظر گرفته شوند.

---

# 37. Core Runtime Dependency Chain

Market

↓

IntelligenceFlow

↓

Decision

↓

DecisionOutcomeBridge

↓

OutcomeRecord

↓

Performance Learning

↓

PerformanceLearningAdapter

↓

intelligence.experience_record.ExperienceRecord

↓

ExperienceMemory

↓

PatternIntelligence

↓

StrategyLearner

↓

StrategyMemory

↓

StrategyRecall

↓

intelligence.learning.strategy_ranker.StrategyRanker

↓

StrategySelector

↓

DecisionRules

↓

Validated Decision

توضیح فارسی:

این زنجیره وابستگی اصلی Core Runtime را از Market تا Decision معتبر نشان می‌دهد.

در این نسخه Contractهای مهم Outcome، ExperienceRecord و StrategyRanker نیز در زنجیره صریحاً ثبت شده‌اند تا Dependency Map با Contract Ledger و Data Flow یکسان باقی بماند.

---

# 38. Learning Dependency Chain

Decision
↓
DecisionOutcomeBridge
↓
PerformanceLearningAdapter
↓
ExperienceRecord
↓
ExperienceMemory
↓
PatternIntelligence
↓
StrategyLearner
↓
StrategyMemory
↓
StrategyRecall
↓
StrategyRanking
↓
StrategySelector
↓
Decision

توضیح فارسی:

این زنجیره، مسیر اصلی یادگیری و بازگشت دانش Strategy به Decision بعدی را نشان می‌دهد.

---

# 39. Evolution Dependency Chain

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
↓
Strategy Recall
↓
Strategy Ranking
↓
Strategy Selection

توضیح فارسی:

Evolution یک مسیر موازی اما متصل به Strategy Intelligence است.

نتیجه Evolution در نهایت دوباره وارد Strategy Knowledge می‌شود.

---

# 40. Meta Dependency Chain

## Meta Intelligence Dependencies

### Main Runtime Dependency Chain

```text
DecisionMemory
    ↓
MetaIntelligence
    ↓
MetaInsight
    ↓
MetaLearningEngine.learn()
    ↓
Meta Learning Result
    ↓
MetaConfidenceAdapter
    ↓
Adjusted Decision Confidence
    ↓
Next Decision
```

توضیح فارسی:

این Dependency Chain مسیر واقعی Runtime را نشان می‌دهد و باید مرجع اصلی برای Meta Intelligence در نظر گرفته شود.

### Secondary Strategy Meta Dependency Chain

```text
Strategy Context
    ↓
StrategyIntelligenceService
    ↓
MetaLearningFlow
    ↓
learning.MetaLearningEngine.analyze()
    ↓
MetaLearningInsight
    ↓
EnhancedStrategyContext
    ↓
Strategy Intelligence
```

توضیح فارسی:

این Dependency Chain فعال است اما Secondary محسوب می‌شود و نباید با مسیر Runtime Meta اصلی ادغام شود.

### Meta Contract Classification

| Contract                                                        | Classification                                |
| --------------------------------------------------------------- | --------------------------------------------- |
| `intelligence.meta.meta_learning_engine.MetaLearningEngine`     | LIVE                                          |
| `intelligence.learning.meta_learning_engine.MetaLearningEngine` | SECONDARY / ACTIVE STRATEGY INTELLIGENCE PATH |
| `intelligence.meta.meta_learning.MetaLearning`                  | SECONDARY / TEST-BACKED                       |
| `MetaInsight`                                                   | LIVE                                          |
| `MetaLearningInsight`                                           | LIVE WITHIN SECONDARY STRATEGY META PATH      |
| `EnhancedStrategyContext`                                       | LIVE WITHIN SECONDARY STRATEGY META PATH      |
| `MetaLearningFlow`                                              | LIVE SECONDARY                                |
| `StrategyIntelligenceService`                                   | LIVE                                          |

توضیح فارسی:

Classification بر اساس Dependency و Runtime Usage انجام می‌شود، نه صرفاً بر اساس شباهت نام یا محل فایل.

### Adaptive Dependency Precision

```text
Meta Learning Result
→ MetaConfidenceAdapter
→ report.confidence
```

توضیح فارسی:

عبارت Adaptive Decision Context نباید به‌عنوان Consumer مستقیم Meta Learning Result استفاده شود، زیرا Consumer واقعی MetaConfidenceAdapter است.

### Freeze Rule

```text
Runtime Composition
→ Runtime Consumer
→ Producer
→ Contract
→ Tests
→ Historical / Structural Evidence
```

توضیح فارسی:

این سلسله‌مراتب مرجع تصمیم‌گیری Contractهاست. هیچ Duplicate بدون عبور از این سلسله‌مراتب حذف یا ادغام نمی‌شود.

---

# 41. Runtime Contract Classification

### LIVE

* IntelligenceComponents
* IntelligenceFlow
* DecisionRecord
* OutcomeRecord
* PerformanceLearningAdapter
* ExperienceMemory
* intelligence.experience_record.ExperienceRecord
* PatternIntelligence
* StrategyLearner
* StrategyMemory
* StrategyRecall
* intelligence.learning.strategy_ranker.StrategyRanker
* StrategySelector
* DecisionRules
* GovernanceMemory
* intelligence.meta.meta_learning_engine.MetaLearningEngine

توضیح فارسی:

این موارد در وضعیت فعلی به عنوان Dependencyهای اصلی Runtime شناخته شده‌اند.


---

# 42. Dependency Audit Rules

Every dependency audit should answer:

1. Who constructs the dependency?
2. Who owns the dependency?
3. Who consumes the dependency?
4. Is the dependency stateful?
5. Is object identity shared?
6. Is the dependency runtime or secondary?
7. Is the contract compatible?
8. Can replacement occur without breaking downstream consumers?

توضیح فارسی:

هر Dependency Audit باید علاوه بر Import، Ownership و Runtime Usage را بررسی کند.

صرف اینکه یک Module یک Class را Import کرده باشد، برای تعیین Contract Authority کافی نیست.

---

# 43. Duplicate Contract Rule

Duplicate contracts must not be removed solely because:

* names are identical
* implementations look similar
* tests exist
* one path appears older

توضیح فارسی:

هیچ Duplicate Contractی فقط به دلیل نام مشابه، شباهت Implementation، وجود Test یا قدیمی به نظر رسیدن مسیر نباید حذف شود.

ابتدا باید Runtime Dependency و Producer → Consumer Chain مشخص شود.

---

# 44. State Identity Rule

When a stateful dependency is shared:

Owner
↓
Shared Instance
↓
Consumer A
↓
Consumer B

object identity must be preserved when semantic state continuity is
required.

توضیح فارسی:

اگر State بین چند Consumer مشترک است، باید همان Instance منتقل شود.

ساخت دو Instance جدا حتی با Configuration یکسان می‌تواند State را از هم جدا کند و رفتار Runtime را تغییر دهد.

---

# 45. Compatibility Rule

Existing compatibility aliases or wrappers must remain until the
replacement contract is explicitly validated.

توضیح فارسی:

Compatibility نباید قبل از اعتبارسنجی Contract جدید حذف شود.

Alias یا Wrapper ممکن است برای حفظ قراردادهای قدیمی لازم باشد.

---

# 46. Audit Boundary

This dependency map represents the known CURRENT runtime dependency
architecture.

It does not claim that every repository dependency belongs to the core
runtime.

Future audits should inspect changes incrementally.

Recommended audit path:

Current Dependency Map
→ Changed Component
→ Changed Dependency
→ Runtime Consumer
→ Contract Impact
→ Targeted Validation

توضیح فارسی:

این فایل فقط Dependencyهای شناخته‌شده Core Runtime را ثبت می‌کند.

هر Dependency خارج از این Map باید ابتدا از نظر Runtime Usage بررسی شود.

Auditهای آینده باید Delta-based باشند و فقط Dependencyهای تغییرکرده را بررسی کنند.

---

# 47. Current Status

Architecture Phase:

V5 Contract / Architecture Audit

Latest Known Regression:

612 passed

Latest Commit:

eebf7a1

Latest Tag:

v5-contract-architecture-audit

توضیح فارسی:

این Dependency Map بر اساس آخرین وضعیت تأییدشده معماری تهیه شده است.

هر تغییر مهم در Ownership، Composition Root، Contract یا Shared State باید باعث بازبینی این فایل شود.

---

# 48. Architecture Dependency Chain Record

The current dependency architecture can be summarized as:

IntelligenceComponents
→ IntelligenceFlow
→ Decision
→ Outcome
→ Performance Learning
→ ExperienceMemory
→ PatternIntelligence
→ StrategyLearner
→ StrategyMemory
→ StrategyRecall
→ StrategyRanking
→ StrategySelector
→ DecisionRules
→ Validated Decision

Parallel:

Strategy Performance
→ Evolution
→ Governance
→ Strategy Memory

Meta:

Experience / Pattern
→ MetaIntelligence
→ MetaLearningEngine
→ Confidence Adaptation
→ Next Decision

توضیح فارسی:

این Chain Record خلاصه Dependency Architecture فعلی است.

در Auditهای آینده می‌توان از همین Chain شروع کرد و فقط بخش‌هایی را که Dependency آنها تغییر کرده است دوباره بررسی کرد.
