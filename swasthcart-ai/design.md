# SwasthCart AI - System Design Document

## Document Control

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-02-14 | System Architecture Team | Draft |

## Executive Summary

SwasthCart AI is a production-ready, enterprise-grade preventive health intelligence system designed to integrate seamlessly with grocery and quick-commerce platforms (Amazon, Flipkart, BigBasket, Blinkit, Instamart). The system employs a stateful agentic architecture orchestrated via LangGraph, utilizing specialized AI agents, large language models (LLMs), and retrieval-augmented generation (RAG) to deliver personalized, explainable health risk analysis.

The system operates as a plug-and-play extension that overlays health intelligence on existing shopping workflows without requiring modifications to core platform functionality. It supports three deployment models: Browser Extension (MVP), Mobile SDK (Partner Integration), and REST API (Enterprise Integration).

### Core Value Proposition

- Personalized product risk scoring based on user-declared health conditions
- Cart-level health assessment with trend analysis
- RAG-grounded explanations with authoritative source citations
- Safer alternative product recommendations
- Transparent risk breakdown with confidence scoring
- Individual and Family mode support
- User-controlled toggle for privacy and autonomy

### Architectural Paradigm

The system implements a stateful agentic architecture with the following key characteristics:

- **LangGraph Orchestration**: Stateful multi-step reasoning with session memory
- **Specialized Agents**: Eight domain-specific agents with defined responsibilities
- **LLM Integration**: Amazon Bedrock for domain-aware reasoning with structured outputs
- **RAG System**: Vector database retrieval with grounded explanation generation
- **Tool Invocation**: LangChain + MCP framework for dynamic tool access
- **Observability**: AWS X-Ray tracing and CloudWatch logging
- **Guardrails**: Multi-layer safety mechanisms preventing harmful outputs
- **Governance**: Model versioning, drift detection, and A/B testing capability


## 1. Vision and Problem Statement

### 1.1 Vision

To empower consumers with transparent, personalized, and actionable health intelligence at the point of purchase, enabling informed dietary decisions that support preventive health management without requiring medical expertise or disrupting existing shopping workflows.

### 1.2 Problem Statement

Modern consumers face significant challenges in making health-conscious food purchasing decisions:

1. **Information Asymmetry**: Ingredient lists and nutrition labels are complex, technical, and difficult to interpret for non-experts
2. **Personalization Gap**: Generic nutrition information fails to account for individual health conditions (diabetes, hypertension, PCOS, thyroid disorders)
3. **Cognitive Overload**: Evaluating dozens of products across multiple health dimensions during shopping is mentally exhausting
4. **Trust Deficit**: Existing health apps lack transparency in scoring methodology and source citations
5. **Integration Friction**: Standalone health apps require context-switching away from shopping platforms
6. **Family Complexity**: Caregivers managing multiple family members' health needs lack tools for holistic assessment

### 1.3 Solution Approach

SwasthCart AI addresses these challenges through:

- **Contextual Integration**: Overlay health intelligence directly within existing shopping workflows
- **Personalized Risk Assessment**: Condition-specific scoring based on user-declared health profiles
- **Explainable AI**: RAG-grounded explanations with authoritative source citations
- **Actionable Recommendations**: Safer alternative suggestions with quantified health improvements
- **Trust Architecture**: Transparent methodology, confidence scores, and user control mechanisms
- **Scalable Infrastructure**: Production-grade AWS deployment with enterprise reliability


## 2. System Architecture

### 2.1 High-Level Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │  Mobile SDK  │  │  REST API    │          │
│  │  Extension   │  │ (iOS/Android)│  │   Client     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Amazon API Gateway (REST/WebSocket)                     │   │
│  │  - Request validation  - Throttling  - CORS             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Amazon Cognito (Authentication & Authorization)         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LangGraph Orchestrator                                  │   │
│  │  - Stateful workflow engine                              │   │
│  │  - Agent coordination                                    │   │
│  │  - Retry & fallback logic                                │   │
│  │  - Guardrail enforcement                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  State Manager (DynamoDB)                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Ingredient  │  │ Risk Scoring │  │ RAG Retrieval│          │
│  │   Analysis   │  │    Agent     │  │    Agent     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Explanation  │  │     Cart     │  │ Alternative  │          │
│  │  Synthesis   │  │ Aggregation  │  │Recommendation│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │  Validation  │  │    Audit &   │                             │
│  │  & Guardrail │  │    Logging   │                             │
│  └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LLM & RAG LAYER                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Amazon Bedrock (Claude 3 Sonnet/Haiku)                  │   │
│  │  - Structured output generation                          │   │
│  │  - Domain-aware reasoning                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Amazon Titan Embeddings                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Vector DB  │  │  Knowledge   │  │  Session     │          │
│  │ (OpenSearch) │  │  Store (S3)  │  │State (DDB)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐                                                │
│  │    Cache     │                                                │
│  │(ElastiCache) │                                                │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TOOL INVOCATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LangChain + MCP Framework                               │   │
│  │  - Ingredient Normalizer                                 │   │
│  │  - Risk Calculator                                       │   │
│  │  - Alternative Ranker                                    │   │
│  │  - Bias Detector                                         │   │
│  │  - Confidence Estimator                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  OBSERVABILITY LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  AWS X-Ray   │  │  CloudWatch  │  │  CloudWatch  │          │
│  │   (Tracing)  │  │    (Logs)    │  │  (Metrics)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Layers

#### 2.2.1 Client Layer

**Browser Extension (MVP)**
- Chrome/Firefox extension using Manifest V3
- Content scripts inject UI overlays into grocery platform pages
- Background service worker manages API communication
- Local storage for user preferences and session state
- Supports Amazon, Flipkart, BigBasket, Blinkit, Instamart

**Mobile SDK**
- React Native SDK for cross-platform iOS/Android support
- Native UI components for seamless integration
- Offline caching for previously analyzed products
- Push notification support for cart health alerts

**REST API Client**
- HTTP client library for enterprise backend integration
- Webhook support for asynchronous analysis
- Batch processing capability for cart analysis
- Rate limiting and retry logic

#### 2.2.2 API Gateway Layer

**Amazon API Gateway**
- RESTful endpoints for product analysis, cart assessment, user profile management
- WebSocket support for real-time cart updates
- Request validation using JSON Schema
- Throttling: 1000 requests/second per user, 10000 requests/second system-wide
- CORS configuration for browser extension support
- API versioning (v1, v2) for backward compatibility

**Amazon Cognito**
- User pool for authentication
- JWT token validation
- OAuth 2.0 support for enterprise SSO
- MFA support for sensitive operations
- User attribute management (health conditions, preferences)


#### 2.2.3 Orchestration Layer (LangGraph)

**LangGraph Orchestrator**

The orchestrator implements stateful workflow management using LangGraph, a framework for building multi-agent systems with explicit state management and control flow.

**Core Responsibilities:**
- Manage stateful multi-step workflows across agent invocations
- Coordinate agent execution order based on workflow definitions
- Maintain session state and intermediate results
- Implement retry logic with exponential backoff
- Execute fallback strategies when agents fail
- Enforce guardrails at workflow transition points
- Generate execution traces for observability

**State Schema:**

```python
class WorkflowState(TypedDict):
    session_id: str
    user_id: str
    workflow_type: Literal["product_analysis", "cart_analysis", "alternative_search"]
    current_step: str
    timestamp: str
    
    # User context
    user_profile: UserProfile
    
    # Input data
    product_data: Optional[ProductData]
    cart_data: Optional[CartData]
    
    # Intermediate results
    normalized_ingredients: Optional[List[NormalizedIngredient]]
    risk_assessment: Optional[RiskAssessment]
    retrieved_documents: Optional[List[Document]]
    explanation: Optional[Explanation]
    alternatives: Optional[List[Alternative]]
    
    # Output
    final_result: Optional[Dict]
    
    # Metadata
    execution_metadata: ExecutionMetadata
    errors: List[Error]
```

**Workflow Definitions:**

```python
# Product Analysis Workflow
product_workflow = StateGraph(WorkflowState)

# Add nodes (agents)
product_workflow.add_node("ingredient_analysis", ingredient_analysis_agent)
product_workflow.add_node("risk_scoring", risk_scoring_agent)
product_workflow.add_node("rag_retrieval", rag_retrieval_agent)
product_workflow.add_node("explanation_synthesis", explanation_synthesis_agent)
product_workflow.add_node("alternative_recommendation", alternative_recommendation_agent)
product_workflow.add_node("validation", validation_guardrail_agent)
product_workflow.add_node("audit_logging", audit_logging_agent)

# Define edges (workflow transitions)
product_workflow.add_edge("ingredient_analysis", "risk_scoring")
product_workflow.add_edge("risk_scoring", "rag_retrieval")
product_workflow.add_edge("rag_retrieval", "explanation_synthesis")
product_workflow.add_conditional_edge(
    "explanation_synthesis",
    should_recommend_alternatives,  # Condition function
    {
        True: "alternative_recommendation",
        False: "validation"
    }
)
product_workflow.add_edge("alternative_recommendation", "validation")
product_workflow.add_edge("validation", "audit_logging")

# Set entry and exit points
product_workflow.set_entry_point("ingredient_analysis")
product_workflow.set_finish_point("audit_logging")
```

**Retry Strategy:**
- Initial retry delay: 1 second
- Exponential backoff multiplier: 2x
- Maximum retry delay: 8 seconds
- Maximum retry attempts: 3
- Jitter: ±20% to prevent thundering herd

**Fallback Strategy:**
- LLM failure → Rule-based engine
- Vector DB failure → Cached explanations or generic guidance
- Agent failure → Skip optional steps, complete core workflow
- Complete system failure → Return error with partial results

**State Persistence:**
- State snapshots stored in DynamoDB after each agent execution
- TTL: 24 hours for completed workflows, 1 hour for abandoned workflows
- Enables workflow resumption after transient failures
- Supports debugging and audit trail reconstruction



#### 2.2.4 Agent Layer

The Agent Layer implements eight specialized agents, each with defined responsibilities, input/output schemas, and tool invocation patterns. Agents are stateless functions that receive workflow state and return updated state.

**Agent Design Principles:**
- Single Responsibility: Each agent handles one domain-specific task
- Stateless Execution: Agents do not maintain internal state between invocations
- Structured I/O: All inputs and outputs conform to Pydantic schemas
- Tool Composition: Agents orchestrate tool invocations via LangChain
- Error Handling: Agents return structured errors for orchestrator handling
- Observability: All agent executions emit structured logs and traces

**Agent Catalog:**

1. **Ingredient Analysis Agent**: Normalizes and categorizes ingredients
2. **Risk Scoring Agent**: Calculates condition-specific risk scores
3. **RAG Retrieval Agent**: Retrieves relevant health knowledge documents
4. **Explanation Synthesis Agent**: Generates human-readable explanations
5. **Cart Aggregation Agent**: Performs cart-level health assessment
6. **Alternative Recommendation Agent**: Identifies safer product alternatives
7. **Validation & Guardrail Agent**: Enforces safety and quality checks
8. **Audit & Logging Agent**: Records execution traces and user interactions

Detailed agent specifications are provided in Section 4.


#### 2.2.5 LLM & RAG Layer

**Amazon Bedrock Integration**

The system utilizes Amazon Bedrock for LLM access with the following configuration:

- **Primary Model**: Claude 3 Sonnet (claude-3-sonnet-20240229)
  - Use case: Complex reasoning, explanation synthesis, alternative recommendations
  - Max tokens: 4096
  - Temperature: 0.3 (deterministic outputs for consistency)
  - Top-p: 0.9

- **Secondary Model**: Claude 3 Haiku (claude-3-haiku-20240307)
  - Use case: Ingredient normalization, simple classification tasks
  - Max tokens: 2048
  - Temperature: 0.1
  - Top-p: 0.95

**Structured Output Generation:**
- All LLM responses use JSON mode with Pydantic schema validation
- Function calling for tool invocation
- Retry logic for malformed outputs (max 2 retries)

**Prompt Engineering Strategy:**
- System prompts define agent persona and constraints
- Few-shot examples for consistent output formatting
- Chain-of-thought prompting for complex reasoning
- Explicit safety instructions to prevent harmful outputs

**Amazon Titan Embeddings:**
- Model: amazon.titan-embed-text-v1
- Embedding dimension: 1536
- Use case: Document and query embedding for RAG retrieval
- Batch size: 25 documents per API call


#### 2.2.6 Data Layer

**Vector Database (Amazon OpenSearch Service)**

- **Index Schema:**
  - Document ID (UUID)
  - Embedding vector (1536 dimensions)
  - Document text (full content)
  - Metadata: source, publication_date, authority_score, condition_tags
  - Document type: research_paper, clinical_guideline, nutrition_database

- **Index Configuration:**
  - Engine: k-NN with HNSW algorithm
  - Distance metric: Cosine similarity
  - Shards: 3 primary, 1 replica
  - Refresh interval: 30 seconds

- **Query Strategy:**
  - Hybrid search: Vector similarity + keyword matching
  - Top-k retrieval: 10 documents
  - Re-ranking: Authority score and recency weighting
  - Filtering: Condition-specific document filtering

**Knowledge Store (Amazon S3)**

- **Bucket Structure:**
  - `swasthcart-knowledge-base/research-papers/`
  - `swasthcart-knowledge-base/clinical-guidelines/`
  - `swasthcart-knowledge-base/nutrition-databases/`
  - `swasthcart-knowledge-base/ingredient-mappings/`

- **Document Format:**
  - JSON with metadata and chunked content
  - Chunk size: 512 tokens with 50-token overlap
  - Versioning enabled for document updates

**Session State (Amazon DynamoDB)**

- **Table: workflow_sessions**
  - Partition key: session_id (UUID)
  - Sort key: timestamp
  - Attributes: user_id, workflow_state (JSON), ttl
  - GSI: user_id-timestamp-index for user history queries

- **Table: user_profiles**
  - Partition key: user_id
  - Attributes: health_conditions, preferences, family_members, created_at, updated_at

**Cache Layer (Amazon ElastiCache for Redis)**

- **Cache Strategy:**
  - Product risk scores: TTL 24 hours
  - RAG retrieval results: TTL 12 hours
  - User profiles: TTL 1 hour
  - Ingredient normalizations: TTL 7 days

- **Cache Keys:**
  - `product:{product_id}:{user_id}:risk_score`
  - `rag:{query_hash}:documents`
  - `user:{user_id}:profile`
  - `ingredient:{ingredient_text}:normalized`

- **Eviction Policy:** LRU (Least Recently Used)


#### 2.2.7 Tool Invocation Layer

The Tool Invocation Layer implements deterministic, rule-based functions that agents invoke for specific computational tasks. Tools are integrated via LangChain's tool framework and exposed through the Model Context Protocol (MCP).

**Tool Catalog:**

1. **Ingredient Normalizer**
   - Input: Raw ingredient text
   - Output: Normalized ingredient name, category, aliases
   - Implementation: Fuzzy matching against ingredient database

2. **Risk Calculator**
   - Input: Ingredient list, user health conditions, portion size
   - Output: Risk score (0-100), risk factors, confidence score
   - Implementation: Rule-based scoring with condition-specific weights

3. **Alternative Ranker**
   - Input: Product risk score, product category, user preferences
   - Output: Ranked list of alternative products with improvement scores
   - Implementation: Multi-criteria ranking (risk reduction, price, availability)

4. **Bias Detector**
   - Input: Generated explanation text
   - Output: Bias flags (fear-mongering, oversimplification, brand bias)
   - Implementation: Pattern matching and sentiment analysis

5. **Confidence Estimator**
   - Input: Risk assessment, retrieved documents, ingredient coverage
   - Output: Confidence score (0-100), uncertainty factors
   - Implementation: Heuristic scoring based on data quality and coverage

**MCP Integration:**
- Tools exposed as MCP servers with JSON-RPC interface
- Tool discovery via MCP protocol
- Automatic schema generation from Pydantic models
- Error handling and retry logic


#### 2.2.8 Observability Layer

**AWS X-Ray (Distributed Tracing)**

- **Trace Structure:**
  - Root segment: API Gateway request
  - Subsegments: Orchestrator, agents, LLM calls, database queries, tool invocations
  - Annotations: user_id, session_id, workflow_type, risk_score
  - Metadata: Input/output payloads, error details

- **Sampling Strategy:**
  - 100% sampling for errors
  - 10% sampling for successful requests
  - 100% sampling for high-risk assessments (score > 70)

**Amazon CloudWatch (Logs & Metrics)**

- **Log Groups:**
  - `/aws/lambda/swasthcart-orchestrator`
  - `/aws/lambda/swasthcart-agents`
  - `/aws/apigateway/swasthcart-api`

- **Log Format:** JSON structured logs with fields:
  - timestamp, level, session_id, user_id, agent_name, message, context

- **Custom Metrics:**
  - `WorkflowExecutionTime` (milliseconds)
  - `AgentInvocationCount` (count)
  - `LLMTokenUsage` (tokens)
  - `CacheHitRate` (percentage)
  - `RiskScoreDistribution` (histogram)
  - `ErrorRate` (percentage)

- **Alarms:**
  - Error rate > 5% for 5 minutes
  - P99 latency > 5 seconds
  - LLM token usage > 1M tokens/hour




## 3. LangGraph Orchestration Flow

### 3.1 Workflow State Machine

LangGraph implements workflows as directed graphs where nodes represent agent executions and edges represent state transitions. The orchestrator maintains a shared state object that flows through the graph.

**State Transition Diagram:**

```
                    ┌─────────────────┐
                    │  START (Entry)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Ingredient    │
                    │    Analysis     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Risk Scoring   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  RAG Retrieval  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Explanation    │
                    │   Synthesis     │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  Risk > 60?     │
                    └────────┬────────┘
                         Yes │    No
                    ┌────────┴────────┐
                    ▼                 ▼
          ┌─────────────────┐  ┌─────────────────┐
          │  Alternative    │  │   Validation    │
          │ Recommendation  │  │  & Guardrails   │
          └────────┬────────┘  └────────┬────────┘
                   │                    │
                   └────────┬───────────┘
                            ▼
                   ┌─────────────────┐
                   │ Audit & Logging │
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │  END (Finish)   │
                   └─────────────────┘
```

### 3.2 Product Analysis Workflow

**Workflow Definition:**

```python
from langgraph.graph import StateGraph, END

def create_product_analysis_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Add agent nodes
    workflow.add_node("ingredient_analysis", ingredient_analysis_node)
    workflow.add_node("risk_scoring", risk_scoring_node)
    workflow.add_node("rag_retrieval", rag_retrieval_node)
    workflow.add_node("explanation_synthesis", explanation_synthesis_node)
    workflow.add_node("alternative_recommendation", alternative_recommendation_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("audit_logging", audit_logging_node)
    
    # Define transitions
    workflow.add_edge("ingredient_analysis", "risk_scoring")
    workflow.add_edge("risk_scoring", "rag_retrieval")
    workflow.add_edge("rag_retrieval", "explanation_synthesis")
    
    # Conditional edge based on risk score
    workflow.add_conditional_edge(
        "explanation_synthesis",
        lambda state: state["risk_assessment"]["overall_score"] > 60,
        {
            True: "alternative_recommendation",
            False: "validation"
        }
    )
    
    workflow.add_edge("alternative_recommendation", "validation")
    workflow.add_edge("validation", "audit_logging")
    workflow.add_edge("audit_logging", END)
    
    # Set entry point
    workflow.set_entry_point("ingredient_analysis")
    
    return workflow.compile()
```

**Execution Flow:**

1. **Ingredient Analysis** (2-3 seconds)
   - Input: Product data (name, ingredients, nutrition facts)
   - Processing: Normalize ingredients, categorize, identify allergens
   - Output: Normalized ingredient list with categories
   - Error handling: Retry with fallback to raw ingredient text

2. **Risk Scoring** (1-2 seconds)
   - Input: Normalized ingredients, user health conditions
   - Processing: Calculate condition-specific risk scores
   - Output: Risk assessment with scores per condition
   - Error handling: Use rule-based scoring if LLM fails

3. **RAG Retrieval** (1-2 seconds)
   - Input: Risk factors, user conditions
   - Processing: Query vector database for relevant health documents
   - Output: Top-10 documents with relevance scores
   - Error handling: Return cached documents or skip if unavailable

4. **Explanation Synthesis** (3-4 seconds)
   - Input: Risk assessment, retrieved documents
   - Processing: Generate human-readable explanation with citations
   - Output: Structured explanation with risk breakdown
   - Error handling: Generate template-based explanation

5. **Alternative Recommendation** (2-3 seconds, conditional)
   - Input: Product category, risk score, user preferences
   - Processing: Search for safer alternatives, rank by improvement
   - Output: Top-5 alternatives with comparison metrics
   - Error handling: Skip if no alternatives found

6. **Validation & Guardrails** (0.5-1 second)
   - Input: Complete workflow output
   - Processing: Check for harmful content, bias, accuracy
   - Output: Validated output or error flags
   - Error handling: Block output if validation fails

7. **Audit & Logging** (0.5 second)
   - Input: Complete workflow state
   - Processing: Log execution trace, user interaction
   - Output: Audit record
   - Error handling: Best-effort logging, do not block workflow

**Total Execution Time:** 10-16 seconds (target: < 15 seconds)


### 3.3 Cart Analysis Workflow

**Workflow Definition:**

```python
def create_cart_analysis_workflow():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("cart_preprocessing", cart_preprocessing_node)
    workflow.add_node("parallel_product_analysis", parallel_product_analysis_node)
    workflow.add_node("cart_aggregation", cart_aggregation_node)
    workflow.add_node("trend_analysis", trend_analysis_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("audit_logging", audit_logging_node)
    
    workflow.add_edge("cart_preprocessing", "parallel_product_analysis")
    workflow.add_edge("parallel_product_analysis", "cart_aggregation")
    workflow.add_edge("cart_aggregation", "trend_analysis")
    workflow.add_edge("trend_analysis", "validation")
    workflow.add_edge("validation", "audit_logging")
    workflow.add_edge("audit_logging", END)
    
    workflow.set_entry_point("cart_preprocessing")
    
    return workflow.compile()
```

**Execution Flow:**

1. **Cart Preprocessing** (0.5 second)
   - Extract product list from cart data
   - Deduplicate products
   - Check cache for previously analyzed products

2. **Parallel Product Analysis** (10-15 seconds)
   - Execute product analysis workflow for each product in parallel
   - Concurrency limit: 5 products at a time
   - Aggregate results as they complete

3. **Cart Aggregation** (2-3 seconds)
   - Calculate cart-level health score
   - Identify top risk contributors
   - Generate cart health summary

4. **Trend Analysis** (1-2 seconds)
   - Compare with user's historical cart data
   - Identify improving or worsening trends
   - Generate trend insights

5. **Validation & Audit** (1 second)
   - Validate aggregated results
   - Log cart analysis event

**Total Execution Time:** 15-22 seconds for 5-10 products


### 3.4 Error Handling and Retry Logic

**Retry Strategy:**

```python
class RetryConfig:
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    backoff_multiplier: float = 2.0
    max_delay: float = 8.0
    jitter: float = 0.2  # ±20%
    
    retryable_errors = [
        "LLMTimeoutError",
        "VectorDBConnectionError",
        "RateLimitError",
        "TransientNetworkError"
    ]
    
    non_retryable_errors = [
        "InvalidInputError",
        "AuthenticationError",
        "ValidationError"
    ]
```

**Fallback Strategies:**

| Component | Primary | Fallback 1 | Fallback 2 |
|-----------|---------|------------|------------|
| LLM | Claude 3 Sonnet | Claude 3 Haiku | Rule-based engine |
| Vector DB | OpenSearch | Cached results | Generic guidance |
| Embeddings | Titan Embeddings | Cached embeddings | Skip RAG |
| Cache | ElastiCache | Direct DB query | Recompute |

**Circuit Breaker Pattern:**

```python
class CircuitBreaker:
    failure_threshold: int = 5  # failures before opening
    timeout: float = 60.0  # seconds before half-open
    success_threshold: int = 2  # successes before closing
    
    states = ["CLOSED", "OPEN", "HALF_OPEN"]
```

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Failures exceeded threshold, requests fail fast
- **HALF_OPEN**: Testing recovery, limited requests allowed


### 3.5 State Persistence and Recovery

**State Snapshot Strategy:**

```python
def save_state_snapshot(state: WorkflowState):
    """Save workflow state after each agent execution"""
    snapshot = {
        "session_id": state["session_id"],
        "workflow_type": state["workflow_type"],
        "current_step": state["current_step"],
        "state_data": state,
        "timestamp": datetime.utcnow().isoformat(),
        "ttl": int(time.time()) + 86400  # 24 hours
    }
    
    dynamodb.put_item(
        TableName="workflow_sessions",
        Item=snapshot
    )
```

**Recovery Mechanism:**

```python
def recover_workflow(session_id: str) -> Optional[WorkflowState]:
    """Recover workflow from last successful state"""
    response = dynamodb.get_item(
        TableName="workflow_sessions",
        Key={"session_id": session_id}
    )
    
    if response.get("Item"):
        state = response["Item"]["state_data"]
        # Resume from current_step
        return state
    
    return None
```

**Idempotency:**
- All agent executions are idempotent
- Duplicate requests with same session_id return cached results
- State updates use conditional writes to prevent race conditions




## 4. Agent Definitions

### 4.1 Ingredient Analysis Agent

**Responsibility:** Normalize raw ingredient text into structured, categorized ingredient objects with allergen identification and nutritional classification.

**Input Schema:**

```python
class IngredientAnalysisInput(BaseModel):
    product_id: str
    product_name: str
    raw_ingredients: str  # Comma-separated ingredient list
    nutrition_facts: Optional[NutritionFacts]
    product_category: str
```

**Output Schema:**

```python
class NormalizedIngredient(BaseModel):
    original_text: str
    normalized_name: str
    category: IngredientCategory  # PRESERVATIVE, SWEETENER, FAT, PROTEIN, etc.
    aliases: List[str]
    allergen_flags: List[AllergenType]  # GLUTEN, DAIRY, SOY, NUTS, etc.
    processing_level: ProcessingLevel  # MINIMAL, MODERATE, ULTRA_PROCESSED
    confidence: float  # 0.0-1.0

class IngredientAnalysisOutput(BaseModel):
    product_id: str
    normalized_ingredients: List[NormalizedIngredient]
    total_ingredient_count: int
    ultra_processed_count: int
    allergen_summary: Dict[AllergenType, int]
    processing_timestamp: str
```

**Tool Invocations:**

1. **Ingredient Normalizer Tool**
   - Fuzzy match against ingredient database (50,000+ entries)
   - Handle common misspellings and variations
   - Map to standardized ingredient names

2. **Allergen Detector Tool**
   - Pattern matching for allergen keywords
   - Cross-reference with allergen database
   - Flag hidden allergens (e.g., casein in "natural flavors")

**Implementation Logic:**

```python
async def ingredient_analysis_agent(state: WorkflowState) -> WorkflowState:
    """
    Normalize and categorize product ingredients
    """
    product_data = state["product_data"]
    
    # Step 1: Parse raw ingredient text
    raw_ingredients = product_data["raw_ingredients"].split(",")
    
    # Step 2: Normalize each ingredient
    normalized_ingredients = []
    for raw_ingredient in raw_ingredients:
        # Invoke Ingredient Normalizer Tool
        normalized = await ingredient_normalizer_tool.invoke({
            "raw_text": raw_ingredient.strip()
        })
        
        # Invoke Allergen Detector Tool
        allergens = await allergen_detector_tool.invoke({
            "ingredient_name": normalized["normalized_name"]
        })
        
        # Classify processing level
        processing_level = classify_processing_level(normalized)
        
        normalized_ingredients.append(NormalizedIngredient(
            original_text=raw_ingredient,
            normalized_name=normalized["normalized_name"],
            category=normalized["category"],
            aliases=normalized["aliases"],
            allergen_flags=allergens,
            processing_level=processing_level,
            confidence=normalized["confidence"]
        ))
    
    # Step 3: Generate summary statistics
    allergen_summary = defaultdict(int)
    ultra_processed_count = 0
    
    for ingredient in normalized_ingredients:
        for allergen in ingredient.allergen_flags:
            allergen_summary[allergen] += 1
        if ingredient.processing_level == ProcessingLevel.ULTRA_PROCESSED:
            ultra_processed_count += 1
    
    # Update state
    state["normalized_ingredients"] = normalized_ingredients
    state["execution_metadata"]["ingredient_analysis_duration"] = time.time() - start_time
    
    return state
```

**LLM Prompt (for ambiguous cases):**

```
You are an expert food scientist specializing in ingredient analysis.

Task: Normalize the following ingredient text and classify it.

Ingredient: "{raw_ingredient}"
Product Category: "{product_category}"

Provide:
1. Normalized ingredient name (standardized terminology)
2. Ingredient category (PRESERVATIVE, SWEETENER, FAT, PROTEIN, CARBOHYDRATE, ADDITIVE, NATURAL, OTHER)
3. Processing level (MINIMAL, MODERATE, ULTRA_PROCESSED)
4. Confidence score (0.0-1.0)

Output as JSON:
{
  "normalized_name": "...",
  "category": "...",
  "processing_level": "...",
  "confidence": 0.0
}

Rules:
- Use scientific names when available
- Flag E-numbers and INS codes as additives
- Consider product category context
- Be conservative with confidence scores
```

**Error Handling:**
- If normalization fails, use raw ingredient text with low confidence
- If allergen detection fails, flag for manual review
- Log all low-confidence normalizations (< 0.7) for human review


### 4.2 Risk Scoring Agent

**Responsibility:** Calculate condition-specific risk scores based on normalized ingredients and user health profile.

**Input Schema:**

```python
class RiskScoringInput(BaseModel):
    product_id: str
    normalized_ingredients: List[NormalizedIngredient]
    nutrition_facts: NutritionFacts
    user_profile: UserProfile
```

**Output Schema:**

```python
class ConditionRiskScore(BaseModel):
    condition: HealthCondition
    score: int  # 0-100
    risk_level: RiskLevel  # LOW, MODERATE, HIGH, CRITICAL
    contributing_factors: List[RiskFactor]
    confidence: float

class RiskFactor(BaseModel):
    factor_name: str
    ingredient_or_nutrient: str
    impact_score: int  # 0-100
    explanation: str

class RiskScoringOutput(BaseModel):
    product_id: str
    overall_score: int  # 0-100
    overall_risk_level: RiskLevel
    condition_scores: List[ConditionRiskScore]
    top_risk_factors: List[RiskFactor]
    confidence: float
```

**Tool Invocations:**

1. **Risk Calculator Tool**
   - Rule-based scoring engine
   - Condition-specific weight matrices
   - Nutrient threshold checks

2. **Confidence Estimator Tool**
   - Assess data quality and coverage
   - Calculate uncertainty based on missing data

**Implementation Logic:**

```python
async def risk_scoring_agent(state: WorkflowState) -> WorkflowState:
    """
    Calculate condition-specific risk scores
    """
    normalized_ingredients = state["normalized_ingredients"]
    nutrition_facts = state["product_data"]["nutrition_facts"]
    user_profile = state["user_profile"]
    
    condition_scores = []
    
    # Calculate risk for each user health condition
    for condition in user_profile["health_conditions"]:
        # Invoke Risk Calculator Tool
        risk_result = await risk_calculator_tool.invoke({
            "condition": condition,
            "ingredients": normalized_ingredients,
            "nutrition_facts": nutrition_facts
        })
        
        condition_scores.append(ConditionRiskScore(
            condition=condition,
            score=risk_result["score"],
            risk_level=classify_risk_level(risk_result["score"]),
            contributing_factors=risk_result["factors"],
            confidence=risk_result["confidence"]
        ))
    
    # Calculate overall score (weighted average)
    overall_score = calculate_overall_score(condition_scores)
    
    # Identify top risk factors across all conditions
    all_factors = [f for cs in condition_scores for f in cs.contributing_factors]
    top_risk_factors = sorted(all_factors, key=lambda x: x.impact_score, reverse=True)[:5]
    
    # Estimate confidence
    confidence = await confidence_estimator_tool.invoke({
        "ingredient_coverage": len(normalized_ingredients),
        "nutrition_data_completeness": nutrition_facts.completeness_score,
        "condition_scores": condition_scores
    })
    
    # Update state
    state["risk_assessment"] = RiskScoringOutput(
        product_id=state["product_data"]["product_id"],
        overall_score=overall_score,
        overall_risk_level=classify_risk_level(overall_score),
        condition_scores=condition_scores,
        top_risk_factors=top_risk_factors,
        confidence=confidence
    )
    
    return state
```

**Risk Calculation Formula:**

```python
def calculate_condition_risk(condition: HealthCondition, 
                            ingredients: List[NormalizedIngredient],
                            nutrition: NutritionFacts) -> int:
    """
    Condition-specific risk scoring
    """
    risk_score = 0
    
    # Ingredient-based risk
    for ingredient in ingredients:
        if ingredient.category in CONDITION_RISK_MAP[condition]:
            weight = CONDITION_RISK_MAP[condition][ingredient.category]
            risk_score += weight * ingredient.confidence
    
    # Nutrient-based risk
    for nutrient, threshold in CONDITION_NUTRIENT_THRESHOLDS[condition].items():
        if nutrition[nutrient] > threshold:
            excess_ratio = nutrition[nutrient] / threshold
            risk_score += NUTRIENT_RISK_WEIGHTS[condition][nutrient] * excess_ratio
    
    # Processing level penalty
    ultra_processed_count = sum(1 for i in ingredients 
                                if i.processing_level == ProcessingLevel.ULTRA_PROCESSED)
    risk_score += ultra_processed_count * ULTRA_PROCESSED_PENALTY
    
    # Normalize to 0-100
    return min(int(risk_score), 100)
```

**Condition Risk Maps (Examples):**

```python
CONDITION_RISK_MAP = {
    HealthCondition.DIABETES: {
        IngredientCategory.SWEETENER: 30,
        IngredientCategory.REFINED_CARB: 25,
        IngredientCategory.TRANS_FAT: 20
    },
    HealthCondition.HYPERTENSION: {
        IngredientCategory.SODIUM: 35,
        IngredientCategory.PRESERVATIVE: 20,
        IngredientCategory.SATURATED_FAT: 15
    },
    HealthCondition.PCOS: {
        IngredientCategory.SWEETENER: 25,
        IngredientCategory.REFINED_CARB: 20,
        IngredientCategory.TRANS_FAT: 20,
        IngredientCategory.DAIRY: 15
    }
}
```


### 4.3 RAG Retrieval Agent

**Responsibility:** Retrieve relevant health knowledge documents from vector database to ground risk explanations in authoritative sources.

**Input Schema:**

```python
class RAGRetrievalInput(BaseModel):
    risk_assessment: RiskScoringOutput
    user_profile: UserProfile
    query_context: str  # Generated query for retrieval
```

**Output Schema:**

```python
class RetrievedDocument(BaseModel):
    document_id: str
    title: str
    content_chunk: str
    source: str  # Journal name, organization, database
    publication_date: str
    authority_score: float  # 0.0-1.0
    relevance_score: float  # 0.0-1.0
    citation: str  # Formatted citation

class RAGRetrievalOutput(BaseModel):
    query: str
    retrieved_documents: List[RetrievedDocument]
    retrieval_metadata: RetrievalMetadata
```

**Tool Invocations:**

1. **Query Generator Tool**
   - Generate optimal search query from risk factors
   - Expand query with synonyms and related terms

2. **Vector Search Tool**
   - Query OpenSearch with embedding
   - Apply filters and re-ranking

**Implementation Logic:**

```python
async def rag_retrieval_agent(state: WorkflowState) -> WorkflowState:
    """
    Retrieve relevant health knowledge documents
    """
    risk_assessment = state["risk_assessment"]
    user_profile = state["user_profile"]
    
    # Step 1: Generate retrieval query
    query = generate_retrieval_query(risk_assessment, user_profile)
    
    # Step 2: Generate query embedding
    query_embedding = await titan_embeddings.embed_query(query)
    
    # Step 3: Vector search with filters
    search_results = await opensearch_client.search(
        index="health-knowledge",
        body={
            "size": 10,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": 20
                                }
                            }
                        }
                    ],
                    "filter": [
                        {
                            "terms": {
                                "condition_tags": [c.value for c in user_profile.health_conditions]
                            }
                        }
                    ]
                }
            }
        }
    )
    
    # Step 4: Re-rank by authority and recency
    documents = []
    for hit in search_results["hits"]["hits"]:
        doc = hit["_source"]
        relevance_score = hit["_score"]
        
        # Re-ranking formula
        final_score = (
            0.6 * relevance_score +
            0.3 * doc["authority_score"] +
            0.1 * recency_score(doc["publication_date"])
        )
        
        documents.append(RetrievedDocument(
            document_id=doc["document_id"],
            title=doc["title"],
            content_chunk=doc["content"],
            source=doc["source"],
            publication_date=doc["publication_date"],
            authority_score=doc["authority_score"],
            relevance_score=final_score,
            citation=format_citation(doc)
        ))
    
    # Sort by final score
    documents.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Update state
    state["retrieved_documents"] = documents[:10]
    
    return state
```

**Query Generation Strategy:**

```python
def generate_retrieval_query(risk_assessment: RiskScoringOutput, 
                            user_profile: UserProfile) -> str:
    """
    Generate optimal retrieval query from risk factors
    """
    # Extract top risk factors
    top_factors = risk_assessment.top_risk_factors[:3]
    
    # Extract conditions
    conditions = [c.value for c in user_profile.health_conditions]
    
    # Build query
    query_parts = []
    
    for factor in top_factors:
        query_parts.append(f"{factor.ingredient_or_nutrient} health effects")
    
    for condition in conditions:
        query_parts.append(f"{condition} dietary guidelines")
    
    return " ".join(query_parts)
```




### 4.4 Explanation Synthesis Agent

**Responsibility:** Generate human-readable, explainable risk analysis with authoritative source citations and transparent methodology.

**Input Schema:**

```python
class ExplanationSynthesisInput(BaseModel):
    risk_assessment: RiskScoringOutput
    retrieved_documents: List[RetrievedDocument]
    user_profile: UserProfile
```

**Output Schema:**

```python
class RiskExplanation(BaseModel):
    summary: str  # 2-3 sentence overview
    detailed_breakdown: List[ConditionExplanation]
    key_concerns: List[str]  # Bullet points
    positive_aspects: List[str]  # Balanced view
    citations: List[Citation]
    confidence_statement: str
    methodology_note: str

class ConditionExplanation(BaseModel):
    condition: HealthCondition
    explanation: str
    supporting_evidence: List[str]  # Citations
    risk_level: RiskLevel

class Citation(BaseModel):
    citation_id: str
    formatted_citation: str
    url: Optional[str]
```

**Tool Invocations:**

1. **Bias Detector Tool**
   - Scan generated text for fear-mongering language
   - Detect oversimplification or exaggeration
   - Flag brand bias or promotional content

**Implementation Logic:**

```python
async def explanation_synthesis_agent(state: WorkflowState) -> WorkflowState:
    """
    Generate explainable risk analysis with citations
    """
    risk_assessment = state["risk_assessment"]
    retrieved_documents = state["retrieved_documents"]
    user_profile = state["user_profile"]
    
    # Step 1: Prepare context for LLM
    context = prepare_explanation_context(
        risk_assessment, 
        retrieved_documents, 
        user_profile
    )
    
    # Step 2: Generate explanation using LLM
    llm_response = await bedrock_client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body={
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": 0.3,
            "system": EXPLANATION_SYNTHESIS_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": EXPLANATION_SYNTHESIS_USER_PROMPT.format(**context)
                }
            ]
        }
    )
    
    explanation_data = json.loads(llm_response["content"][0]["text"])
    
    # Step 3: Validate and check for bias
    bias_check = await bias_detector_tool.invoke({
        "text": explanation_data["summary"] + " " + " ".join(explanation_data["key_concerns"])
    })
    
    if bias_check["has_bias"]:
        # Regenerate with bias mitigation prompt
        explanation_data = await regenerate_with_bias_mitigation(context, bias_check)
    
    # Step 4: Add citations
    citations = format_citations(retrieved_documents)
    
    # Step 5: Add confidence statement
    confidence_statement = generate_confidence_statement(
        risk_assessment.confidence,
        len(retrieved_documents)
    )
    
    # Step 6: Add methodology note
    methodology_note = (
        "Risk scores are calculated based on ingredient analysis, nutritional content, "
        "and condition-specific dietary guidelines. Scores range from 0 (lowest risk) to "
        "100 (highest risk). This analysis is for informational purposes only and does not "
        "constitute medical advice."
    )
    
    # Update state
    state["explanation"] = RiskExplanation(
        summary=explanation_data["summary"],
        detailed_breakdown=explanation_data["detailed_breakdown"],
        key_concerns=explanation_data["key_concerns"],
        positive_aspects=explanation_data["positive_aspects"],
        citations=citations,
        confidence_statement=confidence_statement,
        methodology_note=methodology_note
    )
    
    return state
```

**LLM System Prompt:**

```
You are a health communication specialist creating transparent, balanced product risk explanations.

Your role:
- Synthesize risk assessment data into clear, actionable explanations
- Ground all claims in provided scientific evidence
- Maintain a balanced, non-alarmist tone
- Use plain language accessible to non-experts
- Cite sources for all health claims
- Acknowledge uncertainty when data is limited

Constraints:
- Never provide medical advice or diagnoses
- Never recommend specific brands or products
- Never use fear-mongering language
- Never oversimplify complex health relationships
- Always present both concerns and positive aspects
- Always include confidence qualifiers

Output format: JSON with fields: summary, detailed_breakdown, key_concerns, positive_aspects
```

**LLM User Prompt Template:**

```
Generate a risk explanation for the following product analysis:

Product: {product_name}
Overall Risk Score: {overall_score}/100
Risk Level: {risk_level}

User Health Conditions: {conditions}

Risk Factors:
{risk_factors}

Supporting Evidence:
{retrieved_documents}

Provide:
1. Summary (2-3 sentences, balanced tone)
2. Detailed breakdown per condition
3. Key concerns (3-5 bullet points)
4. Positive aspects (2-3 bullet points, if any)

Use citation markers [1], [2], etc. to reference evidence.
Maintain objectivity and avoid alarmist language.
```

**Bias Detection Patterns:**

```python
BIAS_PATTERNS = {
    "fear_mongering": [
        r"dangerous",
        r"toxic",
        r"deadly",
        r"never consume",
        r"avoid at all costs"
    ],
    "oversimplification": [
        r"always causes",
        r"guaranteed to",
        r"will definitely",
        r"100% safe",
        r"completely harmless"
    ],
    "brand_bias": [
        r"better than \w+",
        r"worse than \w+",
        r"switch to \w+",
        r"buy \w+ instead"
    ]
}
```


### 4.5 Cart Aggregation Agent

**Responsibility:** Perform cart-level health assessment by aggregating individual product risk scores and identifying patterns.

**Input Schema:**

```python
class CartAggregationInput(BaseModel):
    cart_id: str
    product_assessments: List[RiskScoringOutput]
    user_profile: UserProfile
```

**Output Schema:**

```python
class CartHealthScore(BaseModel):
    cart_id: str
    overall_health_score: int  # 0-100 (inverted risk)
    total_products: int
    high_risk_products: int
    moderate_risk_products: int
    low_risk_products: int
    top_concerns: List[CartConcern]
    category_breakdown: Dict[str, CategoryScore]
    trend_analysis: Optional[TrendAnalysis]

class CartConcern(BaseModel):
    concern_type: str  # "High sodium across multiple products"
    affected_products: List[str]
    aggregate_impact: int
    recommendation: str

class CategoryScore(BaseModel):
    category: str
    average_score: int
    product_count: int
```

**Implementation Logic:**

```python
async def cart_aggregation_agent(state: WorkflowState) -> WorkflowState:
    """
    Aggregate product-level assessments into cart-level insights
    """
    product_assessments = state["product_assessments"]
    user_profile = state["user_profile"]
    
    # Step 1: Calculate overall cart health score
    total_risk = sum(p.overall_score for p in product_assessments)
    avg_risk = total_risk / len(product_assessments)
    overall_health_score = 100 - avg_risk  # Invert to health score
    
    # Step 2: Categorize products by risk level
    high_risk = [p for p in product_assessments if p.overall_risk_level == RiskLevel.HIGH]
    moderate_risk = [p for p in product_assessments if p.overall_risk_level == RiskLevel.MODERATE]
    low_risk = [p for p in product_assessments if p.overall_risk_level == RiskLevel.LOW]
    
    # Step 3: Identify cross-product concerns
    top_concerns = identify_cart_concerns(product_assessments)
    
    # Step 4: Category breakdown
    category_breakdown = calculate_category_scores(product_assessments)
    
    # Step 5: Trend analysis (if historical data available)
    trend_analysis = None
    if user_profile.get("historical_carts"):
        trend_analysis = analyze_cart_trends(
            current_cart=product_assessments,
            historical_carts=user_profile["historical_carts"]
        )
    
    # Update state
    state["cart_health_score"] = CartHealthScore(
        cart_id=state["cart_data"]["cart_id"],
        overall_health_score=int(overall_health_score),
        total_products=len(product_assessments),
        high_risk_products=len(high_risk),
        moderate_risk_products=len(moderate_risk),
        low_risk_products=len(low_risk),
        top_concerns=top_concerns,
        category_breakdown=category_breakdown,
        trend_analysis=trend_analysis
    )
    
    return state
```

**Concern Identification Logic:**

```python
def identify_cart_concerns(assessments: List[RiskScoringOutput]) -> List[CartConcern]:
    """
    Identify patterns across multiple products
    """
    concerns = []
    
    # Aggregate risk factors across all products
    factor_aggregation = defaultdict(lambda: {"products": [], "total_impact": 0})
    
    for assessment in assessments:
        for factor in assessment.top_risk_factors:
            key = factor.ingredient_or_nutrient
            factor_aggregation[key]["products"].append(assessment.product_id)
            factor_aggregation[key]["total_impact"] += factor.impact_score
    
    # Identify concerns affecting multiple products
    for factor, data in factor_aggregation.items():
        if len(data["products"]) >= 3:  # Threshold: 3+ products
            concerns.append(CartConcern(
                concern_type=f"High {factor} across multiple products",
                affected_products=data["products"],
                aggregate_impact=data["total_impact"],
                recommendation=generate_concern_recommendation(factor)
            ))
    
    # Sort by aggregate impact
    concerns.sort(key=lambda x: x.aggregate_impact, reverse=True)
    
    return concerns[:5]  # Top 5 concerns
```


### 4.6 Alternative Recommendation Agent

**Responsibility:** Identify and rank safer product alternatives with quantified health improvements.

**Input Schema:**

```python
class AlternativeRecommendationInput(BaseModel):
    product_id: str
    product_category: str
    risk_assessment: RiskScoringOutput
    user_profile: UserProfile
    user_preferences: UserPreferences  # Price range, brands, dietary restrictions
```

**Output Schema:**

```python
class Alternative(BaseModel):
    product_id: str
    product_name: str
    brand: str
    risk_score: int
    risk_improvement: int  # Percentage improvement
    price: float
    price_difference: float  # Percentage difference
    availability: str  # "In stock", "Limited", "Out of stock"
    match_score: float  # 0.0-1.0, how well it matches original product
    key_improvements: List[str]
    trade_offs: List[str]

class AlternativeRecommendationOutput(BaseModel):
    original_product_id: str
    alternatives: List[Alternative]
    recommendation_rationale: str
```

**Tool Invocations:**

1. **Alternative Ranker Tool**
   - Multi-criteria ranking algorithm
   - Balances health improvement, price, availability, match quality

**Implementation Logic:**

```python
async def alternative_recommendation_agent(state: WorkflowState) -> WorkflowState:
    """
    Recommend safer product alternatives
    """
    risk_assessment = state["risk_assessment"]
    product_data = state["product_data"]
    user_profile = state["user_profile"]
    
    # Step 1: Search for alternatives in same category
    candidate_products = await search_alternative_products(
        category=product_data["category"],
        exclude_product_id=product_data["product_id"]
    )
    
    # Step 2: Analyze each candidate (cached if available)
    candidate_assessments = []
    for candidate in candidate_products:
        # Check cache first
        cached_assessment = await get_cached_assessment(candidate["product_id"], user_profile["user_id"])
        
        if cached_assessment:
            candidate_assessments.append(cached_assessment)
        else:
            # Run product analysis workflow
            assessment = await analyze_product(candidate, user_profile)
            candidate_assessments.append(assessment)
    
    # Step 3: Filter candidates with lower risk
    better_alternatives = [
        a for a in candidate_assessments 
        if a.overall_score < risk_assessment.overall_score
    ]
    
    # Step 4: Rank alternatives
    ranked_alternatives = await alternative_ranker_tool.invoke({
        "original_risk_score": risk_assessment.overall_score,
        "candidates": better_alternatives,
        "user_preferences": user_profile["preferences"]
    })
    
    # Step 5: Format alternatives
    alternatives = []
    for alt in ranked_alternatives[:5]:  # Top 5
        risk_improvement = calculate_improvement_percentage(
            risk_assessment.overall_score,
            alt["risk_score"]
        )
        
        alternatives.append(Alternative(
            product_id=alt["product_id"],
            product_name=alt["product_name"],
            brand=alt["brand"],
            risk_score=alt["risk_score"],
            risk_improvement=risk_improvement,
            price=alt["price"],
            price_difference=calculate_price_difference(product_data["price"], alt["price"]),
            availability=alt["availability"],
            match_score=alt["match_score"],
            key_improvements=identify_key_improvements(risk_assessment, alt),
            trade_offs=identify_trade_offs(product_data, alt)
        ))
    
    # Update state
    state["alternatives"] = AlternativeRecommendationOutput(
        original_product_id=product_data["product_id"],
        alternatives=alternatives,
        recommendation_rationale=generate_recommendation_rationale(alternatives)
    )
    
    return state
```

**Ranking Algorithm:**

```python
def rank_alternatives(original_score: int,
                     candidates: List[Dict],
                     preferences: UserPreferences) -> List[Dict]:
    """
    Multi-criteria ranking with user preference weighting
    """
    scored_candidates = []
    
    for candidate in candidates:
        # Health improvement score (0-100)
        health_score = (original_score - candidate["risk_score"]) / original_score * 100
        
        # Price score (0-100, lower price difference is better)
        price_diff = abs(candidate["price"] - preferences["target_price"]) / preferences["target_price"]
        price_score = max(0, 100 - price_diff * 100)
        
        # Availability score
        availability_score = {
            "In stock": 100,
            "Limited": 50,
            "Out of stock": 0
        }[candidate["availability"]]
        
        # Match score (how similar to original product)
        match_score = candidate["match_score"] * 100
        
        # Weighted final score
        final_score = (
            preferences["health_weight"] * health_score +
            preferences["price_weight"] * price_score +
            preferences["availability_weight"] * availability_score +
            preferences["match_weight"] * match_score
        )
        
        candidate["final_score"] = final_score
        scored_candidates.append(candidate)
    
    # Sort by final score
    scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    
    return scored_candidates
```




### 4.7 Validation & Guardrail Agent

**Responsibility:** Enforce safety checks, quality validation, and guardrails to prevent harmful or inaccurate outputs.

**Input Schema:**

```python
class ValidationInput(BaseModel):
    workflow_output: Dict  # Complete workflow result
    workflow_type: str
    user_profile: UserProfile
```

**Output Schema:**

```python
class ValidationResult(BaseModel):
    is_valid: bool
    validation_checks: List[ValidationCheck]
    blocked_content: List[str]
    warnings: List[str]
    sanitized_output: Optional[Dict]

class ValidationCheck(BaseModel):
    check_name: str
    passed: bool
    severity: Severity  # INFO, WARNING, ERROR, CRITICAL
    message: str
```

**Validation Checks:**

1. **Content Safety Check**
   - No medical diagnoses or treatment recommendations
   - No fear-mongering or alarmist language
   - No brand endorsements or promotional content

2. **Accuracy Check**
   - Risk scores within valid range (0-100)
   - All citations reference valid documents
   - Confidence scores align with data quality

3. **Completeness Check**
   - All required fields present
   - No null values in critical fields
   - Minimum explanation length met

4. **Bias Check**
   - No discriminatory language
   - Balanced presentation of risks and benefits
   - No cultural or dietary bias

5. **Privacy Check**
   - No PII in output
   - User health conditions not exposed in logs
   - Anonymized identifiers only

**Implementation Logic:**

```python
async def validation_guardrail_agent(state: WorkflowState) -> WorkflowState:
    """
    Validate workflow output and enforce guardrails
    """
    workflow_output = prepare_workflow_output(state)
    
    validation_checks = []
    blocked_content = []
    warnings = []
    
    # Check 1: Content Safety
    safety_check = validate_content_safety(workflow_output)
    validation_checks.append(safety_check)
    if not safety_check.passed:
        blocked_content.extend(safety_check.blocked_items)
    
    # Check 2: Accuracy
    accuracy_check = validate_accuracy(workflow_output)
    validation_checks.append(accuracy_check)
    
    # Check 3: Completeness
    completeness_check = validate_completeness(workflow_output)
    validation_checks.append(completeness_check)
    
    # Check 4: Bias
    bias_check = await bias_detector_tool.invoke({
        "text": extract_text_content(workflow_output)
    })
    validation_checks.append(bias_check)
    if bias_check.has_bias:
        warnings.append(f"Potential bias detected: {bias_check.bias_type}")
    
    # Check 5: Privacy
    privacy_check = validate_privacy(workflow_output)
    validation_checks.append(privacy_check)
    
    # Determine overall validity
    critical_failures = [c for c in validation_checks 
                        if not c.passed and c.severity == Severity.CRITICAL]
    is_valid = len(critical_failures) == 0
    
    # Sanitize output if needed
    sanitized_output = workflow_output
    if blocked_content:
        sanitized_output = sanitize_output(workflow_output, blocked_content)
    
    # Update state
    state["validation_result"] = ValidationResult(
        is_valid=is_valid,
        validation_checks=validation_checks,
        blocked_content=blocked_content,
        warnings=warnings,
        sanitized_output=sanitized_output if is_valid else None
    )
    
    return state
```

**Content Safety Patterns:**

```python
PROHIBITED_PATTERNS = {
    "medical_advice": [
        r"you should take",
        r"consult.*doctor",
        r"diagnose",
        r"treatment for",
        r"cure",
        r"prescribe"
    ],
    "fear_mongering": [
        r"will kill you",
        r"extremely dangerous",
        r"toxic poison",
        r"never eat",
        r"deadly"
    ],
    "brand_endorsement": [
        r"buy \w+ brand",
        r"\w+ is the best",
        r"sponsored by",
        r"recommended by \w+ company"
    ]
}

def validate_content_safety(output: Dict) -> ValidationCheck:
    """
    Check for prohibited content patterns
    """
    text_content = extract_text_content(output)
    violations = []
    
    for category, patterns in PROHIBITED_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                violations.append(f"{category}: {pattern}")
    
    return ValidationCheck(
        check_name="content_safety",
        passed=len(violations) == 0,
        severity=Severity.CRITICAL if violations else Severity.INFO,
        message=f"Found {len(violations)} safety violations" if violations else "Passed"
    )
```

**Guardrail Enforcement:**

```python
GUARDRAILS = {
    "max_risk_score": 100,
    "min_risk_score": 0,
    "max_explanation_length": 2000,  # characters
    "min_explanation_length": 100,
    "max_alternatives": 10,
    "min_confidence": 0.0,
    "max_confidence": 1.0,
    "required_fields": [
        "overall_score",
        "risk_level",
        "explanation",
        "confidence"
    ]
}
```


### 4.8 Audit & Logging Agent

**Responsibility:** Record comprehensive execution traces, user interactions, and audit trails for compliance and debugging.

**Input Schema:**

```python
class AuditLoggingInput(BaseModel):
    workflow_state: WorkflowState
    validation_result: ValidationResult
```

**Output Schema:**

```python
class AuditRecord(BaseModel):
    audit_id: str
    timestamp: str
    user_id: str
    session_id: str
    workflow_type: str
    
    # Input data (anonymized)
    input_summary: Dict
    
    # Execution metadata
    execution_duration: float
    agent_invocations: List[AgentInvocation]
    llm_calls: List[LLMCall]
    tool_invocations: List[ToolInvocation]
    
    # Output data
    output_summary: Dict
    validation_status: str
    
    # Observability
    trace_id: str
    error_count: int
    warning_count: int
```

**Implementation Logic:**

```python
async def audit_logging_agent(state: WorkflowState) -> WorkflowState:
    """
    Create comprehensive audit trail
    """
    # Step 1: Prepare audit record
    audit_record = AuditRecord(
        audit_id=generate_uuid(),
        timestamp=datetime.utcnow().isoformat(),
        user_id=anonymize_user_id(state["user_id"]),
        session_id=state["session_id"],
        workflow_type=state["workflow_type"],
        input_summary=create_input_summary(state),
        execution_duration=calculate_execution_duration(state),
        agent_invocations=extract_agent_invocations(state),
        llm_calls=extract_llm_calls(state),
        tool_invocations=extract_tool_invocations(state),
        output_summary=create_output_summary(state),
        validation_status=state["validation_result"]["is_valid"],
        trace_id=state["execution_metadata"]["trace_id"],
        error_count=len(state["errors"]),
        warning_count=len(state["validation_result"]["warnings"])
    )
    
    # Step 2: Write to audit log (S3)
    await write_audit_log(audit_record)
    
    # Step 3: Write to CloudWatch Logs
    logger.info(
        "Workflow completed",
        extra={
            "session_id": state["session_id"],
            "workflow_type": state["workflow_type"],
            "duration": audit_record.execution_duration,
            "validation_status": audit_record.validation_status
        }
    )
    
    # Step 4: Emit CloudWatch Metrics
    cloudwatch.put_metric_data(
        Namespace="SwasthCartAI",
        MetricData=[
            {
                "MetricName": "WorkflowExecutionTime",
                "Value": audit_record.execution_duration,
                "Unit": "Milliseconds",
                "Dimensions": [
                    {"Name": "WorkflowType", "Value": state["workflow_type"]}
                ]
            },
            {
                "MetricName": "LLMTokenUsage",
                "Value": sum(call.token_count for call in audit_record.llm_calls),
                "Unit": "Count"
            }
        ]
    )
    
    # Step 5: Update user interaction history
    await update_user_history(
        user_id=state["user_id"],
        interaction={
            "timestamp": audit_record.timestamp,
            "workflow_type": state["workflow_type"],
            "product_id": state.get("product_data", {}).get("product_id"),
            "risk_score": state.get("risk_assessment", {}).get("overall_score")
        }
    )
    
    state["audit_record"] = audit_record
    
    return state
```

**Audit Log Storage:**

```python
async def write_audit_log(audit_record: AuditRecord):
    """
    Write audit record to S3 with partitioning
    """
    # Partition by date for efficient querying
    date_partition = datetime.utcnow().strftime("%Y/%m/%d")
    
    s3_key = f"audit-logs/{date_partition}/{audit_record.audit_id}.json"
    
    await s3_client.put_object(
        Bucket="swasthcart-audit-logs",
        Key=s3_key,
        Body=json.dumps(audit_record.dict(), indent=2),
        ServerSideEncryption="AES256"
    )
```

**User Interaction History:**

```python
async def update_user_history(user_id: str, interaction: Dict):
    """
    Update user's interaction history in DynamoDB
    """
    await dynamodb.update_item(
        TableName="user_profiles",
        Key={"user_id": user_id},
        UpdateExpression="SET interaction_history = list_append(if_not_exists(interaction_history, :empty_list), :new_interaction)",
        ExpressionAttributeValues={
            ":empty_list": [],
            ":new_interaction": [interaction]
        }
    )
```




## 5. Tool Invocation Architecture

### 5.1 LangChain + MCP Integration

The system integrates deterministic tools via LangChain's tool framework and exposes them through the Model Context Protocol (MCP) for standardized invocation.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Layer                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Agent invokes tool via LangChain                │   │
│  │  tool_result = await tool.ainvoke(input_data)   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              LangChain Tool Framework                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  - Tool discovery and registration               │   │
│  │  - Input validation (Pydantic schemas)           │   │
│  │  - Error handling and retries                    │   │
│  │  - Observability (tracing, logging)              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│           Model Context Protocol (MCP)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  JSON-RPC interface for tool invocation          │   │
│  │  - tools/list: Discover available tools          │   │
│  │  - tools/call: Invoke tool with parameters       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                  Tool Implementations                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Ingredient  │  │     Risk     │  │ Alternative  │  │
│  │  Normalizer  │  │  Calculator  │  │    Ranker    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │     Bias     │  │  Confidence  │                     │
│  │   Detector   │  │  Estimator   │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Tool Catalog

#### 5.2.1 Ingredient Normalizer Tool

**Purpose:** Normalize raw ingredient text to standardized names with category classification.

**Input Schema:**

```python
class IngredientNormalizerInput(BaseModel):
    raw_text: str
    context: Optional[str]  # Product category for disambiguation
```

**Output Schema:**

```python
class IngredientNormalizerOutput(BaseModel):
    normalized_name: str
    category: IngredientCategory
    aliases: List[str]
    confidence: float
```

**Implementation:**

```python
@tool
async def ingredient_normalizer_tool(input_data: IngredientNormalizerInput) -> IngredientNormalizerOutput:
    """
    Normalize ingredient using fuzzy matching and NLP
    """
    raw_text = input_data.raw_text.strip().lower()
    
    # Step 1: Exact match lookup
    exact_match = ingredient_db.get(raw_text)
    if exact_match:
        return IngredientNormalizerOutput(
            normalized_name=exact_match["name"],
            category=exact_match["category"],
            aliases=exact_match["aliases"],
            confidence=1.0
        )
    
    # Step 2: Fuzzy matching
    matches = process.extract(
        raw_text,
        ingredient_db.keys(),
        scorer=fuzz.token_sort_ratio,
        limit=5
    )
    
    best_match, score = matches[0]
    
    if score >= 85:  # High confidence threshold
        ingredient = ingredient_db[best_match]
        return IngredientNormalizerOutput(
            normalized_name=ingredient["name"],
            category=ingredient["category"],
            aliases=ingredient["aliases"],
            confidence=score / 100.0
        )
    
    # Step 3: Pattern-based classification
    category = classify_by_pattern(raw_text)
    
    return IngredientNormalizerOutput(
        normalized_name=raw_text.title(),
        category=category,
        aliases=[],
        confidence=0.5
    )
```

#### 5.2.2 Risk Calculator Tool

**Purpose:** Calculate condition-specific risk scores using rule-based logic.

**Input Schema:**

```python
class RiskCalculatorInput(BaseModel):
    condition: HealthCondition
    ingredients: List[NormalizedIngredient]
    nutrition_facts: NutritionFacts
```

**Output Schema:**

```python
class RiskCalculatorOutput(BaseModel):
    score: int  # 0-100
    factors: List[RiskFactor]
    confidence: float
```

**Implementation:**

```python
@tool
async def risk_calculator_tool(input_data: RiskCalculatorInput) -> RiskCalculatorOutput:
    """
    Calculate condition-specific risk score
    """
    condition = input_data.condition
    ingredients = input_data.ingredients
    nutrition = input_data.nutrition_facts
    
    risk_score = 0
    factors = []
    
    # Ingredient-based risk
    for ingredient in ingredients:
        if ingredient.category in CONDITION_RISK_WEIGHTS[condition]:
            weight = CONDITION_RISK_WEIGHTS[condition][ingredient.category]
            impact = weight * ingredient.confidence
            risk_score += impact
            
            factors.append(RiskFactor(
                factor_name=ingredient.category.value,
                ingredient_or_nutrient=ingredient.normalized_name,
                impact_score=int(impact),
                explanation=f"{ingredient.normalized_name} may impact {condition.value}"
            ))
    
    # Nutrient-based risk
    for nutrient, threshold in CONDITION_NUTRIENT_LIMITS[condition].items():
        nutrient_value = getattr(nutrition, nutrient)
        if nutrient_value > threshold:
            excess_ratio = nutrient_value / threshold
            impact = NUTRIENT_RISK_WEIGHTS[condition][nutrient] * excess_ratio
            risk_score += impact
            
            factors.append(RiskFactor(
                factor_name=f"High {nutrient}",
                ingredient_or_nutrient=nutrient,
                impact_score=int(impact),
                explanation=f"{nutrient.title()} exceeds recommended limit for {condition.value}"
            ))
    
    # Normalize to 0-100
    final_score = min(int(risk_score), 100)
    
    # Sort factors by impact
    factors.sort(key=lambda x: x.impact_score, reverse=True)
    
    return RiskCalculatorOutput(
        score=final_score,
        factors=factors[:10],  # Top 10 factors
        confidence=calculate_confidence(ingredients, nutrition)
    )
```

#### 5.2.3 Alternative Ranker Tool

**Purpose:** Rank alternative products using multi-criteria scoring.

**Input Schema:**

```python
class AlternativeRankerInput(BaseModel):
    original_risk_score: int
    candidates: List[Dict]
    user_preferences: UserPreferences
```

**Output Schema:**

```python
class AlternativeRankerOutput(BaseModel):
    ranked_alternatives: List[Dict]
```

**Implementation:**

```python
@tool
async def alternative_ranker_tool(input_data: AlternativeRankerInput) -> AlternativeRankerOutput:
    """
    Rank alternatives using weighted multi-criteria scoring
    """
    original_score = input_data.original_risk_score
    candidates = input_data.candidates
    preferences = input_data.user_preferences
    
    scored_candidates = []
    
    for candidate in candidates:
        # Health improvement (0-100)
        health_improvement = (original_score - candidate["risk_score"]) / original_score * 100
        
        # Price score (0-100)
        price_ratio = candidate["price"] / preferences.max_price
        price_score = max(0, 100 - (price_ratio - 1) * 100)
        
        # Availability score
        availability_map = {"In stock": 100, "Limited": 50, "Out of stock": 0}
        availability_score = availability_map.get(candidate["availability"], 0)
        
        # Match score (product similarity)
        match_score = candidate.get("match_score", 0.5) * 100
        
        # Weighted final score
        final_score = (
            preferences.health_weight * health_improvement +
            preferences.price_weight * price_score +
            preferences.availability_weight * availability_score +
            preferences.match_weight * match_score
        )
        
        candidate["final_score"] = final_score
        candidate["health_improvement"] = health_improvement
        scored_candidates.append(candidate)
    
    # Sort by final score
    scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    
    return AlternativeRankerOutput(ranked_alternatives=scored_candidates)
```

#### 5.2.4 Bias Detector Tool

**Purpose:** Detect bias, fear-mongering, and inappropriate content in generated text.

**Input Schema:**

```python
class BiasDetectorInput(BaseModel):
    text: str
```

**Output Schema:**

```python
class BiasDetectorOutput(BaseModel):
    has_bias: bool
    bias_type: Optional[str]
    flagged_phrases: List[str]
    severity: Severity
```

**Implementation:**

```python
@tool
async def bias_detector_tool(input_data: BiasDetectorInput) -> BiasDetectorOutput:
    """
    Detect bias and inappropriate content using pattern matching
    """
    text = input_data.text.lower()
    
    flagged_phrases = []
    bias_types = []
    
    # Check for fear-mongering
    for pattern in FEAR_MONGERING_PATTERNS:
        if re.search(pattern, text):
            flagged_phrases.append(pattern)
            bias_types.append("fear_mongering")
    
    # Check for oversimplification
    for pattern in OVERSIMPLIFICATION_PATTERNS:
        if re.search(pattern, text):
            flagged_phrases.append(pattern)
            bias_types.append("oversimplification")
    
    # Check for brand bias
    for pattern in BRAND_BIAS_PATTERNS:
        if re.search(pattern, text):
            flagged_phrases.append(pattern)
            bias_types.append("brand_bias")
    
    # Sentiment analysis for extreme negativity
    sentiment_score = analyze_sentiment(text)
    if sentiment_score < -0.8:  # Very negative
        bias_types.append("extreme_negativity")
    
    has_bias = len(bias_types) > 0
    severity = Severity.CRITICAL if "fear_mongering" in bias_types else Severity.WARNING
    
    return BiasDetectorOutput(
        has_bias=has_bias,
        bias_type=bias_types[0] if bias_types else None,
        flagged_phrases=flagged_phrases,
        severity=severity
    )
```

#### 5.2.5 Confidence Estimator Tool

**Purpose:** Estimate confidence score based on data quality and coverage.

**Input Schema:**

```python
class ConfidenceEstimatorInput(BaseModel):
    ingredient_coverage: int
    nutrition_data_completeness: float
    condition_scores: List[ConditionRiskScore]
```

**Output Schema:**

```python
class ConfidenceEstimatorOutput(BaseModel):
    confidence: float  # 0.0-1.0
    uncertainty_factors: List[str]
```

**Implementation:**

```python
@tool
async def confidence_estimator_tool(input_data: ConfidenceEstimatorInput) -> ConfidenceEstimatorOutput:
    """
    Calculate confidence score based on data quality
    """
    uncertainty_factors = []
    
    # Factor 1: Ingredient coverage
    if input_data.ingredient_coverage < 5:
        uncertainty_factors.append("Limited ingredient data")
        ingredient_score = 0.5
    else:
        ingredient_score = min(input_data.ingredient_coverage / 20, 1.0)
    
    # Factor 2: Nutrition data completeness
    nutrition_score = input_data.nutrition_data_completeness
    if nutrition_score < 0.7:
        uncertainty_factors.append("Incomplete nutrition information")
    
    # Factor 3: Condition score confidence
    avg_condition_confidence = sum(cs.confidence for cs in input_data.condition_scores) / len(input_data.condition_scores)
    if avg_condition_confidence < 0.7:
        uncertainty_factors.append("Low confidence in risk calculations")
    
    # Overall confidence (weighted average)
    overall_confidence = (
        0.4 * ingredient_score +
        0.3 * nutrition_score +
        0.3 * avg_condition_confidence
    )
    
    return ConfidenceEstimatorOutput(
        confidence=overall_confidence,
        uncertainty_factors=uncertainty_factors
    )
```

### 5.3 Tool Registration and Discovery

**MCP Tool Registration:**

```python
from mcp.server import MCPServer

mcp_server = MCPServer("swasthcart-tools")

# Register tools
mcp_server.register_tool(
    name="ingredient_normalizer",
    description="Normalize raw ingredient text to standardized names",
    input_schema=IngredientNormalizerInput.schema(),
    handler=ingredient_normalizer_tool
)

mcp_server.register_tool(
    name="risk_calculator",
    description="Calculate condition-specific risk scores",
    input_schema=RiskCalculatorInput.schema(),
    handler=risk_calculator_tool
)

# ... register other tools
```

**Tool Discovery:**

```python
# Agents can discover available tools
available_tools = await mcp_server.list_tools()

for tool in available_tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Input Schema: {tool.input_schema}")
```




## 6. RAG Design

### 6.1 Vector Database Schema

**Amazon OpenSearch Service Configuration:**

```json
{
  "settings": {
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "knn": true,
      "knn.algo_param.ef_search": 512
    }
  },
  "mappings": {
    "properties": {
      "document_id": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      },
      "metadata": {
        "properties": {
          "source": {"type": "keyword"},
          "publication_date": {"type": "date"},
          "authority_score": {"type": "float"},
          "condition_tags": {"type": "keyword"},
          "document_type": {"type": "keyword"},
          "author": {"type": "text"},
          "journal": {"type": "keyword"}
        }
      }
    }
  }
}
```

### 6.2 Embedding Strategy

**Document Chunking:**

```python
class DocumentChunker:
    """
    Chunk documents for optimal retrieval
    """
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, document: str) -> List[str]:
        """
        Split document into overlapping chunks
        """
        tokens = self.tokenize(document)
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.detokenize(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
```

**Embedding Generation:**

```python
async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings using Amazon Titan
    """
    embeddings = []
    
    # Batch processing (25 texts per call)
    for i in range(0, len(texts), 25):
        batch = texts[i:i + 25]
        
        response = await bedrock_client.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps({
                "inputText": batch
            })
        )
        
        batch_embeddings = response["embedding"]
        embeddings.extend(batch_embeddings)
    
    return embeddings
```

**Document Indexing Pipeline:**

```python
async def index_document(document: Dict):
    """
    Process and index document into OpenSearch
    """
    # Step 1: Chunk document
    chunker = DocumentChunker(chunk_size=512, overlap=50)
    chunks = chunker.chunk_document(document["content"])
    
    # Step 2: Generate embeddings
    embeddings = await generate_embeddings(chunks)
    
    # Step 3: Index each chunk
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        doc_id = f"{document['document_id']}_chunk_{idx}"
        
        await opensearch_client.index(
            index="health-knowledge",
            id=doc_id,
            body={
                "document_id": document["document_id"],
                "title": document["title"],
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "source": document["source"],
                    "publication_date": document["publication_date"],
                    "authority_score": calculate_authority_score(document),
                    "condition_tags": document["condition_tags"],
                    "document_type": document["document_type"],
                    "author": document.get("author"),
                    "journal": document.get("journal")
                }
            }
        )
```

### 6.3 Retrieval Logic

**Hybrid Search Strategy:**

```python
async def hybrid_search(query: str, 
                       filters: Dict,
                       top_k: int = 10) -> List[RetrievedDocument]:
    """
    Combine vector similarity and keyword matching
    """
    # Generate query embedding
    query_embedding = await generate_embeddings([query])
    
    # Hybrid search query
    search_body = {
        "size": top_k * 2,  # Retrieve more for re-ranking
        "query": {
            "bool": {
                "should": [
                    # Vector similarity (70% weight)
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "knn_score",
                                "lang": "knn",
                                "params": {
                                    "field": "embedding",
                                    "query_value": query_embedding[0],
                                    "space_type": "cosinesimil"
                                }
                            },
                            "boost": 0.7
                        }
                    },
                    # Keyword matching (30% weight)
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^2", "content"],
                            "type": "best_fields",
                            "boost": 0.3
                        }
                    }
                ],
                "filter": [
                    {"terms": {"metadata.condition_tags": filters.get("conditions", [])}},
                    {"range": {"metadata.authority_score": {"gte": 0.5}}}
                ]
            }
        }
    }
    
    response = await opensearch_client.search(
        index="health-knowledge",
        body=search_body
    )
    
    # Parse results
    documents = []
    for hit in response["hits"]["hits"]:
        documents.append(RetrievedDocument(
            document_id=hit["_source"]["document_id"],
            title=hit["_source"]["title"],
            content_chunk=hit["_source"]["content"],
            source=hit["_source"]["metadata"]["source"],
            publication_date=hit["_source"]["metadata"]["publication_date"],
            authority_score=hit["_source"]["metadata"]["authority_score"],
            relevance_score=hit["_score"],
            citation=format_citation(hit["_source"])
        ))
    
    return documents
```

**Re-ranking Strategy:**

```python
def rerank_documents(documents: List[RetrievedDocument],
                    query: str,
                    user_conditions: List[HealthCondition]) -> List[RetrievedDocument]:
    """
    Re-rank retrieved documents by relevance, authority, and recency
    """
    for doc in documents:
        # Base score from retrieval
        base_score = doc.relevance_score
        
        # Authority boost
        authority_boost = doc.authority_score * 0.3
        
        # Recency boost (exponential decay)
        days_old = (datetime.now() - datetime.fromisoformat(doc.publication_date)).days
        recency_boost = math.exp(-days_old / 365) * 0.2  # Decay over 1 year
        
        # Condition relevance boost
        condition_boost = 0.0
        if any(cond.value in doc.content_chunk.lower() for cond in user_conditions):
            condition_boost = 0.2
        
        # Final score
        doc.relevance_score = base_score + authority_boost + recency_boost + condition_boost
    
    # Sort by final score
    documents.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return documents
```

### 6.4 Grounding Validation

**Citation Verification:**

```python
def validate_citations(explanation: str, 
                      retrieved_documents: List[RetrievedDocument]) -> bool:
    """
    Verify that all citations in explanation reference valid documents
    """
    # Extract citation markers [1], [2], etc.
    citation_pattern = r'\[(\d+)\]'
    cited_indices = set(int(m) for m in re.findall(citation_pattern, explanation))
    
    # Check all citations are valid
    max_valid_index = len(retrieved_documents)
    
    for idx in cited_indices:
        if idx < 1 or idx > max_valid_index:
            return False
    
    return True
```

**Grounding Check:**

```python
def check_grounding(claim: str, 
                   retrieved_documents: List[RetrievedDocument]) -> float:
    """
    Verify that claim is supported by retrieved documents
    """
    # Simple approach: Check if claim keywords appear in documents
    claim_keywords = extract_keywords(claim)
    
    support_scores = []
    for doc in retrieved_documents:
        doc_keywords = extract_keywords(doc.content_chunk)
        overlap = len(claim_keywords & doc_keywords) / len(claim_keywords)
        support_scores.append(overlap)
    
    # Return max support score
    return max(support_scores) if support_scores else 0.0
```

### 6.5 Knowledge Base Curation

**Document Sources:**

1. **Research Papers**
   - PubMed Central (PMC)
   - Google Scholar
   - Nutrition journals (AJCN, JN, Nutrients)

2. **Clinical Guidelines**
   - WHO dietary guidelines
   - National health organizations (NIH, CDC, ICMR)
   - Diabetes associations (ADA, IDF)
   - Cardiology associations (AHA, ESC)

3. **Nutrition Databases**
   - USDA FoodData Central
   - Indian Food Composition Tables (IFCT)
   - Branded food databases

**Authority Scoring:**

```python
def calculate_authority_score(document: Dict) -> float:
    """
    Calculate authority score based on source credibility
    """
    score = 0.0
    
    # Source type
    source_weights = {
        "peer_reviewed_journal": 1.0,
        "clinical_guideline": 0.95,
        "government_database": 0.9,
        "health_organization": 0.85,
        "nutrition_database": 0.8
    }
    score += source_weights.get(document["document_type"], 0.5)
    
    # Journal impact factor (if applicable)
    if document.get("impact_factor"):
        score += min(document["impact_factor"] / 50, 0.2)  # Cap at 0.2
    
    # Citation count
    if document.get("citation_count"):
        score += min(math.log10(document["citation_count"] + 1) / 10, 0.1)
    
    # Normalize to 0-1
    return min(score, 1.0)
```

**Update Strategy:**

- Weekly: Add new research papers from PubMed
- Monthly: Update nutrition databases
- Quarterly: Review and update clinical guidelines
- Annual: Comprehensive knowledge base audit


## 7. Synthetic Scenario Engine

### 7.1 Architecture

The Synthetic Scenario Engine generates realistic test data for development, testing, and demonstration purposes without exposing real user data.

**Components:**

```
┌─────────────────────────────────────────────────────────┐
│           Synthetic Data Generator                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  - User Profile Generator                        │   │
│  │  - Product Catalog Generator                     │   │
│  │  │  - Cart Scenario Generator                    │   │
│  │  - Interaction Simulator                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│            Synthetic Data Store (Isolated)              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  S3 Bucket: swasthcart-synthetic-data            │   │
│  │  - Synthetic user profiles                       │   │
│  │  - Synthetic product catalog                     │   │
│  │  - Synthetic cart scenarios                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Data Generation

**User Profile Generation:**

```python
class SyntheticUserGenerator:
    """
    Generate realistic synthetic user profiles
    """
    def generate_user_profile(self) -> UserProfile:
        """
        Create synthetic user with realistic health conditions
        """
        # Random health condition combinations
        condition_probabilities = {
            HealthCondition.DIABETES: 0.15,
            HealthCondition.HYPERTENSION: 0.20,
            HealthCondition.PCOS: 0.10,
            HealthCondition.THYROID: 0.12,
            HealthCondition.HEART_DISEASE: 0.08,
            HealthCondition.OBESITY: 0.18
        }
        
        conditions = [
            cond for cond, prob in condition_probabilities.items()
            if random.random() < prob
        ]
        
        # Generate preferences
        preferences = UserPreferences(
            health_weight=random.uniform(0.6, 0.9),
            price_weight=random.uniform(0.1, 0.3),
            availability_weight=random.uniform(0.05, 0.15),
            match_weight=random.uniform(0.05, 0.15),
            max_price=random.uniform(100, 500)
        )
        
        return UserProfile(
            user_id=f"synthetic_{uuid.uuid4()}",
            health_conditions=conditions,
            preferences=preferences,
            age_group=random.choice(["18-30", "31-45", "46-60", "60+"]),
            dietary_restrictions=random.sample(
                ["vegetarian", "vegan", "gluten-free", "lactose-intolerant"],
                k=random.randint(0, 2)
            )
        )
```

**Product Catalog Generation:**

```python
class SyntheticProductGenerator:
    """
    Generate synthetic product data
    """
    def generate_product(self, category: str) -> ProductData:
        """
        Create synthetic product with realistic ingredients
        """
        # Category-specific ingredient templates
        ingredient_templates = {
            "snacks": [
                "refined wheat flour, palm oil, sugar, salt, artificial flavors",
                "corn, vegetable oil, cheese powder, salt, MSG",
                "potatoes, sunflower oil, salt, spices"
            ],
            "beverages": [
                "carbonated water, high fructose corn syrup, caramel color, phosphoric acid",
                "water, sugar, fruit concentrate, citric acid, preservatives",
                "milk, sugar, cocoa powder, stabilizers"
            ],
            "packaged_foods": [
                "rice, lentils, spices, salt, preservatives",
                "wheat flour, water, yeast, salt, sugar",
                "tomatoes, onions, garlic, spices, preservatives"
            ]
        }
        
        ingredients = random.choice(ingredient_templates.get(category, []))
        
        # Generate nutrition facts
        nutrition = NutritionFacts(
            calories=random.randint(100, 500),
            total_fat=random.uniform(0, 30),
            saturated_fat=random.uniform(0, 15),
            trans_fat=random.uniform(0, 2),
            cholesterol=random.uniform(0, 100),
            sodium=random.uniform(100, 1500),
            total_carbohydrates=random.uniform(10, 70),
            dietary_fiber=random.uniform(0, 10),
            total_sugars=random.uniform(0, 40),
            protein=random.uniform(1, 20)
        )
        
        return ProductData(
            product_id=f"synthetic_{uuid.uuid4()}",
            product_name=f"Synthetic {category.title()} Product",
            brand=random.choice(["Brand A", "Brand B", "Brand C"]),
            category=category,
            raw_ingredients=ingredients,
            nutrition_facts=nutrition,
            price=random.uniform(50, 500)
        )
```

**Cart Scenario Generation:**

```python
class SyntheticCartGenerator:
    """
    Generate realistic cart scenarios
    """
    def generate_cart_scenario(self, 
                               user_profile: UserProfile,
                               scenario_type: str) -> CartData:
        """
        Create synthetic cart based on scenario type
        """
        scenarios = {
            "high_risk": {
                "categories": ["snacks", "beverages", "packaged_foods"],
                "product_count": random.randint(8, 15),
                "risk_bias": "high"
            },
            "balanced": {
                "categories": ["snacks", "beverages", "fresh_produce", "dairy"],
                "product_count": random.randint(10, 20),
                "risk_bias": "mixed"
            },
            "health_conscious": {
                "categories": ["fresh_produce", "whole_grains", "lean_protein"],
                "product_count": random.randint(12, 18),
                "risk_bias": "low"
            }
        }
        
        scenario = scenarios[scenario_type]
        products = []
        
        for _ in range(scenario["product_count"]):
            category = random.choice(scenario["categories"])
            product = self.product_generator.generate_product(category)
            products.append(product)
        
        return CartData(
            cart_id=f"synthetic_{uuid.uuid4()}",
            user_id=user_profile.user_id,
            products=products,
            scenario_type=scenario_type
        )
```

### 7.3 Isolation from Production

**Environment Separation:**

```python
class DataEnvironment(Enum):
    PRODUCTION = "production"
    SYNTHETIC = "synthetic"
    DEVELOPMENT = "development"

def get_data_source(environment: DataEnvironment):
    """
    Route to appropriate data source based on environment
    """
    if environment == DataEnvironment.PRODUCTION:
        return ProductionDataSource()
    elif environment == DataEnvironment.SYNTHETIC:
        return SyntheticDataSource()
    else:
        return DevelopmentDataSource()
```

**Access Controls:**

- Synthetic data stored in separate S3 bucket with restricted access
- Synthetic user IDs prefixed with `synthetic_` for easy identification
- Separate DynamoDB tables for synthetic session state
- No cross-contamination between production and synthetic data


