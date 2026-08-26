# EGAH Implementation Plan
## Evidence-Governed Agent Harnesses - Production Implementation Strategy

**Version:** 1.0  
**Date:** August 26, 2026  
**Status:** Implementation Planning

---

## Executive Summary

This document provides a comprehensive implementation plan for building a production-ready Evidence-Governed Agent Harness (EGAH) proof-of-concept. The plan covers technology stack selection, architecture design, phased implementation approach, effort estimation, and demo scenarios to validate the core EGAH concepts.

**Core EGAH Principle:** Observability tells us what happened. EGAH determines whether what happened is still sufficient evidence for what the agent is about to do.

---

## 1. Technology Stack Recommendations

### 1.1 Core Agent Orchestration Framework

**Primary Choice: LangGraph (Python)**

**Rationale:**
- Native support for stateful, graph-based agent execution
- Built-in checkpointing and persistence mechanisms
- Strong integration with LangChain ecosystem
- Active development and community support
- Python ecosystem dominance in AI/ML

**Alternative: LangGraph.js (TypeScript)**
- Consider if team has stronger TypeScript background
- Similar capabilities to Python version
- Better for web-native deployments

### 1.2 Durable State Storage

**Primary Choice: PostgreSQL + pgvector**

**Rationale:**
- Proven relational database with ACID guarantees
- pgvector extension for vector similarity searches
- Excellent for structured evidence envelope storage
- Strong JSON support for flexible schema evolution
- Mature tooling and operational expertise

**Schema Requirements:**
- `execution_state` table: Graph state, checkpoints, recovery state
- `evidence_envelopes` table: Evidence records with provenance, validity, verification
- `verification_history` table: Audit trail of all verification decisions
- `capability_boundaries` table: Task classification and model routing rules
- `resource_accounting` table: Token usage, compute costs, outcome attribution

**Alternative: Redis + PostgreSQL Hybrid**
- Redis for hot state/caching (fast access)
- PostgreSQL for durable evidence storage
- Useful for high-throughput scenarios

### 1.3 Vector Database for Evidence Retrieval

**Primary Choice: Qdrant**

**Rationale:**
- High-performance vector similarity search
- Built-in filtering capabilities (critical for evidence validity queries)
- Self-hosted option for data privacy
- Strong Python SDK
- Efficient for evidence freshness queries

**Alternative: Weaviate**
- More feature-rich but higher complexity
- Built-in vectorization capabilities
- Consider if advanced filtering needed

### 1.4 LLM Providers

**Small Model (8B):**
- **Llama 3.1 8B** (via Ollama for local deployment)
- **Mistral 7B** (via Mistral API or local)
- **Phi-3 Mini** (via Azure or local)

**Frontier Model:**
- **GPT-4o** (OpenAI) - Primary choice for escalation
- **Claude 3.5 Sonnet** (Anthropic) - Alternative
- **Gemini 1.5 Pro** (Google) - Alternative

**Rationale:** Multi-provider support enables capability boundary demonstrations and cost optimization.

### 1.5 Observability Integration

**Primary Choice: OpenTelemetry + Langfuse**

**Rationale:**
- OpenTelemetry: Industry-standard telemetry collection
- Langfuse: Specialized for LLM/agent observability
- Strong integration with LangGraph
- Cost tracking, evaluation, and tracing capabilities
- Aligns with EGAH principle (observability as separate layer)

**Configuration:**
- Export traces to Langfuse via OTLP
- Capture: model calls, tool invocations, tokens, latency, costs
- Custom spans for evidence checkpoints and verification decisions

**Alternative: Phoenix (Arize)**
- Excellent for LLM observability
- Strong evaluation capabilities
- Consider if advanced tracing needed

### 1.6 Message Queue for Async Operations

**Primary Choice: RabbitMQ**

**Rationale:**
- Mature, reliable message broker
- Excellent for evidence validation workflows
- Supports delayed queues (evidence freshness checks)
- Strong Python client (pika)

**Alternative: Redis Streams**
- Simpler setup
- Built-in to Redis if already using
- Good for lighter workloads

### 1.7 API Layer

**Primary Choice: FastAPI (Python)**

**Rationale:**
- Native async support
- Automatic OpenAPI documentation
- Strong validation with Pydantic
- Excellent for agent harness APIs
- Easy integration with LangGraph

**Endpoints to Implement:**
- `POST /agent/execute` - Submit agent task
- `GET /agent/state/{run_id}` - Query execution state
- `GET /evidence/{evidence_id}` - Retrieve evidence envelope
- `POST /agent/crash` - Simulate crash (for demo)
- `POST /agent/recover/{run_id}` - Trigger recovery
- `GET /metrics/checkpoint-overhead` - Performance metrics

### 1.8 Frontend Demo Interface

**Primary Choice: Next.js + shadcn/ui + TailwindCSS**

**Rationale:**
- Modern React framework with excellent DX
- shadcn/ui: Beautiful, accessible components
- Real-time updates via WebSocket/SSE
- Strong TypeScript support
- Easy deployment (Vercel, etc.)

**Key Views:**
- Agent execution visualization (graph view)
- Evidence envelope inspector
- Step-by-step execution timeline
- Crash simulation and recovery demo
- Capability boundary visualization
- Resource accounting dashboard

### 1.9 Containerization and Deployment

**Primary Choice: Docker + Docker Compose**

**Rationale:**
- Consistent development and production environments
- Easy service orchestration
- All-in-one demo setup

**Services:**
- egah-core (LangGraph agent harness)
- egah-api (FastAPI)
- egah-frontend (Next.js)
- postgres (state storage)
- qdrant (vector DB)
- rabbitmq (message queue)
- ollama (local LLM serving)

**Production Consideration: Kubernetes**
- For scalable production deployment
- Consider after PoC validation

---

## 2. Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         EGAH RUNTIME                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         DURABLE EXECUTION STATE LAYER                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Graph State │  │ Checkpoints │  │ Memory      │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         DURABLE EVIDENCE STATE LAYER                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Evidence    │  │ Verification│  │ Capability  │      │  │
│  │  │ Envelopes   │  │ History    │  │ Boundaries  │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         POLICY / DECISION CONTROL LAYER                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Continue    │  │ Refresh     │  │ Escalate    │      │  │
│  │  │ Abstain     │  │ Verify      │  │ Route Model │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         AGENT EXECUTION ENGINE (LangGraph)               │  │
│  │  Plan → Evidence Checkpoint → Tool → Verify → Update     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ telemetry (OpenTelemetry)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY PLANE                          │
│  OpenTelemetry → Langfuse → Traces • Logs • Metrics • Cost     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Evidence-Enhanced Execution Graph

```python
# LangGraph State with Evidence Integration
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class EvidenceEnvelope(TypedDict):
    evidence_id: str
    timestamp: str
    agent_id: str
    task_id: str
    execution_phase: str
    evidence_type: str
    content: dict
    provenance: dict
    verification_status: str  # pending, verified, failed, stale
    validity_window: dict  # valid_from, valid_until
    resource_consumption: dict
    outcome_attribution: str
    capability_boundary: str  # within, near, beyond

class AgentState(TypedDict):
    # Traditional execution state
    messages: Annotated[list, operator.add]
    graph_state: dict
    checkpoints: list
    
    # EGAH evidence state
    evidence_envelopes: list[EvidenceEnvelope]
    verification_history: list[dict]
    current_boundary: str
    
    # Resource accounting
    token_usage: dict
    compute_cost: float
    outcome_verified: bool

# Evidence Checkpoint Node
def evidence_checkpoint(state: AgentState) -> AgentState:
    """Create evidence envelope before consequential action"""
    envelope = create_evidence_envelope(state)
    verification_result = verify_evidence(envelope)
    
    state["evidence_envelopes"].append(envelope)
    state["verification_history"].append(verification_result)
    
    # Policy decision based on verification
    if verification_result["status"] == "verified":
        return state  # Continue to action
    elif verification_result["status"] == "stale":
        return refresh_evidence(state)
    elif verification_result["status"] == "uncertain":
        return request_human_review(state)
    else:  # failed/unsafe
        return abstain_action(state)

# Build evidence-enhanced graph
workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_node)
workflow.add_node("evidence_checkpoint", evidence_checkpoint)
workflow.add_node("tool_execute", tool_execute_node)
workflow.add_node("verify_result", verify_result_node)
workflow.add_node("update_evidence", update_evidence_node)

workflow.add_edge("plan", "evidence_checkpoint")
workflow.add_edge("evidence_checkpoint", "tool_execute")
workflow.add_edge("tool_execute", "verify_result")
workflow.add_edge("verify_result", "update_evidence")
workflow.add_edge("update_evidence", "plan")  # Loop for multi-step

workflow.set_entry_point("plan")
workflow.set_finish_point("update_evidence")
```

### 2.3 Crash Recovery Architecture

```python
class RecoveryController:
    """Manages evidence-aware crash recovery"""
    
    def recover_from_crash(self, run_id: str, crash_step: int) -> dict:
        # 1. Restore execution state
        execution_state = self.restore_execution_state(run_id)
        
        # 2. Restore evidence state
        evidence_state = self.restore_evidence_state(run_id)
        
        # 3. Restore verification history
        verification_history = self.restore_verification_history(run_id)
        
        # 4. Analyze evidence validity at crash point
        validity_analysis = self.analyze_evidence_validity(
            evidence_state, 
            crash_step
        )
        
        # 5. Determine recovery strategy
        recovery_plan = self.generate_recovery_plan(validity_analysis)
        
        return {
            "execution_state": execution_state,
            "evidence_state": evidence_state,
            "recovery_plan": recovery_plan,
            "can_resume": recovery_plan["safe_to_resume"]
        }
    
    def analyze_evidence_validity(self, evidence_state, crash_step):
        """Check which evidence remains valid after crash"""
        valid_evidence = []
        stale_evidence = []
        revalidation_needed = []
        
        for envelope in evidence_state["envelopes"]:
            if envelope["step"] <= crash_step:
                # Check freshness, external changes, etc.
                if self.is_evidence_still_valid(envelope):
                    valid_evidence.append(envelope)
                else:
                    stale_evidence.append(envelope)
                    revalidation_needed.append(envelope)
        
        return {
            "valid": valid_evidence,
            "stale": stale_evidence,
            "revalidation_required": revalidation_needed
        }
```

### 2.4 Capability Boundary Enforcement

```python
class CapabilityBoundaryEngine:
    """Routes tasks to appropriate models based on evidence"""
    
    def classify_task(self, task: dict, evidence_history: list) -> str:
        """Classify task into boundary categories"""
        
        # Analyze task complexity
        complexity = self.assess_complexity(task)
        
        # Check evidence history for similar tasks
        evidence_confidence = self.assess_evidence_confidence(
            task, 
            evidence_history
        )
        
        # Determine boundary
        if complexity <= self.config["small_model_threshold"] and \
           evidence_confidence >= self.config["high_confidence_threshold"]:
            return "within_boundary"
        elif complexity <= self.config["medium_model_threshold"]:
            return "boundary_near"
        else:
            return "beyond_boundary"
    
    def route_model(self, boundary: str) -> str:
        """Route to appropriate model"""
        if boundary == "within_boundary":
            return "llama-3.1-8b"  # Small model
        elif boundary == "boundary_near":
            return "llama-3.1-8b-with-verification"  # Small + human review
        else:  # beyond_boundary
            return "gpt-4o"  # Frontier model
```

### 2.5 Resource/Outcome Accounting

```python
class ResourceAccounting:
    """Tracks resource consumption vs verified outcomes"""
    
    def record_consumption(self, run_id: str, consumption: dict):
        """Record token usage, compute, API costs"""
        self.db.insert("resource_accounting", {
            "run_id": run_id,
            "model": consumption["model"],
            "tokens": consumption["tokens"],
            "cost": consumption["cost"],
            "timestamp": datetime.utcnow()
        })
    
    def attribute_outcome(self, run_id: str, outcome: dict):
        """Link resource consumption to verified outcome"""
        total_cost = self.get_total_cost(run_id)
        outcome_value = self.assess_outcome_value(outcome)
        
        roi = {
            "run_id": run_id,
            "total_cost": total_cost,
            "outcome_value": outcome_value,
            "roi_ratio": outcome_value / total_cost if total_cost > 0 else 0,
            "model_used": self.get_primary_model(run_id),
            "verified": outcome["verified"]
        }
        
        self.db.insert("roi_accounting", roi)
```

---

## 3. Implementation Approach

### 3.1 Development Methodology

**Approach:** Incremental, test-driven development with continuous validation

**Principles:**
1. Build core evidence state management first (foundational)
2. Add LangGraph integration (orchestration)
3. Implement crash recovery (critical differentiator)
4. Add capability boundaries (small model routing)
5. Integrate observability (telemetry layer)
6. Build demo interface (visualization)

### 3.2 Core Components Implementation Order

**Phase 1: Foundation (Weeks 1-2)**
1. Database schema design and setup
2. Evidence envelope data model
3. Basic state persistence layer
4. Verification history tracking

**Phase 2: Agent Harness (Weeks 3-4)**
1. LangGraph workflow setup
2. Evidence checkpoint node implementation
3. Tool execution with verification
4. Evidence update mechanism

**Phase 3: Crash Recovery (Weeks 5-6)**
1. Checkpoint persistence
2. Recovery controller implementation
3. Evidence validity analysis
4. Safe resume logic

**Phase 4: Capability Boundaries (Weeks 7-8)**
1. Task classification engine
2. Evidence confidence assessment
3. Model routing logic
4. Small model integration (Ollama)

**Phase 5: Observability (Week 9)**
1. OpenTelemetry instrumentation
2. Langfuse integration
3. Custom evidence spans
4. Resource tracking

**Phase 6: Demo Interface (Weeks 10-11)**
1. FastAPI backend
2. Next.js frontend
3. Real-time execution visualization
4. Evidence inspector UI

**Phase 7: Testing & Refinement (Week 12)**
1. Integration testing
2. Performance benchmarking
3. Demo scenario validation
4. Documentation

---

## 4. Effort Estimation

### 4.1 Resource Requirements

**Team Composition:**
- 1 Senior AI Engineer (LangGraph/LLM expertise) - Full-time
- 1 Backend Engineer (Python/FastAPI/PostgreSQL) - Full-time
- 1 Frontend Engineer (React/Next.js) - Part-time (Weeks 10-12)
- 1 DevOps Engineer (Docker/Deployment) - Part-time (Weeks 11-12)

**Total Duration:** 12 weeks (3 months)

### 4.2 Effort Breakdown by Phase

| Phase | Duration | Key Deliverables | Complexity |
|-------|----------|------------------|------------|
| Phase 1: Foundation | 2 weeks | DB schema, evidence models, persistence | Medium |
| Phase 2: Agent Harness | 2 weeks | LangGraph workflow, evidence checkpoints | High |
| Phase 3: Crash Recovery | 2 weeks | Recovery controller, validity analysis | High |
| Phase 4: Capability Boundaries | 2 weeks | Task classification, model routing | Medium |
| Phase 5: Observability | 1 week | OTel integration, Langfuse setup | Low |
| Phase 6: Demo Interface | 2 weeks | API, frontend, visualization | Medium |
| Phase 7: Testing & Refinement | 1 week | Testing, benchmarking, docs | Medium |

**Total Effort:** ~12 person-weeks (assuming 1 full-time engineer)

### 4.3 Complexity Assessment

**Highest Complexity Areas:**
1. Evidence validity analysis algorithms (requires domain logic)
2. Crash recovery state reconstruction (edge cases)
3. Real-time execution visualization (WebSocket handling)

**Medium Complexity:**
1. LangGraph workflow design
2. Database schema for evidence envelopes
3. Model routing logic

**Lower Complexity:**
1. Observability integration (well-established patterns)
2. API layer (standard CRUD)
3. Basic UI components

---

## 5. Proof of Concept Scope

### 5.1 Demo Scenario: Multi-Step Document Analysis Workflow

**Scenario Description:**
An agent analyzes a complex document across multiple steps, with a simulated crash at step 40/60, demonstrating evidence-aware recovery.

**Workflow Steps:**
1. **Step 1-10:** Document ingestion and parsing
2. **Step 11-20:** Entity extraction and classification
3. **Step 21-30:** Relationship mapping between entities
4. **Step 31-40:** Risk assessment (CRASH HERE)
5. **Step 41-50:** Recommendation generation
6. **Step 51-60:** Final report generation

**Evidence Checkpoints at:**
- Step 10: Document parsing complete
- Step 20: Entity extraction verified
- Step 30: Relationship mapping validated
- Step 40: Risk assessment (crash point)
- Step 50: Recommendations verified

### 5.2 Demo Features

**Feature 1: Normal Execution (Baseline)**
- Show traditional agent execution without evidence
- Highlight what state is preserved
- Demonstrate limitation: evidence not tracked

**Feature 2: Evidence-Enhanced Execution**
- Show EGAH execution with evidence checkpoints
- Visualize evidence envelopes at each checkpoint
- Display verification history

**Feature 3: Crash Simulation**
- Trigger crash at step 40
- Show system state at crash point
- Display evidence state at crash

**Feature 4: Traditional Recovery (Comparison)**
- Restore only execution state
- Attempt to continue
- Highlight missing evidence context
- Show potential risks

**Feature 5: Evidence-Governed Recovery**
- Restore execution + evidence state
- Analyze evidence validity
- Identify stale evidence
- Revalidate where necessary
- Safe resume with full context

**Feature 6: Capability Boundary Demo**
- Show task classification
- Route simple tasks to 8B model
- Route complex tasks to GPT-4o
- Show cost comparison
- Display outcome verification

**Feature 7: Resource Accounting Dashboard**
- Show token usage by model
- Display cost per task
- Show outcome attribution
- Compare small vs large model ROI

### 5.3 Success Criteria

**Technical Success:**
- Evidence state correctly persisted across crashes
- Recovery controller accurately identifies stale evidence
- Capability boundary classification works for demo tasks
- Observability correctly traces evidence checkpoints
- Demo interface shows real-time execution

**Demonstration Success:**
- Clear visual distinction between traditional vs evidence-governed recovery
- Measurable performance impact (checkpoint overhead)
- Cost comparison between small and large models
- Compelling evidence of value proposition

### 5.4 Metrics to Capture

**Performance Metrics:**
- Evidence checkpoint overhead (latency added)
- Recovery time (traditional vs evidence-governed)
- Throughput impact

**Functional Metrics:**
- Evidence validity detection accuracy
- Recovery success rate
- Capability boundary classification accuracy

**Cost Metrics:**
- Token usage (small vs large model)
- Cost savings from small model routing
- ROI ratio (outcome value / cost)

---

## 6. Technology Stack Summary

### 6.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Agent Orchestration | LangGraph | Latest | Graph-based agent execution |
| Language | Python | 3.11+ | Core implementation |
| State Storage | PostgreSQL | 16+ | Durable execution + evidence state |
| Vector Extension | pgvector | Latest | Evidence similarity search |
| Vector DB | Qdrant | Latest | Evidence retrieval |
| LLM (Small) | Llama 3.1 8B | Latest | Local inference via Ollama |
| LLM (Frontier) | GPT-4o | Latest | Escalation model |
| Observability | OpenTelemetry | Latest | Telemetry collection |
| Observability Platform | Langfuse | Latest | LLM-specific observability |
| API Framework | FastAPI | Latest | REST API layer |
| Frontend Framework | Next.js | 14+ | Demo interface |
| UI Components | shadcn/ui | Latest | Pre-built components |
| Styling | TailwindCSS | Latest | Utility-first CSS |
| Message Queue | RabbitMQ | Latest | Async evidence validation |
| Containerization | Docker | Latest | Service orchestration |
| Local LLM Serving | Ollama | Latest | Local model inference |

### 6.2 Development Tools

| Tool | Purpose |
|------|---------|
| pytest | Unit testing |
| pytest-asyncio | Async test support |
| black | Code formatting |
| ruff | Linting |
| mypy | Type checking |
| docker-compose | Local development |
| pgAdmin | Database management |
| LangSmith | LangChain debugging |

---

## 7. Implementation Roadmap

### 7.1 Week-by-Week Plan

**Week 1: Project Setup & Database Schema**
- Set up development environment
- Design PostgreSQL schema
- Implement evidence envelope data models
- Set up Docker Compose for local development
- Create base repository structure

**Week 2: Evidence State Layer**
- Implement evidence envelope CRUD operations
- Build verification history tracking
- Create evidence validity checking logic
- Write unit tests for evidence models
- Set up database migrations

**Week 3: LangGraph Integration**
- Set up basic LangGraph workflow
- Implement plan node
- Create tool execution node
- Integrate with PostgreSQL state storage
- Add basic checkpointing

**Week 4: Evidence Checkpoints**
- Implement evidence checkpoint node
- Add verification logic
- Create evidence update mechanism
- Integrate evidence state into workflow
- Test multi-step execution

**Week 5: Crash Recovery Foundation**
- Implement checkpoint persistence
- Create recovery controller skeleton
- Add execution state restoration
- Implement crash simulation mechanism

**Week 6: Evidence-Aware Recovery**
- Implement evidence state restoration
- Build evidence validity analysis
- Add revalidation logic
- Implement safe resume decision
- Test recovery scenarios

**Week 7: Capability Boundaries - Part 1**
- Implement task complexity assessment
- Create evidence confidence scoring
- Build task classification engine
- Define boundary thresholds

**Week 8: Capability Boundaries - Part 2**
- Integrate Ollama for local 8B model
- Implement model routing logic
- Add GPT-4o integration for escalation
- Test capability boundary scenarios
- Measure cost differences

**Week 9: Observability Integration**
- Install and configure OpenTelemetry
- Add instrumentation to LangGraph
- Integrate with Langfuse
- Create custom evidence spans
- Add resource tracking

**Week 10: API Layer**
- Set up FastAPI project
- Implement agent execution endpoint
- Add state query endpoints
- Create evidence retrieval endpoints
- Add crash simulation endpoints

**Week 11: Frontend Development**
- Set up Next.js project
- Create agent execution visualization
- Build evidence envelope inspector
- Implement crash/recovery demo UI
- Add capability boundary visualization
- Create resource accounting dashboard

**Week 12: Integration & Polish**
- End-to-end integration testing
- Performance benchmarking
- Demo scenario refinement
- Documentation
- Deployment preparation

---

## 8. Risk Assessment & Mitigation

### 8.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LangGraph learning curve | Medium | Medium | Allocate time for POC, use LangSmith for debugging |
| Evidence validity complexity | High | High | Start with simple time-based validity, evolve |
| Crash recovery edge cases | Medium | High | Extensive testing with various crash scenarios |
| Small model performance | Medium | Medium | Have fallback to GPT-4o, tune thresholds |
| Observability overhead | Low | Low | Configure sampling, optimize span creation |

### 8.2 Project Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Medium | High | Strict adherence to PoC scope, defer features |
| Timeline overruns | Medium | Medium | Buffer time in estimates, prioritize features |
| Demo complexity | Low | Medium | Simplify demo scenario if needed |
| Integration issues | Medium | Medium | Early integration testing, mock services |

---

## 9. Success Metrics

### 9.1 Technical Metrics

- Evidence checkpoint overhead < 100ms per checkpoint
- Recovery time < 5 seconds for 60-step workflow
- Evidence validity detection accuracy > 90%
- Capability boundary classification accuracy > 85%

### 9.2 Demo Metrics

- Clear visual evidence of value proposition
- Measurable cost savings from small model routing (>30%)
- Successful demonstration of crash recovery superiority
- Compelling observability integration

### 9.3 Project Metrics

- On-time delivery (12 weeks)
- All core features implemented
- Demo runs without errors
- Documentation complete

---

## 10. Next Steps

### 10.1 Immediate Actions

1. **Environment Setup**
   - Set up development machine with required tools
   - Create repository structure
   - Configure Docker Compose

2. **Schema Finalization**
   - Review and finalize PostgreSQL schema
   - Define evidence envelope structure
   - Plan indexing strategy

3. **LangGraph POC**
   - Build simple LangGraph workflow
   - Test with basic agent task
   - Validate integration approach

4. **Team Alignment**
   - Review implementation plan with team
   - Assign responsibilities
   - Set up communication channels

### 10.2 Decision Points

**Week 2 Decision:** Confirm evidence envelope schema is sufficient for demo needs

**Week 4 Decision:** Validate LangGraph approach meets requirements

**Week 6 Decision:** Confirm crash recovery complexity is manageable

**Week 8 Decision:** Validate small model performance for demo tasks

**Week 10 Decision:** Confirm demo interface approach

---

## 11. Appendix

### 11.1 Evidence Envelope Schema

```sql
CREATE TABLE evidence_envelopes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id VARCHAR(255) UNIQUE NOT NULL,
    run_id UUID NOT NULL REFERENCES execution_state(id),
    step_number INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    agent_id VARCHAR(255),
    task_id VARCHAR(255),
    execution_phase VARCHAR(100),
    evidence_type VARCHAR(100),
    content JSONB NOT NULL,
    provenance JSONB,
    verification_status VARCHAR(50) NOT NULL, -- pending, verified, failed, stale
    valid_from TIMESTAMP WITH TIME ZONE,
    valid_until TIMESTAMP WITH TIME ZONE,
    resource_consumption JSONB,
    outcome_attribution VARCHAR(255),
    capability_boundary VARCHAR(50), -- within, near, beyond
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_evidence_run_id ON evidence_envelopes(run_id);
CREATE INDEX idx_evidence_step ON evidence_envelopes(step_number);
CREATE INDEX idx_evidence_status ON evidence_envelopes(verification_status);
CREATE INDEX idx_evidence_validity ON evidence_envelopes(valid_from, valid_until);
```

### 11.2 Verification History Schema

```sql
CREATE TABLE verification_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id UUID NOT NULL REFERENCES evidence_envelopes(id),
    verification_type VARCHAR(100) NOT NULL,
    verification_result VARCHAR(50) NOT NULL, -- passed, failed, stale, uncertain
    verifier VARCHAR(255), -- system, human, model
    verification_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_verification_evidence ON verification_history(evidence_id);
CREATE INDEX idx_verification_timestamp ON verification_history(verification_timestamp);
```

### 11.3 Capability Boundaries Schema

```sql
CREATE TABLE capability_boundaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(255) NOT NULL,
    complexity_threshold FLOAT NOT NULL,
    evidence_confidence_threshold FLOAT NOT NULL,
    boundary_category VARCHAR(50) NOT NULL, -- within, near, beyond
    recommended_model VARCHAR(255) NOT NULL,
    requires_verification BOOLEAN DEFAULT FALSE,
    requires_human_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_boundaries_task_type ON capability_boundaries(task_type);
```

### 11.4 Resource Accounting Schema

```sql
CREATE TABLE resource_accounting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES execution_state(id),
    evidence_id UUID REFERENCES evidence_envelopes(id),
    model VARCHAR(255) NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cost FLOAT NOT NULL,
    latency_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_resource_run_id ON resource_accounting(run_id);
CREATE INDEX idx_resource_model ON resource_accounting(model);
```

---

## Conclusion

This implementation plan provides a comprehensive roadmap for building a production-ready EGAH proof-of-concept. The recommended technology stack leverages modern, well-supported tools that align with the EGAH architecture principles. The phased approach ensures manageable complexity while delivering a compelling demonstration of the core value proposition: **evidence as first-class runtime state for long-running agent execution**.

The 12-week timeline is realistic for a focused team, with clear milestones and success criteria. The demo scenario directly addresses the CFP's core question: "What should survive when an agent crashes at step 40 of 60?" and provides a concrete, visual demonstration of the EGAH advantage over traditional checkpoint-based recovery.

**Key Success Factor:** Maintain focus on the core EGAH principle—evidence as decision-bearing state—rather than expanding into broader governance or observability features. The strength of EGAH is its specific, targeted approach to a critical production problem in long-running agent systems.
