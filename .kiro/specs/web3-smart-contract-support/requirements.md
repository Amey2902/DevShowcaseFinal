# Requirements Document

## Introduction

This feature extends the DevShowcase project's API analysis capabilities to support Web3 smart contract projects. The system will detect Solidity-based projects, parse smart contract functions using AI, convert them to REST-like API endpoints, and enable testing in the existing sandbox environment with mock blockchain responses.

## Glossary

- **Smart_Contract**: A self-executing contract with terms directly written into code on a blockchain
- **Solidity**: Programming language for writing smart contracts on Ethereum-compatible blockchains
- **Web3_Framework**: Development framework for smart contract projects (Hardhat, Truffle, Foundry)
- **Contract_Function**: Public or external function in a smart contract that can be called
- **Mock_Blockchain_Response**: Simulated blockchain transaction response for testing purposes
- **Analysis_Engine**: The existing Django service that uses Groq AI for code analysis
- **API_Playground**: The existing React component for testing API endpoints
- **Sandbox_Environment**: The existing system for executing and testing API calls with mock data

## Requirements

### Requirement 1: Detect Web3 Projects

**User Story:** As a developer, I want the system to automatically detect Web3 smart contract projects, so that I can analyze them without manual configuration.

#### Acceptance Criteria

1. WHEN a project contains .sol files, THE Analysis_Engine SHALL identify it as a Web3 project
2. WHEN a project contains hardhat.config.js OR truffle-config.js OR foundry.toml, THE Analysis_Engine SHALL identify it as a Web3 project
3. WHEN a Web3 project is detected, THE Analysis_Engine SHALL determine the specific framework type (Hardhat, Truffle, Foundry)
4. THE Analysis_Engine SHALL detect Web3 framework versions from package.json and config files
5. WHEN multiple Web3 frameworks are present, THE Analysis_Engine SHALL prioritize based on config file presence

### Requirement 2: Parse Smart Contract Functions

**User Story:** As a developer, I want the system to extract public and external functions from my smart contracts, so that I can understand the available API surface.

#### Acceptance Criteria

1. WHEN analyzing Solidity files, THE Analysis_Engine SHALL identify all public and external functions
2. THE Analysis_Engine SHALL extract function signatures including parameters and return types
3. THE Analysis_Engine SHALL identify function visibility (public, external) and state mutability (view, pure, payable)
4. WHEN parsing contract functions, THE Analysis_Engine SHALL respect Groq free tier rate limits
5. THE Analysis_Engine SHALL detect inherited functions from imported contracts (OpenZeppelin, etc.)
6. WHEN encountering parsing errors, THE Analysis_Engine SHALL log the error and continue with other contracts

### Requirement 3: Convert Functions to REST Endpoints

**User Story:** As a developer, I want smart contract functions converted to REST-like endpoints, so that I can test them in the familiar API Playground interface.

#### Acceptance Criteria

1. THE Analysis_Engine SHALL convert each contract function to a REST endpoint format
2. WHEN converting functions, THE Analysis_Engine SHALL use the pattern `/contracts/{ContractName}/{functionName}`
3. THE Analysis_Engine SHALL map view/pure functions to GET requests and state-changing functions to POST requests
4. THE Analysis_Engine SHALL include function parameters as request body schema for POST endpoints
5. THE Analysis_Engine SHALL include function parameters as query parameters for GET endpoints
6. THE Analysis_Engine SHALL generate response schemas based on function return types

### Requirement 4: Display Web3 Endpoints in API Playground

**User Story:** As a developer, I want to see Web3 endpoints alongside traditional API endpoints, so that I can test all my project's APIs in one place.

#### Acceptance Criteria

1. THE API_Playground SHALL display Web3 endpoints with a distinct visual indicator
2. THE API_Playground SHALL group endpoints by smart contract name
3. THE API_Playground SHALL show function visibility and state mutability in the endpoint description
4. WHEN displaying Web3 endpoints, THE API_Playground SHALL use existing UI components without modification
5. THE API_Playground SHALL indicate when an endpoint represents a blockchain transaction vs query

### Requirement 5: Test Web3 Endpoints with Mock Responses

**User Story:** As a developer, I want to test Web3 endpoints in the sandbox environment, so that I can validate my smart contract interfaces without deploying to a blockchain.

#### Acceptance Criteria

1. THE Sandbox_Environment SHALL execute Web3 endpoint tests with mock blockchain responses
2. WHEN testing view/pure functions, THE Sandbox_Environment SHALL return mock data matching the function's return type
3. WHEN testing state-changing functions, THE Sandbox_Environment SHALL return mock transaction receipts
4. THE Sandbox_Environment SHALL simulate common blockchain scenarios (success, revert, out of gas)
5. THE Sandbox_Environment SHALL maintain compatibility with existing SandboxCollection and SandboxRecord classes
6. WHEN generating mock responses, THE Sandbox_Environment SHALL include realistic blockchain metadata (block number, gas used, transaction hash)

### Requirement 6: Detect Web3 Library Versions

**User Story:** As a developer, I want the system to identify specific versions of Web3 libraries I'm using, so that I can understand compatibility and feature availability.

#### Acceptance Criteria

1. THE Analysis_Engine SHALL detect OpenZeppelin contract versions from import statements
2. THE Analysis_Engine SHALL identify Uniswap protocol versions (v2, v3) from contract interfaces
3. THE Analysis_Engine SHALL extract Web3 library versions from package.json dependencies
4. WHEN version detection fails, THE Analysis_Engine SHALL continue analysis with generic Web3 support
5. THE Analysis_Engine SHALL store detected library versions in the project metadata

### Requirement 7: Integrate with Existing Backend Architecture

**User Story:** As a system maintainer, I want Web3 support to integrate seamlessly with existing code, so that maintenance overhead is minimized.

#### Acceptance Criteria

1. THE Analysis_Engine SHALL extend existing framework detection logic without breaking current functionality
2. THE Web3_Parser SHALL follow the same interface pattern as existing framework parsers
3. WHEN Web3 analysis fails, THE Analysis_Engine SHALL fall back to traditional API detection
4. THE Analysis_Engine SHALL reuse existing Groq AI integration for smart contract parsing
5. THE Web3_Support SHALL integrate with existing Django models and serializers without schema changes

### Requirement 8: Handle Solidity Language Features

**User Story:** As a developer, I want the system to understand Solidity-specific language features, so that my smart contract analysis is accurate.

#### Acceptance Criteria

1. THE Analysis_Engine SHALL parse Solidity import statements to identify contract dependencies
2. THE Analysis_Engine SHALL handle contract inheritance and interface implementations
3. THE Analysis_Engine SHALL identify constructor functions and their parameters
4. THE Analysis_Engine SHALL parse event definitions and include them in the API documentation
5. THE Analysis_Engine SHALL handle Solidity modifiers and their impact on function behavior
6. WHEN encountering unsupported Solidity features, THE Analysis_Engine SHALL log warnings and continue parsing