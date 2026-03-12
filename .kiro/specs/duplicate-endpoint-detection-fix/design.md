# Duplicate Endpoint Detection Fix Design

## Overview

The endpoint detection system incorrectly accumulates endpoints during project re-uploads instead of replacing them. When users re-upload the same project, auto-detected endpoints are added to existing ones, creating duplicates (e.g., 6 endpoints instead of 3). This fix implements selective endpoint clearing that removes only auto-detected endpoints while preserving manually created ones during re-upload.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when a project is re-uploaded and auto-detected endpoints already exist
- **Property (P)**: The desired behavior when re-uploading - only current endpoints should be displayed, with manual endpoints preserved
- **Preservation**: Existing manually created endpoints and first-time upload behavior that must remain unchanged by the fix
- **EndpointExtractor**: The service in `devshowcase_backend/projects/services/endpoint_extractor.py` that saves detected endpoints to the database
- **auto_detected**: The boolean field on Endpoint model that distinguishes auto-detected from manually created endpoints

## Bug Details

### Fault Condition

The bug manifests when a user re-uploads a project that already has auto-detected endpoints. The `EndpointExtractor.extract_endpoint_details()` method creates new endpoint records without clearing existing auto-detected ones, causing accumulation.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type ProjectUploadContext
  OUTPUT: boolean
  
  RETURN input.project.endpoints.filter(auto_detected=True).exists()
         AND input.is_reupload == True
         AND input.new_endpoints_detected > 0
END FUNCTION
```

### Examples

- **Example 1**: Project initially uploaded with 3 endpoints → Re-upload detects same 3 endpoints → User sees 6 total endpoints (3 original + 3 duplicates)
- **Example 2**: Project with 2 auto-detected + 1 manual endpoint → Re-upload detects 2 endpoints → User sees 5 total endpoints (2 original auto + 1 manual + 2 new auto)
- **Example 3**: Project with mixed endpoints → Re-upload with different code → Should show only new auto-detected + preserved manual endpoints
- **Edge Case**: Re-upload detects no endpoints → Should clear all auto-detected endpoints, preserve manual ones

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- First-time project uploads must continue to detect and save endpoints normally
- Manually created endpoints must be preserved during any re-upload operation
- Within-session endpoint deduplication must continue to work as before
- Different projects must maintain completely separate endpoint collections

**Scope:**
All upload scenarios that do NOT involve re-uploading a project with existing auto-detected endpoints should be completely unaffected by this fix. This includes:
- First-time uploads to new projects
- Uploads to projects with only manual endpoints
- Manual endpoint creation through the UI
- Endpoint deletion operations

## Hypothesized Root Cause

Based on the code analysis, the root cause is in the `EndpointExtractor.extract_endpoint_details()` method:

1. **Missing Cleanup Logic**: The method directly creates new endpoints without checking for existing auto-detected ones
   - Located in `devshowcase_backend/projects/services/endpoint_extractor.py` line 66
   - Uses `Endpoint.objects.create()` without any pre-cleanup

2. **No Re-upload Detection**: The system doesn't distinguish between first-time uploads and re-uploads
   - The upload pipeline in `tasks.py` treats all uploads identically
   - No logic to identify when a project already has endpoints

3. **Lack of Selective Deletion**: No mechanism exists to delete only auto-detected endpoints while preserving manual ones
   - The `auto_detected=True` field exists but isn't used for cleanup
   - Manual endpoints (auto_detected=False) need to be preserved

4. **Session-only Deduplication**: Current deduplication only works within a single upload session
   - Uses `seen_endpoints` set that resets for each upload
   - Doesn't check against existing database records

## Correctness Properties

Property 1: Fault Condition - Auto-detected Endpoint Replacement

_For any_ project re-upload where auto-detected endpoints already exist (isBugCondition returns true), the fixed EndpointExtractor SHALL clear existing auto-detected endpoints before saving new ones, ensuring only the current set of detected endpoints plus preserved manual endpoints are displayed.

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation - Manual Endpoint and First-upload Behavior

_For any_ upload scenario where the bug condition does NOT hold (first-time uploads, projects with only manual endpoints), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing functionality for non-buggy scenarios.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**
## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `devshowcase_backend/projects/services/endpoint_extractor.py`

**Function**: `extract_endpoint_details`

**Specific Changes**:
1. **Add Pre-cleanup Logic**: Before creating new endpoints, delete existing auto-detected ones for the project
   - Add `self.project.endpoints.filter(auto_detected=True).delete()` before the endpoint creation loop
   - This ensures only current auto-detected endpoints remain

2. **Preserve Manual Endpoints**: Ensure the cleanup only affects auto-detected endpoints
   - Use `auto_detected=True` filter to target only automatically detected endpoints
   - Manual endpoints (auto_detected=False or None) will be preserved

3. **Add Logging**: Include debug logging to track cleanup operations
   - Log count of endpoints deleted during cleanup
   - Log count of new endpoints created

4. **Error Handling**: Wrap cleanup in try-catch to prevent upload failure
   - If cleanup fails, log error but continue with endpoint creation
   - Ensure upload doesn't fail due to cleanup issues

5. **Transaction Safety**: Ensure cleanup and creation happen atomically
   - Use database transaction to ensure consistency
   - If endpoint creation fails, cleanup should be rolled back

**Alternative Approach (if needed)**: If the above approach causes issues, implement a two-phase approach:
- Phase 1: Mark existing auto-detected endpoints as "to_be_replaced" 
- Phase 2: After successful new endpoint creation, delete marked endpoints
- This provides better rollback capability if new endpoint creation fails

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Create test scenarios that simulate project re-uploads with existing auto-detected endpoints. Run these tests on the UNFIXED code to observe endpoint accumulation and understand the exact failure patterns.

**Test Cases**:
1. **Basic Re-upload Test**: Upload project with 3 endpoints, then re-upload same project (will fail on unfixed code - shows 6 endpoints)
2. **Mixed Endpoints Test**: Project with 2 auto + 1 manual endpoint, re-upload detects 2 endpoints (will fail on unfixed code - shows 5 endpoints)
3. **Different Code Re-upload**: Re-upload with modified code that has different endpoints (will fail on unfixed code - shows old + new)
4. **No Endpoints Re-upload**: Re-upload project where new analysis finds no endpoints (may fail on unfixed code - old endpoints remain)

**Expected Counterexamples**:
- Endpoint counts increase with each re-upload instead of staying constant
- Possible causes: missing cleanup logic, no re-upload detection, session-only deduplication

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := extract_endpoint_details_fixed(input)
  ASSERT expectedBehavior(result)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT extract_endpoint_details_original(input) = extract_endpoint_details_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for first-time uploads and manual endpoint operations, then write property-based tests capturing that behavior.

**Test Cases**:
1. **First-time Upload Preservation**: Verify new projects continue to detect and save endpoints correctly
2. **Manual Endpoint Preservation**: Verify manually created endpoints are never deleted during re-uploads
3. **Different Project Preservation**: Verify re-uploads to different projects don't affect each other
4. **Session Deduplication Preservation**: Verify within-session deduplication continues working

### Unit Tests

- Test endpoint cleanup logic with various existing endpoint configurations
- Test preservation of manual endpoints during cleanup
- Test error handling when cleanup or creation fails
- Test transaction rollback scenarios

### Property-Based Tests

- Generate random project configurations with mixed auto/manual endpoints and verify correct cleanup
- Generate random re-upload scenarios and verify endpoint counts are correct
- Test that all non-re-upload scenarios continue to work across many configurations

### Integration Tests

- Test full upload pipeline with re-upload scenarios
- Test UI behavior showing correct endpoint counts after re-upload
- Test that API playground continues to work with cleaned endpoints