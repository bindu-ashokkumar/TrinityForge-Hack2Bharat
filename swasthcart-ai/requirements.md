# Requirements Document: SwasthCart AI

## Introduction

SwasthCart AI is a preventive health intelligence extension that provides personalized, explainable health risk analysis for grocery and quick-commerce platforms. The system analyzes product ingredients, nutritional metadata, and shopping cart composition against user-specified health conditions to generate risk scores, evidence-based explanations, and safer alternative recommendations.

The system operates as a stateful agentic architecture orchestrated by LangGraph, utilizing specialized agents, large language models, retrieval-augmented generation, and vector databases. It is designed for deployment as a browser extension (MVP), mobile SDK, or REST API for enterprise integration.

This document specifies functional and non-functional requirements following EARS (Easy Approach to Requirements Syntax) patterns and INCOSE quality standards.

## Glossary

- **SwasthCart_System**: The complete preventive health intelligence platform including all agents, orchestration, and interfaces
- **Risk_Score**: A numerical value (0-100) representing the health risk level of a product or cart for a specific user profile
- **Health_Profile**: User-specified health conditions, dietary restrictions, and sensitivity parameters
- **Product_Analysis_Agent**: Specialized agent responsible for ingredient extraction and normalization
- **Risk_Scoring_Agent**: Specialized agent that calculates health risk scores based on ingredients and health profiles
- **RAG_Retrieval_Agent**: Specialized agent that retrieves evidence from vector database for explanation grounding
- **Explanation_Synthesis_Agent**: Specialized agent that generates human-readable explanations with citations
- **Cart_Aggregation_Agent**: Specialized agent that computes cart-level health scores and patterns
- **Alternative_Recommendation_Agent**: Specialized agent that identifies and ranks safer product alternatives
- **Validation_Guardrail_Agent**: Specialized agent that enforces safety constraints and validates outputs
- **Audit_Logging_Agent**: Specialized agent that records decision trails and compliance data
- **LangGraph_Orchestrator**: The stateful workflow engine that coordinates agent execution and manages session state
- **Vector_Database**: Amazon OpenSearch service storing embeddings of dietary guidelines, research, and ingredient data
- **Knowledge_Store**: Structured repository of ingredient risk mappings, condition sensitivity matrices, and classification indices
- **Tool_Invocation_Layer**: MCP-based interface for agents to invoke deterministic functions and external services
- **Synthetic_Scenario_Engine**: Testing framework that generates simulated ingredient-risk interactions for model validation
- **Swasth_Mode**: User-controlled toggle that enables or disables the health intelligence overlay
- **Individual_Mode**: Scoring configuration for a single user's health profile
- **Family_Mode**: Scoring configuration that considers multiple health profiles simultaneously
- **Confidence_Score**: A numerical value (0-1) representing the system's certainty in its risk assessment
- **Grounding_Citation**: A reference snippet from the vector database that supports an explanation
- **Medical_Claim**: Any statement that diagnoses, treats, cures, or prevents disease (explicitly prohibited)
- **PHI**: Protected Health Information as defined by HIPAA (explicitly excluded from system scope)
- **Guardrail**: A safety mechanism that validates, filters, or overrides agent outputs
- **Audit_Trail**: A complete log of agent decisions, tool invocations, and risk calculations for a session
- **Deterministic_Override**: A rule-based fallback mechanism when agent confidence is below threshold
- **Ultra_Processed_Classification**: A categorization system for food processing levels based on NOVA framework
- **Ingredient_Metadata**: Structured data about ingredients including chemical composition, additives, and allergens
- **Risk_Weight**: A numerical coefficient representing the severity of a specific ingredient for a health condition
- **Sensitivity_Matrix**: A lookup table mapping health conditions to ingredient sensitivities
- **Safer_Alternative**: A product with lower risk score that serves similar culinary purpose
- **Cart_Health_Score**: An aggregated risk score computed across all products in a shopping cart
- **Session_Memory**: Stateful context maintained by LangGraph across multiple agent invocations
- **Hallucination_Mitigation**: Guardrail mechanisms that detect and suppress ungrounded LLM outputs
- **Prompt_Injection**: Malicious user input designed to manipulate agent behavior (explicitly protected against)
- **Model_Versioning**: The practice of tracking and managing different versions of LLMs and datasets
- **Drift_Detection**: Monitoring mechanism that identifies degradation in model performance over time
- **Graceful_Degradation**: System behavior that maintains partial functionality when components fail

## Requirements

### Requirement 1: Product Risk Analysis

**User Story:** As a health-conscious shopper, I want to see personalized risk scores for products I'm viewing, so that I can make informed purchasing decisions aligned with my health conditions.

#### Acceptance Criteria

1. WHEN a user views a product page with Swasth Mode enabled, THE SwasthCart_System SHALL display a Risk_Score within 3 seconds
2. WHEN the Product_Analysis_Agent receives product data, THE Product_Analysis_Agent SHALL extract and normalize all ingredients from the ingredient list
3. WHEN the Risk_Scoring_Agent receives normalized ingredients and a Health_Profile, THE Risk_Scoring_Agent SHALL calculate a Risk_Score between 0 and 100
4. WHEN the Risk_Score is calculated, THE SwasthCart_System SHALL display the score with color-coded visual indicators (green: 0-33, yellow: 34-66, red: 67-100)
5. WHEN the user clicks on the Risk_Score, THE Explanation_Synthesis_Agent SHALL generate a human-readable explanation with Grounding_Citations
6. WHEN the Explanation_Synthesis_Agent generates an explanation, THE Validation_Guardrail_Agent SHALL verify that the explanation contains no Medical_Claims
7. WHEN the Risk_Scoring_Agent confidence is below 0.6, THE SwasthCart_System SHALL invoke the Deterministic_Override mechanism
8. WHEN product Ingredient_Metadata is incomplete, THE SwasthCart_System SHALL display a confidence indicator reflecting data quality
