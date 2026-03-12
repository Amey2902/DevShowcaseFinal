# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - Auto-detected Endpoint Accumulation Bug
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility
  - Test that when a project is re-uploaded with existing auto-detected endpoints, only current endpoints are shown (not accumulated)
  - Test scenarios: Basic re-upload (3→6 endpoints), Mixed endpoints (2 auto + 1 manual → 5 total), Different code re-upload
  - The test assertions should match the Expected Behavior Properties from design (Requirements 2.1, 2.2, 2.3)
  - Run test on UNFIXED code in `devshowcase_backend/projects/services/endpoint_extractor.py`
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause (endpoint accumulation patterns)
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - First-upload and Manual Endpoint Behavior
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (first-time uploads, manual endpoints)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Test scenarios: First-time uploads detect endpoints normally, Manual endpoints preserved during operations, Different projects maintain separate collections, Session deduplication works
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_
 
- [x] 3. Fix for duplicate endpoint detection bug

  - [x] 3.1 Implement the pre-cleanup logic in EndpointExtractor
    - Add pre-cleanup logic in `extract_endpoint_details()` method before endpoint creation loop
    - Delete existing auto-detected endpoints: `self.project.endpoints.filter(auto_detected=True).delete()`
    - Preserve manual endpoints by only targeting `auto_detected=True` records
    - Add debug logging to track cleanup operations (count deleted, count created)
    - Wrap cleanup in try-catch with error handling to prevent upload failure
    - Use database transaction to ensure cleanup and creation happen atomically
    - _Bug_Condition: isBugCondition(input) where input.project has existing auto-detected endpoints AND input.is_reupload == True_
    - _Expected_Behavior: expectedBehavior(result) - only current auto-detected + preserved manual endpoints shown_
    - _Preservation: First-time uploads, manual endpoints, different projects, session deduplication unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Auto-detected Endpoint Replacement
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: Expected Behavior Properties from design (2.1, 2.2, 2.3)_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - First-upload and Manual Endpoint Behavior
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.