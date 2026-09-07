# Phoenix Genesis — Current Runtime Architecture

## 1. Purpose

This document describes the CURRENT runtime architecture of Phoenix Genesis.

It is an implementation-oriented architecture record.

It is intentionally more detailed than:

docs/phoenix_map.md

but does not attempt to document every class in the repository.

The purpose is to allow future architecture audits to start from the
known runtime structure instead of remapping the repository.

توضیح فارسی:

این فایل نقشه اجرایی فعلی ققنوس است.

جزئیات آن از نقشه جامع معماری بیشتر است، اما قرار نیست فهرست تمام Classهای Repository باشد.

هدف این است که در Auditهای آینده از همین ساختار شناخته‌شده شروع کنیم و مجبور نباشیم کل Repository را دوباره از صفر Map کنیم.

---

# 2. Runtime Entry / Orchestration

## IntelligenceFlow

Primary orchestration boundary:

intelligence.flow.IntelligenceFlow

Responsibilities include coordinating:

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

IntelligenceFlow ارکستریتور اصلی Runtime است.

این Flow اجزای مختلف Intelligence را به یک چرخه اجرایی متصل می‌کند.

بنابراین IntelligenceFlow بیشتر نقش هماهنگ‌کننده دارد تا مالک مستقل تمام Componentها.

IntelligenceFlow is an orchestration boundary.

It should not independently construct duplicate stateful intelligence
components when those components are owned by IntelligenceComponents.

توضیح فارسی:

اگر یک Component دارای State یا Memory در IntelligenceComponents ساخته و مالکیت آن مشخص شده باشد، IntelligenceFlow نباید دوباره یک نسخه مستقل از آن بسازد.

---

# 3. Composition Root

## IntelligenceComponents

Current shared component composition root:

intelligence.components.intelligence_components.IntelligenceComponents

Purpose:

Construct and own shared intelligence components.

توضیح فارسی:

IntelligenceComponents نقطه اصلی ساخت و مالکیت Componentهای مشترک Runtime است.

Primary architectural rule:

A shared/stateful component should have one authoritative owner when
multiple downstream consumers depend on the same state.

توضیح فارسی:

اگر چند مصرف‌کننده به State مشترک یک Component نیاز دارند، باید یک مالک معتبر برای آن Component وجود داشته باشد.

IntelligenceFlow obtains shared components from IntelligenceComponents.

Compatibility aliases may exist in IntelligenceFlow so existing
contracts remain stable.

توضیح فارسی:

IntelligenceFlow Componentهای مشترک را از Composition Root دریافت می‌کند.

برخی Aliasها ممکن است برای حفظ Compatibility قراردادهای قدیمی داخل IntelligenceFlow وجود داشته باشند.

این Aliasها به‌تنهایی به معنی وجود Component دوم نیستند.

---

# 4. Runtime Ownership Model

The ownership hierarchy is:

IntelligenceComponents
↓
IntelligenceFlow
↓
Specialized Flows / Services
↓
Memory / Learning / Intelligence Consumers

توضیح فارسی:

ساختار مالکیت از بالا به پایین است.

IntelligenceComponents مالک ساخت و هویت Componentهای مشترک است.

IntelligenceFlow آنها را برای اجرای چرخه استفاده می‌کند.

Flowها و Serviceهای تخصصی مصرف‌کننده این Componentها هستند.

Specialized services should not silently create independent copies of
stateful shared components.

توضیح فارسی:

Serviceهای تخصصی نباید بدون اطلاع معماری، نسخه مستقل دیگری از Componentهای Stateful مشترک ایجاد کنند.

---

# 5. Primary Decision Runtime

The main decision lifecycle is:

Market Context
↓
Market Analysis
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

این مسیر، جریان اصلی تولید Decision در Runtime است.

داده بازار ابتدا تحلیل می‌شود، سپس Signal، Regime و Risk مشخص می‌شوند و بعد وارد Reasoning و Decision Engine می‌شوند.

در انتها Decision اعتبارسنجی می‌شود و به Action Proposal می‌رسد.

Decision is the boundary between forward intelligence generation and
post-decision learning.

توضیح فارسی:

Decision مرز مهمی بین دو بخش سیستم است.

قبل از Decision، سیستم در حال تولید Intelligence برای تصمیم است.

بعد از Decision، سیستم وارد مرحله Outcome، Performance و Learning می‌شود.

---

# 6. Decision Record

DecisionRecord represents the structured decision produced by the
decision lifecycle.

Conceptual information includes:

* symbol
* timeframe
* regime
* signal
* confidence
* risk
* action
* validation status
* quality
* timestamp

توضیح فارسی:

DecisionRecord قرارداد ساختاریافته‌ای است که نتیجه چرخه تصمیم‌گیری را ثبت می‌کند.

این Record اطلاعات لازم برای فهمیدن اینکه سیستم چه تصمیمی گرفته و در چه Contextی آن را گرفته، نگهداری می‌کند.

DecisionRecord is the source context for downstream outcome tracking.

توضیح فارسی:

DecisionRecord مبنای اصلی برای دنبال کردن Outcome بعد از تصمیم است.

---

# 7. Outcome Boundary

Outcome represents realized market reality after a decision.

The outcome layer is intentionally separated from decision generation.

Primary relationship:

Decision
↓
Outcome

توضیح فارسی:

Decision می‌گوید سیستم چه تصمیمی گرفته است.

Outcome می‌گوید بعد از آن تصمیم، واقعاً چه اتفاقی افتاده است.

این دو مفهوم عمداً از هم جدا هستند.

The outcome is then consumed by performance/learning infrastructure.

This prevents learning components from independently redefining the
market result.

توضیح فارسی:

Learning نباید خودش تعریف مستقلی از نتیجه بازار بسازد.

Outcome باید مرجع واقعیت رخ‌داده باشد و Performance و Learning آن را مصرف کنند.

---

# 8. Outcome Processing

DecisionOutcomeBridge is responsible for bridging decision context into
the outcome/performance learning pipeline.

Conceptual flow:

Decision
↓
DecisionOutcomeBridge
↓
PerformanceLearningAdapter
↓
ExperienceMemory

توضیح فارسی:

DecisionOutcomeBridge نقطه اتصال Decision به مسیر Outcome و Learning است.

در ادامه PerformanceLearningAdapter اطلاعات حاصل‌شده را برای ورود به Experience آماده می‌کند.

The current development/testing flow may contain synthetic outcome
values.

This is documented technical debt and is not considered equivalent to
a production execution/outcome source.

توضیح فارسی:

در مسیر فعلی Development و Testing ممکن است Outcomeهای مصنوعی وجود داشته باشند.

این مورد فقط به عنوان Debt ثبت شده و نباید با منبع واقعی Outcome در Production یکی فرض شود.

---

# 9. Performance Learning

PerformanceLearningAdapter transforms outcome information into a learning
representation suitable for experience storage.

Conceptual responsibility:

Outcome
↓
Performance
↓
Performance Learning
↓
Experience

توضیح فارسی:

PerformanceLearningAdapter نقش پل بین نتیجه واقعی و Experience را دارد.

وظیفه آن تبدیل اطلاعات Outcome و Performance به شکلی است که Learning بتواند آن را ذخیره و استفاده کند.

Performance learning must preserve:

* decision context
* strategy identity
* outcome information
* relevant confidence/risk context

توضیح فارسی:

در این تبدیل نباید Context تصمیم، هویت Strategy، اطلاعات Outcome یا اطلاعات مهم Confidence و Risk از بین برود.

---

# 10. Experience Memory

## Core Runtime ExperienceRecord

Authoritative core runtime contract:

intelligence.experience_record.ExperienceRecord

توضیح فارسی:

این نسخه، قرارداد اصلی ExperienceRecord در Runtime فعلی است.

ExperienceRecord contains contextual learning information including
fields related to:

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

ExperienceRecord علاوه بر نتیجه یادگیری، Context مربوط به تصمیم و Strategy را نیز حمل می‌کند.

ExperienceMemory consumes/stores this runtime experience representation.

توضیح فارسی:

ExperienceMemory این قرارداد را دریافت و نگهداری می‌کند.

---

# 11. Pattern Intelligence

PatternIntelligence consumes learned experience.

Conceptual flow:

ExperienceMemory
↓
PatternRecognizer
↓
PatternCluster
↓
PatternIntelligence

توضیح فارسی:

Pattern Intelligence تجربه‌های ذخیره‌شده را بررسی می‌کند و ساختارها و الگوهای تکرارشونده را استخراج می‌کند.

Pattern intelligence must preserve the complete contextual identity of
the learned strategy.

توضیح فارسی:

در هنگام تبدیل Experience به Pattern، هویت کامل Strategy و Context باید حفظ شود.

Important historical issue:

Pattern keys were previously vulnerable to incorrect splitting when
regime names contained underscores.

This was corrected so composite identity/context is preserved.

توضیح فارسی:

در گذشته شکستن کلیدها بر اساس Underscore می‌توانست مقدارهایی مانند نام Regimeهای مرکب را اشتباه تجزیه کند.

این مشکل اصلاح شده است تا هویت ترکیبی Context حفظ شود.

---

# 12. Strategy Learning

StrategyLearner consumes pattern/experience intelligence and produces
learned strategies.

Conceptual flow:

PatternIntelligence
↓
StrategyLearner
↓
StrategyMemory

توضیح فارسی:

StrategyLearner اطلاعات حاصل از Pattern و Experience را به Strategyهای یادگرفته‌شده تبدیل می‌کند.

Learned strategy identity must remain stable across:

learning
→ storage
→ recall
→ ranking
→ selection

توضیح فارسی:

هویت Strategy نباید در مسیر یادگیری، ذخیره‌سازی، بازیابی، رتبه‌بندی یا انتخاب تغییر کند.

StrategyBridge provides compatibility/canonicalization where strategy
representation differs between contracts.

توضیح فارسی:

وقتی نمایش Strategy بین دو Contract متفاوت باشد، StrategyBridge وظیفه تبدیل یا Canonicalization را بر عهده دارد.

---

# 13. Strategy Memory

StrategyMemory is the persistence boundary for learned strategies.

It separates learned strategy storage from:

* strategy recall
* ranking
* selection
* evolution

توضیح فارسی:

StrategyMemory محل نگهداری Strategyهای یادگرفته‌شده است.

این Memory عمداً از Recall، Ranking، Selection و Evolution جدا نگه داشته می‌شود تا مسئولیت ذخیره‌سازی با تصمیم‌گیری قاطی نشود.

---

# 14. Strategy Recall

StrategyRecall retrieves candidate strategies from StrategyMemory.

Conceptual flow:

StrategyMemory
↓
StrategyRecall
↓
Candidate Strategies

توضیح فارسی:

StrategyRecall فقط Strategyهای مناسب را از Memory بازیابی می‌کند.

Recall مسئول انتخاب Champion نیست.

Recall is retrieval.

Recall does not perform final champion selection.

---

# 15. Strategy Ranking

Two StrategyRanker implementations exist.

### Runtime StrategyRanker

Location:

`intelligence.learning.strategy_ranker.StrategyRanker`

Status:

LIVE RUNTIME CONTRACT

Construction:

IntelligenceComponents

Runtime ownership:

IntelligenceComponents

Runtime consumer:

IntelligenceFlow

Downstream role:

StrategySelector

Runtime path:

StrategyRecall

→ StrategyRanker

→ StrategySelector

توضیح فارسی:

این نسخه قرارداد فعال StrategyRanker در Runtime است.

IntelligenceComponents آن را می‌سازد و IntelligenceFlow همان Instance را دریافت می‌کند.

StrategySelector از این مسیر برای رتبه‌بندی Strategyهای بازیابی‌شده استفاده می‌کند.

---

### Root StrategyRanker

Location:

`intelligence.strategy_ranker.StrategyRanker`

Status:

SECONDARY CONTRACT

Observed characteristics:

The root implementation provides a different and richer ranking-result
contract including:

`rank()`

`rank_with_result()`

`best()`

توضیح فارسی:

این نسخه در Composition Root فعلی ساخته نمی‌شود و در مسیر اصلی Runtime قرار ندارد.

با این حال Contract متفاوتی دارد و صرفاً به دلیل وجود آن در مسیر Root نباید Legacy فرض شود.

Decision:

KEEP SEPARATE

DO NOT MERGE

DO NOT DELETE

Reason:

The two implementations have different ownership, construction paths,
and output contracts.

Future migration or consolidation requires explicit producer/consumer
analysis and compatibility validation.

توضیح فارسی:

نسخه Learning قرارداد Live فعلی است.

نسخه Root فعلاً Secondary است.

در مرحله فعلی هیچ Merge، Delete یا Rename انجام نمی‌شود.


---

# 16. Strategy Selection

StrategySelector performs final strategy selection.

Conceptual flow:

StrategyRecall
↓
StrategyRanking
↓
StrategySelector
↓
Champion Strategy

توضیح فارسی:

StrategySelector مسئول انتخاب نهایی Champion Strategy است.

Important distinction:

Ranker ranks.

Selector selects.

توضیح فارسی:

Ranker فقط رتبه‌بندی می‌کند.

Selector انتخاب می‌کند.

این دو مسئولیت نباید در یک Component ادغام شوند مگر اینکه تصمیم معماری صریحی برای آن گرفته شود.

The selector must not silently become another ranking engine.

---

# 17. Decision Gate

DecisionRules contains the current decision validation/gating logic.

The strategy validity portion checks the selected/champion strategy
contract.

Conceptually:

Strategy Selection
↓
Champion Strategy
↓
Decision Gate
↓
Validated Decision

توضیح فارسی:

DecisionRules مرز فعلی Gate و Validation تصمیم است.

پس از انتخاب Champion، اعتبار Strategy بررسی می‌شود و تصمیم می‌تواند وارد مرحله معتبر بعدی شود.

This existing gate must be reused rather than replaced by introducing
another parallel gate.

توضیح فارسی:

Gate فعلی باید تا زمان تصمیم معماری جدید دوباره استفاده شود.

نباید صرفاً برای حل یک نیاز جدید، یک Gate موازی و تکراری ساخته شود.

---

# 18. Strategy Evolution

Strategy evolution operates downstream of measurable strategy
performance.

Conceptual flow:

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

توضیح فارسی:

Evolution بر اساس Performance قابل اندازه‌گیری Strategy عمل می‌کند.

ابتدا عملکرد تحلیل می‌شود، سپس درباره Evolution تصمیم گرفته می‌شود، Governance آن را کنترل می‌کند و نتیجه به StrategyMemory برمی‌گردد.

Evolution decisions:

KEEP
RETIRE
IMPROVE

StrategyEvolutionFlow coordinates the evolution process.

توضیح فارسی:

StrategyEvolutionFlow جریان Evolution را هماهنگ می‌کند.

---

# 19. Governance Runtime

Governance provides safety/control around sensitive strategy evolution
operations.

Important distinction:

GovernanceMemory
≠
GovernanceEvolutionMemory

توضیح فارسی:

GovernanceMemory و GovernanceEvolutionMemory دو مفهوم و Contract متفاوت هستند.

GovernanceMemory sharing has been verified across the active evolution
flow and related governance recall/intelligent gate components.

Where shared governance state is required, the same memory instance must
be propagated.

توضیح فارسی:

در مسیر فعال Evolution، اشتراک Instance مربوط به GovernanceMemory بررسی و تأیید شده است.

هر جا State مشترک لازم باشد، همان Instance باید به Componentهای وابسته منتقل شود.

---

# 20. Meta Intelligence

## Meta Intelligence — Current Architecture

### Runtime Meta Intelligence

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

این مسیر Meta Intelligence اصلی در Runtime فعلی Phoenix Genesis است.

### Strategy Meta Intelligence

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

این مسیر Secondary اما فعال است و بخشی از Strategy Intelligence محسوب می‌شود.

### State and Ownership

```text
IntelligenceComponents
→ owns shared stateful components
→ IntelligenceFlow consumes shared instances
```

توضیح فارسی:

اصل State Identity همچنان برقرار است. مستندات Meta نباید باعث ایجاد این برداشت شوند که Secondary Meta مسیر دیگری از State Ownership اصلی ایجاد کرده است.

### Meta Contract Status

```text
MetaInsight
→ LIVE

MetaLearningInsight
→ LIVE / SECONDARY PATH

EnhancedStrategyContext
→ LIVE / SECONDARY PATH

MetaLearningFlow
→ LIVE SECONDARY

MetaLearning
→ SECONDARY / TEST-BACKED
```

توضیح فارسی:

MetaLearning به دلیل وجود Contract و Test Coverage فعلاً Legacy محسوب نمی‌شود.

### Architecture Freeze

```text
No destructive cleanup during contract freeze.
```

توضیح فارسی:

در این مرحله هدف تثبیت معماری و Contractهاست، نه پاک‌سازی ساختاری. هر Refactor باید پس از تعیین مرز V5 انجام شود.

---

# 21. Runtime MetaLearningEngine

Authoritative runtime contract:

intelligence.meta.meta_learning_engine.MetaLearningEngine

Primary runtime consumer:

IntelligenceFlow

Contract:

learn(meta_insight)

The current implementation produces information including:

* confidence_adjustment
* reliability

The current adjustment logic is based primarily on MetaInsight
reliability/sample information.

توضیح فارسی:

این نسخه قرارداد فعال MetaLearningEngine در Runtime است.

IntelligenceFlow از متد مشخص‌شده برای دریافت نتیجه Meta Learning استفاده می‌کند.

در حال حاضر Confidence Adjustment عمدتاً بر اطلاعات Reliability و Sample مربوط به MetaInsight متکی است.

This is documented as an architectural observation, not an immediate
refactor requirement.

توضیح فارسی:

این موضوع فعلاً فقط یک مشاهده معماری و Debt مستندشده است و به معنی نیاز فوری به Refactor نیست.

---

# 22. Secondary MetaLearningEngine

A separate implementation exists:

`intelligence.learning.meta_learning_engine.MetaLearningEngine`

Status:

SECONDARY CONTRACT

Contract:

`analyze(knowledge)`

Output:

`MetaLearningInsight`

This implementation belongs to a separate learning-oriented path and is
not constructed by the current IntelligenceComponents composition root.

توضیح فارسی:

این نسخه متعلق به مسیر Learning ثانویه است و در Composition Root فعلی ساخته نمی‌شود.

Contract آن نیز با Runtime MetaLearningEngine متفاوت است.

The authoritative runtime contract remains:

`intelligence.meta.meta_learning_engine.MetaLearningEngine`

Contract:

`learn(meta_insight)`

توضیح فارسی:

نسخه Runtime همچنان Contract اصلی و Live است.

نسخه Learning صرفاً به دلیل نام یکسان Class نباید با آن Merge شود.

Decision:

KEEP SEPARATE

DO NOT MERGE

DO NOT DELETE

Any future migration requires explicit producer/consumer analysis and
compatibility validation.

---

# 23. Adaptive Intelligence

Adaptive intelligence consumes learned context and adjusts future
decision confidence/behavior.

The current architecture includes:

* adaptive confidence context
* MetaConfidenceAdapter
* meta learning
* multi-strategy learning feedback

توضیح فارسی:

Adaptive Intelligence اطلاعات یادگرفته‌شده را برای تغییر رفتار یا Confidence تصمیم‌های آینده استفاده می‌کند.

Important timing observation:

Some adaptive context is calculated before all current-cycle learning
information becomes available.

This is documented debt and should be revisited only when the adaptive
architecture is explicitly redesigned.

توضیح فارسی:

یک مسئله زمانی در معماری فعلی وجود دارد.

بخشی از Adaptive Context قبل از کامل شدن اطلاعات Learning همان چرخه محاسبه می‌شود.

این مورد فعلاً فقط ثبت شده و نباید در مرحله مستندسازی دست‌کاری شود.

---

# 24. Decision Memory

Decision Memory provides historical persistence for decisions and their
associated intelligence context.

Conceptually:

Decision
↓
Decision Memory

توضیح فارسی:

DecisionMemory برای نگهداری سابقه تصمیم‌ها و Context مرتبط با آنها استفاده می‌شود.

Decision memory is distinct from:

* ExperienceMemory
* StrategyMemory
* GovernanceMemory
* MetaMemory

توضیح فارسی:

DecisionMemory با Memoryهای Experience، Strategy، Governance و Meta متفاوت است.

هر Memory مسئولیت معنایی مستقل خود را دارد.

---

# 25. Memory Architecture

The major memory boundaries are:

DecisionMemory
→ decision history

ExperienceMemory
→ contextual learning experience

StrategyMemory
→ learned strategies

GovernanceMemory
→ governance state/history

GovernanceEvolutionMemory
→ evolution-specific governance memory

MetaMemory
→ meta-level feedback/history

توضیح فارسی:

هر Memory یک مرز معنایی مشخص دارد:

DecisionMemory برای سابقه تصمیم است.

ExperienceMemory برای تجربه قابل یادگیری است.

StrategyMemory برای دانش Strategy است.

GovernanceMemory برای State و سابقه Governance است.

GovernanceEvolutionMemory برای اطلاعات Governance مخصوص Evolution است.

MetaMemory برای Feedback و سابقه سطح Meta است.

These should not be treated as interchangeable storage containers.

توضیح فارسی:

این Memoryها جایگزین یکدیگر نیستند و نباید صرفاً به دلیل شباهت فنی، یکی فرض شوند.

---

# 26. Runtime Contract Classification

### LIVE

* IntelligenceComponents
* IntelligenceFlow
* DecisionRecord
* OutcomeRecord
* intelligence.experience_record.ExperienceRecord
* PerformanceLearningAdapter
* ExperienceMemory
* PatternIntelligence
* StrategyLearner
* StrategyMemory
* StrategyRecall
* intelligence.learning.strategy_ranker.StrategyRanker
* StrategySelector
* DecisionRules
* intelligence.meta.meta_learning_engine.MetaLearningEngine

توضیح فارسی:

این موارد در وضعیت فعلی به عنوان Contractها و Componentهای اصلی Runtime شناخته شده‌اند.

### SECONDARY / LEGACY CANDIDATE

* intelligence.learning.experience_record.ExperienceRecord

توضیح فارسی:

این نسخه همچنان در مسیر Learning استفاده می‌شود و تا زمان Audit کامل زیرسیستم Learning، وضعیت آن Secondary / Legacy Candidate باقی می‌ماند.

### SECONDARY

* intelligence.learning.meta_learning_engine.MetaLearningEngine
* intelligence.strategy_ranker.StrategyRanker

توضیح فارسی:

این دو Contract در وضعیت فعلی Secondary هستند.

هر دو مسیر و Contract متفاوتی نسبت به نسخه Live دارند، اما هنوز شواهد کافی برای Legacy بودن قطعی آنها وجود ندارد.

The classification is based on current runtime construction,
ownership, producer/consumer relationships, and downstream usage.

No destructive cleanup is permitted solely because an item is classified
as secondary.

توضیح فارسی:

Secondary بودن به تنهایی مجوز حذف، Merge یا Rename نیست.

هر تصمیم جایگزینی یا حذف باید بر اساس Dependency، Runtime Usage، Contract Compatibility و Producer/Consumer Evidence گرفته شود.

---

# 27. Runtime Safety Rules

1. Shared state requires explicit ownership.

2. Stateful components should not be duplicated accidentally.

3. Producer/consumer relationships define contract authority.

4. Ranker and Selector remain separate responsibilities.

5. Decision and Outcome remain separate semantic boundaries.

6. Experience and Strategy Performance remain distinct concepts.

7. Governance state must preserve required identity across dependent flows.

8. Duplicate contracts require evidence before replacement/removal.

9. Existing Decision Gate logic should be reused instead of duplicated.

10. Compatibility must be preserved until replacement contracts are
    explicitly validated.

توضیح فارسی:

این ده قانون، اصول ایمنی معماری فعلی هستند.

مهم‌ترین آنها عبارت‌اند از:

مالکیت State باید مشخص باشد.

Componentهای Stateful نباید ناخواسته Duplicate شوند.

مرجع Contract باید از Producer و Consumer واقعی مشخص شود.

Ranker و Selector دو مسئولیت متفاوت دارند.

Decision و Outcome دو مفهوم متفاوت هستند.

Experience با Strategy Performance یکی نیست.

در Stateهای مشترک، Identity باید حفظ شود.

Duplicateها بدون مدرک نباید حذف یا جایگزین شوند.

Gate موجود نباید بی‌دلیل دوباره ساخته شود.

و تا زمانی که Contract جدید اعتبارسنجی نشده، Compatibility باید حفظ شود.

---

# 28. Current Runtime Architecture Chain

Decision
→ Outcome
→ Performance Learning
→ Experience Memory
→ Pattern Intelligence
→ Strategy Learner
→ Strategy Memory
→ Strategy Recall
→ Strategy Ranking
→ Strategy Selector
→ Decision

توضیح فارسی:

این زنجیره، چرخه اصلی Learning و Strategy در Runtime فعلی را نشان می‌دهد.

Parallel meta/evolution systems extend this chain:

Strategy Performance
→ Evolution
→ Governance
→ Strategy Memory

Experience / Pattern
→ Meta Intelligence
→ Meta Learning
→ Confidence Adaptation
→ Next Decision

توضیح فارسی:

دو مسیر مهم به این چرخه متصل هستند.

مسیر Evolution، Strategy را بر اساس Performance تغییر می‌دهد.

مسیر Meta، کیفیت Intelligence را بررسی کرده و Confidence آینده را تطبیق می‌دهد.

---

# 29. Audit Boundary

This document describes the known CURRENT runtime architecture.

It does not claim that every repository class belongs to this runtime.

Any component not connected to the runtime chain must be classified
through dependency analysis before being considered part of the core
architecture.

توضیح فارسی:

این فایل فقط معماری Runtime شناخته‌شده را ثبت می‌کند.

وجود یک Class در Repository به معنی عضویت آن در Core Runtime نیست.

هر Component خارج از زنجیره Runtime باید ابتدا از نظر Dependency و Usage بررسی شود.

The next architecture audit should therefore be DELTA-based:

Current Architecture
→ Changed Contract
→ Changed Dependency
→ Runtime Impact
→ Targeted Validation

توضیح فارسی:

Audit بعدی باید فقط روی تغییرات انجام شود.

ابتدا معماری فعلی را می‌خوانیم.

سپس Contract تغییرکرده را پیدا می‌کنیم.

بعد Dependency تغییرکرده و اثر آن روی Runtime را بررسی می‌کنیم.

در نهایت فقط همان بخش را Validation می‌کنیم.

---

# 30. Current Status

Architecture phase:

V5 Contract / Architecture Audit

Latest known regression:

612 passed

Latest commit:

eebf7a1

Latest tag:

v5-contract-architecture-audit

توضیح فارسی:

این فایل باید همیشه نمایانگر وضعیت Runtime در آخرین Checkpoint تأییدشده باشد.

هرگاه یک تغییر معماری مهم نهایی شد، این بخش و Chainهای مربوطه باید بررسی و در صورت نیاز به‌روزرسانی شوند.
