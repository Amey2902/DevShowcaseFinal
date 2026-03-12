# Implementation Plan: Web3 Smart Contract Support

## Overview

This implementation extends the existing DevShowcase platform to support Web3 smart contract projects. The solution integrates Web3 detection, Solidity parsing, and mock blockchain testing into the current Django/React architecture without breaking existing functionality.

## Tasks

- [x] 1. Extend Analysis Engine with Web3 Detection
  - [x] 1.1 Add Web3 project detection to analysis_engine.py
    - Extend `_detect_language_and_framework()` method to detect .sol files and Web3 config files
    - Add framework prioritization logic (Hardhat, Truffle, Foundry)
    - Extract framework versions from package.json and config files
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 1.2 Write property test for Web3 project detection
    - **Property 1: Web3 Project Detection**
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [ ]* 1.3 Write property test for framework version detection
    - **Property 2: Framework Version Detection**
    - **Validates: Requirements 1.4, 6.3, 6.4, 6.5**

- [x] 2. Create Web3 Contract Parser
  - [x] 2.1 Create web3_parser.py module
    - Implement Web3ContractParser class with Groq AI integration
    - Add Solidity-specific AI prompt generation
    - Implement rate limiting and batching for Groq free tier
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.2 Implement contract function extraction
    - Parse public and external functions with signatures
    - Extract function visibility and state mutability
    - Handle contract inheritance and imported functions
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

  - [ ]* 2.3 Write property test for comprehensive function extraction
    - **Property 4: Comprehensive Function Extraction**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [ ]* 2.4 Write property test for rate limit compliance
    - **Property 5: Rate Limit Compliance**
    - **Validates: Requirements 2.4**

- [ ] 3. Implement REST Endpoint Conversion
  - [ ] 3.1 Add endpoint conversion logic to web3_parser.py
    - Convert contract functions to REST endpoint format
    - Map view/pure functions to GET, state-changing to POST
    - Generate parameter schemas and response schemas
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 3.2 Write property test for REST endpoint conversion
    - **Property 8: REST Endpoint Conversion**
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 3.3 Write property test for HTTP method mapping
    - **Property 9: HTTP Method Mapping**
    - **Validates: Requirements 3.3**

- [x] 4. Integrate Web3 Parser with Analysis Engine
  - [x] 4.1 Modify analysis_engine.py to use Web3 parser
    - Add Web3 parsing branch in `analyze_project()` method
    - Integrate Web3ContractParser with existing AI analysis flow
    - Ensure fallback to traditional API detection on Web3 failures
    - _Requirements: 7.1, 7.3, 7.4_

  - [x] 4.2 Add Solidity language feature parsing
    - Parse import statements and contract dependencies
    - Handle constructor functions and event definitions
    - Detect contract inheritance and modifiers
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 4.3 Write property test for inheritance resolution
    - **Property 6: Inheritance Resolution**
    - **Validates: Requirements 2.5, 8.2**

  - [ ]* 4.4 Write property test for error resilience
    - **Property 7: Error Resilience**
    - **Validates: Requirements 2.6, 8.6**

- [x] 5. Checkpoint - Ensure Web3 detection and parsing works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Create Web3 Sandbox Handler
  - [x] 6.1 Create web3_service.py in sandbox module
    - Implement Web3SandboxHandler class
    - Add Web3 endpoint detection logic
    - Generate mock blockchain responses for view/pure functions
    - _Requirements: 5.1, 5.2_

  - [x] 6.2 Implement mock transaction responses
    - Generate mock transaction receipts for state-changing functions
    - Include realistic blockchain metadata (block number, gas, hash)
    - Simulate blockchain scenarios (success, revert, out of gas)
    - _Requirements: 5.3, 5.4, 5.6_

  - [ ]* 6.3 Write property test for mock blockchain response generation
    - **Property 13: Mock Blockchain Response Generation**
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 7. Integrate Web3 Sandbox with Existing Service
  - [x] 7.1 Extend SandboxService.execute_sandbox_request()
    - Add Web3 endpoint detection and routing
    - Maintain compatibility with existing SandboxCollection/SandboxRecord
    - Ensure backward compatibility for non-Web3 endpoints
    - _Requirements: 5.5, 7.1, 7.5_

  - [ ]* 7.2 Write property test for sandbox compatibility
    - **Property 15: Sandbox Compatibility**
    - **Validates: Requirements 5.5**

  - [ ]* 7.3 Write property test for backward compatibility
    - **Property 18: Backward Compatibility**
    - **Validates: Requirements 7.1, 7.5**

- [ ] 8. Add Web3 Library Version Detection
  - [ ] 8.1 Implement library version detection in web3_parser.py
    - Detect OpenZeppelin contract versions from imports
    - Identify Uniswap protocol versions from interfaces
    - Extract Web3 library versions from package.json
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 8.2 Write property test for library version detection
    - **Property 17: Library Version Detection**
    - **Validates: Requirements 6.1, 6.2**

- [x] 9. Checkpoint - Ensure Web3 sandbox integration works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Add Web3 UI Indicators (Backend Support)
  - [x] 10.1 Add Web3 endpoint identification in serializers
    - Modify endpoint serialization to include Web3 indicators
    - Add contract name and function metadata to endpoint responses
    - Ensure existing API Playground can display Web3 endpoints
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 10.2 Write property test for Web3 UI integration
    - **Property 12: Web3 UI Integration**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [x] 11. Add Comprehensive Error Handling
  - [x] 11.1 Implement error handling in web3_parser.py
    - Add graceful handling for Solidity parsing errors
    - Implement exponential backoff for Groq API rate limits
    - Add fallback behavior for unsupported Solidity features
    - _Requirements: 2.6, 7.3, 8.6_

  - [x] 11.2 Add error handling in web3_service.py
    - Handle Web3 endpoint detection failures
    - Provide meaningful error messages for mock response generation
    - Ensure graceful degradation when Web3 features fail
    - _Requirements: 7.3_

  - [ ]* 11.3 Write property test for fallback behavior
    - **Property 20: Fallback Behavior**
    - **Validates: Requirements 7.3**

- [ ] 12. Integration Testing and Validation
  - [ ] 12.1 Create integration tests for end-to-end Web3 workflow
    - Test complete flow: upload → detect → parse → generate endpoints → test
    - Validate mixed projects with both traditional APIs and Web3 contracts
    - Test error scenarios and fallback behavior
    - _Requirements: 7.1, 7.3, 7.5_

  - [ ]* 12.2 Write property tests for parameter mapping
    - **Property 10: Parameter Mapping**
    - **Validates: Requirements 3.4, 3.5**

  - [ ]* 12.3 Write property tests for response schema generation
    - **Property 11: Response Schema Generation**
    - **Validates: Requirements 3.6**

  - [ ]* 12.4 Write property tests for blockchain scenario simulation
    - **Property 14: Blockchain Scenario Simulation**
    - **Validates: Requirements 5.4**

- [x] 13. Final Integration and Wiring
  - [x] 13.1 Wire all Web3 components together
    - Ensure Web3 detection flows through to endpoint generation
    - Verify Web3 endpoints appear in API Playground
    - Test Web3 sandbox execution end-to-end
    - _Requirements: 7.1, 7.2, 7.4, 7.5_

  - [x] 13.2 Add comprehensive logging and monitoring
    - Add debug logging for Web3 detection and parsing
    - Log Web3 sandbox request/response cycles
    - Monitor Groq API usage and rate limiting
    - _Requirements: 2.4, 2.6_

  - [ ]* 13.3 Write property tests for interface consistency
    - **Property 19: Interface Consistency**
    - **Validates: Requirements 7.2**

  - [ ]* 13.4 Write property tests for AI integration reuse
    - **Property 21: AI Integration Reuse**
    - **Validates: Requirements 7.4**

  - [ ]* 13.5 Write property tests for Solidity language feature parsing
    - **Property 22: Solidity Language Feature Parsing**
    - **Validates: Requirements 8.1, 8.3, 8.4, 8.5**

- [x] 14. Final checkpoint - Ensure complete Web3 integration
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Integration tests ensure Web3 features work seamlessly with existing functionality
- Checkpoints ensure incremental validation throughout implementation
- All Web3 functionality extends existing systems without breaking current features