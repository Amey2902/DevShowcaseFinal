from django.test import TestCase
from django.contrib.auth.models import User
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from projects.models import Project, ProjectUpload, Endpoint
from projects.services.endpoint_extractor import EndpointExtractor


# Property-based test generators
@st.composite
def endpoint_data_sets(draw):
    """Generate diverse sets of endpoint data for testing."""
    # Generate 1-6 endpoints
    num_endpoints = draw(st.integers(min_value=1, max_value=6))
    
    endpoints = []
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    for i in range(num_endpoints):
        method = draw(st.sampled_from(methods))
        path = f"/api/endpoint{i}"
        name = f"{method} {path}"
        
        endpoint_data = {
            'method': method,
            'path': path,
            'name': name,
            'description': f'Test endpoint {i}',
            'file': f'src/routes/endpoint{i}.py',
            'line': draw(st.integers(min_value=1, max_value=100)),
            'path_parameters': [],
            'query_parameters': [],
            'auth_required': draw(st.booleans()),
            'auth_type': draw(st.sampled_from(['', 'Bearer', 'Basic'])),
            'request_schema': {},
            'response_schema': {}
        }
        
        endpoints.append(endpoint_data)
    
    return endpoints


@st.composite
def reupload_scenarios(draw):
    """Generate re-upload scenarios with different endpoint configurations."""
    # First upload endpoints
    first_endpoints = draw(endpoint_data_sets())

    # Second upload endpoints - could be same, different, or subset
    scenario_type = draw(st.sampled_from(['same', 'different', 'subset', 'superset']))

    if scenario_type == 'same':
        second_endpoints = first_endpoints.copy()
    elif scenario_type == 'different':
        second_endpoints = draw(endpoint_data_sets())
    elif scenario_type == 'subset':
        if len(first_endpoints) > 1:
            subset_size = draw(st.integers(min_value=1, max_value=len(first_endpoints)-1))
            second_endpoints = first_endpoints[:subset_size]
        else:
            second_endpoints = first_endpoints.copy()
    else:  # superset
        second_endpoints = first_endpoints.copy()
        additional = draw(endpoint_data_sets())

        # Ensure additional endpoints don't duplicate existing ones
        existing_keys = {f"{ep['method']}:{ep['path']}" for ep in second_endpoints}
        unique_additional = []

        for ep in additional:
            key = f"{ep['method']}:{ep['path']}"
            if key not in existing_keys:
                unique_additional.append(ep)
                existing_keys.add(key)

        # If no unique additional endpoints, create at least one unique endpoint
        if not unique_additional:
            # Find a unique path by incrementing the endpoint number
            max_endpoint_num = max([
                int(ep['path'].split('endpoint')[-1]) if 'endpoint' in ep['path'] else 0
                for ep in second_endpoints
            ], default=0)

            unique_additional = [{
                'method': 'GET',
                'path': f'/api/endpoint{max_endpoint_num + 1}',
                'name': f'GET /api/endpoint{max_endpoint_num + 1}',
                'description': f'Test endpoint {max_endpoint_num + 1}',
                'file': f'src/routes/endpoint{max_endpoint_num + 1}.py',
                'line': 1,
                'path_parameters': [],
                'query_parameters': [],
                'auth_required': False,
                'auth_type': '',
                'request_schema': {},
                'response_schema': {}
            }]

        second_endpoints.extend(unique_additional)

    return {
        'first_upload': first_endpoints,
        'second_upload': second_endpoints,
        'scenario_type': scenario_type
    }



class TestEndpointExtractorBugCondition(HypothesisTestCase):
    """
    Bug condition exploration tests for endpoint accumulation bug.
    
    CRITICAL: These tests MUST FAIL on unfixed code - failure confirms the bug exists.
    DO NOT attempt to fix the test or the code when it fails.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            title='Test Project',
            short_description='Test project for endpoint extraction'
        )
    
    def _create_upload_instance(self):
        """Helper to create a ProjectUpload instance."""
        return ProjectUpload.objects.create(
            project=self.project,
            user=self.user,
            upload_method='files',
            status='analyzing'
        )
    
    def _create_manual_endpoint(self, name="Manual Endpoint", method="GET", url="http://example.com/manual"):
        """Helper to create a manual endpoint."""
        return Endpoint.objects.create(
            project=self.project,
            name=name,
            method=method,
            url=url,
            description="Manually created endpoint",
            auto_detected=False
        )
    
    @given(scenario=reupload_scenarios())
    @settings(max_examples=50, deadline=10000)
    def test_fault_condition_auto_detected_endpoint_replacement(self, scenario):
        """
        **Property 1: Fault Condition** - Auto-detected Endpoint Accumulation Bug
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        
        CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
        
        For any project re-upload where auto-detected endpoints already exist, the system 
        SHALL clear existing auto-detected endpoints before saving new ones, ensuring only 
        the current set of detected endpoints are displayed (not accumulated).
        
        Test scenarios:
        - Basic re-upload (3→6 endpoints shows bug)
        - Mixed endpoints (2 auto + 1 manual → 5 total shows bug)  
        - Different code re-upload (should show only new endpoints)
        """
        # Arrange - First upload with initial endpoints
        first_upload = self._create_upload_instance()
        first_extractor = EndpointExtractor(first_upload)
        
        first_endpoints_data = scenario['first_upload']
        first_count = first_extractor.extract_endpoint_details(first_endpoints_data)
        
        # Verify first upload worked
        initial_auto_endpoints = self.project.endpoints.filter(auto_detected=True).count()
        self.assertEqual(initial_auto_endpoints, first_count)
        self.assertEqual(initial_auto_endpoints, len(first_endpoints_data))
        
        # Add a manual endpoint to test preservation
        manual_endpoint = self._create_manual_endpoint()
        total_before_reupload = self.project.endpoints.count()
        manual_count = self.project.endpoints.filter(auto_detected=False).count()
        self.assertEqual(manual_count, 1)
        
        # Act - Second upload (re-upload scenario)
        second_upload = self._create_upload_instance()
        second_extractor = EndpointExtractor(second_upload)
        
        second_endpoints_data = scenario['second_upload']
        second_count = second_extractor.extract_endpoint_details(second_endpoints_data)
        
        # Assert - Expected behavior (this will FAIL on unfixed code, proving bug exists)
        
        # Property 2.1: System SHALL clear existing auto-detected endpoints and show only current set
        final_auto_endpoints = self.project.endpoints.filter(auto_detected=True).count()
        expected_auto_count = len(second_endpoints_data)
        
        self.assertEqual(
            final_auto_endpoints, 
            expected_auto_count,
            f"Expected {expected_auto_count} auto-detected endpoints after re-upload, "
            f"but found {final_auto_endpoints}. This indicates endpoint accumulation bug. "
            f"Scenario: {scenario['scenario_type']}, "
            f"First upload: {len(first_endpoints_data)} endpoints, "
            f"Second upload: {len(second_endpoints_data)} endpoints"
        )
        
        # Property 2.2: System SHALL display only actual number of unique endpoints from latest upload
        total_endpoints = self.project.endpoints.count()
        expected_total = expected_auto_count + manual_count  # auto + manual
        
        self.assertEqual(
            total_endpoints,
            expected_total,
            f"Expected {expected_total} total endpoints (auto + manual), "
            f"but found {total_endpoints}. This indicates endpoint accumulation bug."
        )
        
        # Property 2.3: System SHALL preserve manually created endpoints during re-upload
        final_manual_endpoints = self.project.endpoints.filter(auto_detected=False).count()
        self.assertEqual(
            final_manual_endpoints,
            manual_count,
            f"Manual endpoints should be preserved during re-upload. "
            f"Expected {manual_count}, found {final_manual_endpoints}"
        )
        
        # Additional verification: Check that manual endpoint still exists
        self.assertTrue(
            Endpoint.objects.filter(id=manual_endpoint.id).exists(),
            "Manual endpoint should not be deleted during re-upload"
        )


class TestEndpointExtractorBugConditionUnits(TestCase):
    """Unit tests for specific bug condition scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            title='Test Project',
            short_description='Test project for endpoint extraction'
        )
    
    def _create_upload_instance(self):
        """Helper to create a ProjectUpload instance."""
        return ProjectUpload.objects.create(
            project=self.project,
            user=self.user,
            upload_method='files',
            status='analyzing'
        )
    
    def test_basic_reupload_accumulation_bug(self):
        """
        Test basic re-upload scenario: 3 endpoints → re-upload same 3 → should show 3, not 6.
        
        CRITICAL: This test MUST FAIL on unfixed code (showing 6 endpoints instead of 3).
        """
        # Arrange - Initial upload with 3 endpoints
        upload1 = self._create_upload_instance()
        extractor1 = EndpointExtractor(upload1)
        
        initial_endpoints = [
            {'method': 'GET', 'path': '/api/users', 'name': 'GET /api/users', 'description': 'Get users'},
            {'method': 'POST', 'path': '/api/users', 'name': 'POST /api/users', 'description': 'Create user'},
            {'method': 'GET', 'path': '/api/posts', 'name': 'GET /api/posts', 'description': 'Get posts'}
        ]
        
        count1 = extractor1.extract_endpoint_details(initial_endpoints)
        self.assertEqual(count1, 3)
        self.assertEqual(self.project.endpoints.filter(auto_detected=True).count(), 3)
        
        # Act - Re-upload same project with same 3 endpoints
        upload2 = self._create_upload_instance()
        extractor2 = EndpointExtractor(upload2)
        
        count2 = extractor2.extract_endpoint_details(initial_endpoints)
        
        # Assert - Should show 3 endpoints, not 6 (this will FAIL on unfixed code)
        final_count = self.project.endpoints.filter(auto_detected=True).count()
        self.assertEqual(
            final_count, 
            3,
            f"Expected 3 endpoints after re-upload, but found {final_count}. "
            f"This indicates the endpoint accumulation bug exists."
        )
    
    def test_mixed_endpoints_reupload_bug(self):
        """
        Test mixed endpoints scenario: 2 auto + 1 manual → re-upload 2 auto → should show 2 auto + 1 manual = 3 total.
        
        CRITICAL: This test MUST FAIL on unfixed code (showing 5 total instead of 3).
        """
        # Arrange - Initial upload with 2 auto-detected endpoints
        upload1 = self._create_upload_instance()
        extractor1 = EndpointExtractor(upload1)
        
        initial_endpoints = [
            {'method': 'GET', 'path': '/api/data', 'name': 'GET /api/data', 'description': 'Get data'},
            {'method': 'POST', 'path': '/api/data', 'name': 'POST /api/data', 'description': 'Create data'}
        ]
        
        extractor1.extract_endpoint_details(initial_endpoints)
        
        # Add 1 manual endpoint
        manual_endpoint = Endpoint.objects.create(
            project=self.project,
            name="Manual API",
            method="PUT",
            url="http://example.com/manual",
            description="Manually created endpoint",
            auto_detected=False
        )
        
        # Verify initial state: 2 auto + 1 manual = 3 total
        self.assertEqual(self.project.endpoints.filter(auto_detected=True).count(), 2)
        self.assertEqual(self.project.endpoints.filter(auto_detected=False).count(), 1)
        self.assertEqual(self.project.endpoints.count(), 3)
        
        # Act - Re-upload with same 2 endpoints
        upload2 = self._create_upload_instance()
        extractor2 = EndpointExtractor(upload2)
        
        extractor2.extract_endpoint_details(initial_endpoints)
        
        # Assert - Should show 2 auto + 1 manual = 3 total (this will FAIL on unfixed code showing 5)
        final_auto = self.project.endpoints.filter(auto_detected=True).count()
        final_manual = self.project.endpoints.filter(auto_detected=False).count()
        final_total = self.project.endpoints.count()
        
        self.assertEqual(
            final_auto, 
            2,
            f"Expected 2 auto-detected endpoints after re-upload, but found {final_auto}. "
            f"This indicates endpoint accumulation bug."
        )
        
        self.assertEqual(
            final_manual,
            1,
            f"Expected 1 manual endpoint to be preserved, but found {final_manual}."
        )
        
        self.assertEqual(
            final_total,
            3,
            f"Expected 3 total endpoints (2 auto + 1 manual), but found {final_total}. "
            f"This indicates endpoint accumulation bug."
        )
        
        # Verify manual endpoint still exists
        self.assertTrue(
            Endpoint.objects.filter(id=manual_endpoint.id).exists(),
            "Manual endpoint should be preserved during re-upload"
        )
    
    def test_different_code_reupload_bug(self):
        """
        Test different code re-upload: Initial 3 endpoints → re-upload with 2 different endpoints → should show 2, not 5.
        
        CRITICAL: This test MUST FAIL on unfixed code (showing 5 endpoints instead of 2).
        """
        # Arrange - Initial upload with 3 endpoints
        upload1 = self._create_upload_instance()
        extractor1 = EndpointExtractor(upload1)
        
        initial_endpoints = [
            {'method': 'GET', 'path': '/api/old1', 'name': 'GET /api/old1', 'description': 'Old endpoint 1'},
            {'method': 'POST', 'path': '/api/old2', 'name': 'POST /api/old2', 'description': 'Old endpoint 2'},
            {'method': 'PUT', 'path': '/api/old3', 'name': 'PUT /api/old3', 'description': 'Old endpoint 3'}
        ]
        
        extractor1.extract_endpoint_details(initial_endpoints)
        self.assertEqual(self.project.endpoints.filter(auto_detected=True).count(), 3)
        
        # Act - Re-upload with different code having 2 different endpoints
        upload2 = self._create_upload_instance()
        extractor2 = EndpointExtractor(upload2)
        
        new_endpoints = [
            {'method': 'GET', 'path': '/api/new1', 'name': 'GET /api/new1', 'description': 'New endpoint 1'},
            {'method': 'DELETE', 'path': '/api/new2', 'name': 'DELETE /api/new2', 'description': 'New endpoint 2'}
        ]
        
        extractor2.extract_endpoint_details(new_endpoints)
        
        # Assert - Should show only 2 new endpoints, not 5 total (this will FAIL on unfixed code)
        final_count = self.project.endpoints.filter(auto_detected=True).count()
        self.assertEqual(
            final_count,
            2,
            f"Expected 2 endpoints after re-upload with different code, but found {final_count}. "
            f"This indicates endpoint accumulation bug - old endpoints not cleared."
        )
        
        # Verify the correct endpoints exist (new ones, not old ones)
        new_paths = [ep['path'] for ep in new_endpoints]
        existing_paths = list(self.project.endpoints.filter(auto_detected=True).values_list('url', flat=True))
        
        # Extract paths from URLs for comparison
        existing_paths_clean = []
        for url in existing_paths:
            if '/api/' in url:
                path = url.split('/api/', 1)[1]
                existing_paths_clean.append('/api/' + path.split('?')[0])  # Remove query params if any
        
        # On fixed code, should only have new endpoints
        # On unfixed code, will have both old and new endpoints (this assertion will fail)
        for new_path in new_paths:
            self.assertIn(
                new_path,
                [path for path in existing_paths_clean if new_path.split('/')[-1] in path],
                f"New endpoint {new_path} should exist after re-upload"
            )