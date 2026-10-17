# System Design Outline

Feature: Make all tables non redundant...
Date: 2026-10-17
Project: Vj | Client: Nik

## Overview
Make all tables non redundant

## Architecture & Component Design
Here are actionable design-phase bullet points for eliminating data redundancy:

* **Normalize Schema to 3NF:** Refactor all relational schemas to Third Normal Form (3NF) to eliminate transitive and partial dependencies across tables.
* **Isolate Shared Entities:** Extract repetitive attributes (e.g., addresses, statuses, contact details) into dedicated master/lookup tables to establish a Single Source of Truth (SSOT).
* **Enforce Relational Integrity:** Replace duplicated data columns with foreign key constraints, using surrogate keys where natural composite keys cause cross-table bloat.
* **Resolve Many-to-Many Relationships:** Implement associative (junction) tables with unique compound keys to prevent row-level data duplication.
* **Standardize Lookup & Reference Data:** Consolidate hardcoded and repeated enumerations into centralized reference tables or system-level enum types.
* **Document Caching Strategies:** Mitigate potential query performance impacts caused by increased table joins via indexing strategies or read-only materialized views, rather than schema-level denormalization.

## Next Steps
- Review architecture with senior developers.
- Prepare implementation tasks and task breakdown.
