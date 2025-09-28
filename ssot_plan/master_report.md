# NEXUS Platform - SSOT Consolidation Master Plan

**Generated**: 2025-01-27T12:30:00Z
**Version**: 1.0

## Executive Summary

This master plan consolidates the NEXUS Platform into a single SSOT core that owns canonical schemas, configurations, and orchestration manifests. The NUC (NEXUS Unified Core) becomes a managed subsystem (registry + orchestrator) that distributes canonical state; Frenly AI acts as the operator that reads from the SSOT and performs actions. The plan includes a prioritized migration in safe phases, CI enforcement jobs, lockfile strategy, and an audit trail for traceability.

## Canonical File Families (26 Total Anchors)

### A. API/Contract Anchors (2)

- `config/ssot/api_contract_registry.yaml` (Frontend API contracts)
- `config/ssot/backend_api_registry.yaml` (Backend API contracts)

### B. Data Schema Anchors (3)

- `config/ssot/database_schema_registry.yaml` (PostgreSQL schema)
- `config/ssot/redis_schema_registry.yaml` (Redis data structures)
- `config/ssot/cache_schema_registry.yaml` (Cache schemas)

### C. Deployment & Orchestration Anchors (4)

- `config/ssot/kubernetes_registry.yaml` (K8s manifests)
- `config/ssot/docker_registry.yaml` (Docker configurations)
- `config/ssot/infrastructure_registry.yaml` (Infrastructure as Code)
- `config/ssot/environment_registry.yaml` (Environment configurations)

### D. Build & Packaging Anchors (3)

- `config/ssot/frontend_build_registry.yaml` (Frontend build config)
- `config/ssot/backend_build_registry.yaml` (Backend build config)
- `config/ssot/dependency_registry.yaml` (Dependency management)

### E. Automation/Pipeline Anchors (5)

- `config/ssot/ci_pipeline_registry.yaml` (CI workflows)
- `config/ssot/cd_pipeline_registry.yaml` (CD workflows)
- `config/ssot/monitoring_pipeline_registry.yaml` (Monitoring automation)
- `config/ssot/backup_pipeline_registry.yaml` (Backup automation)
- `config/ssot/security_pipeline_registry.yaml` (Security automation)

### F. Operator/Prompt Registry Anchors (4)

- `config/ssot/frenly_ai_registry.yaml` (Frenly AI operator config)
- `config/ssot/agent_prompt_registry.yaml` (Agent prompt templates)
- `config/ssot/template_registry.yaml` (Code templates)
- `config/ssot/operator_policy_registry.yaml` (Operator policies)

### G. Secrets & Policy Anchors (3)

- `config/ssot/security_policy_registry.yaml` (Security policies)
- `config/ssot/compliance_registry.yaml` (Compliance requirements)
- `config/ssot/access_control_registry.yaml` (Access control policies)

### H. Observability & Audit Anchors (2)

- `config/ssot/logging_registry.yaml` (Log formats and schemas)
- `config/ssot/metrics_registry.yaml` (Metrics and monitoring config)

## Phased Migration Plan (6 Phases, 33 Days)

### Phase 0 — Discovery & Snapshot (1 day)

- Run `RepoScanner` → produce `discovery/*` artifacts
- Take immutable snapshot of repo at current state

### Phase 1 — Establish SSOT Registry (2 days)

- Create `ssot/modules_index.yaml` with all 26 anchors
- Set up CODEOWNERS for SSOT anchor families

### Phase 2 — CI Enforcement (3 days)

- Add CI job `ssot-validate` to GitHub Actions
- Implement validation scripts

### Phase 3 — Read-only Integration (5 days)

- Integrate NUC to fetch SSOT snapshot
- Update frontend/backend build steps to read SSOT contracts

### Phase 4 — Controlled Canonicalization (10 days)

- Create PRs to change services to refer to SSOT anchors
- Implement contract tests against SSOT-provided schemas

### Phase 5 — Archive & Cleanup (5 days)

- Archive duplicate configs and non-canonical files
- Update all references to point to SSOT anchors

### Phase 6 — Automation Consolidation (7 days)

- Move all pipeline definitions to SSOT anchors
- NUC drives scheduled jobs based on SSOT

## Acceptance Criteria & Metrics

### Quantitative Metrics

- **Anchor Coverage**: 90% of high-centrality candidates registered in SSOT manifest
- **CI Protection**: `ssot-validate` job passes on draft PRs, blocks unauthorized changes
- **Drift Rate**: <5% duplicate/unaligned config copies within 30 days
- **Build Stability**: No increase in build failures attributable to SSOT integration
- **NUC Sync Latency**: <5 minutes for critical SSOT changes

### Success Criteria

1. All 26 SSOT anchors are registered and validated
2. CI jobs enforce SSOT integrity and prevent unauthorized changes
3. All services successfully consume from SSOT without runtime issues
4. Frenly AI operates entirely from SSOT with no separate truth sources
5. Complete audit trail of all SSOT changes and operations
6. Zero configuration drift after 30 days of operation

This master plan provides a comprehensive roadmap for consolidating the NEXUS Platform into a single SSOT system that ensures consistency, traceability, and maintainability across all components while maintaining safety through phased migration and robust rollback procedures.

---

**Last Updated**: 2025-01-27T12:30:00Z
**Version**: 1.0
**Author**: NEXUS System Architect Agent
**Next Review**: 2025-02-27
**Status**: Ready for Implementation
