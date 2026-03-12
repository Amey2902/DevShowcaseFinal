from django.test import TestCase
from django.contrib.auth.models import User
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from projects.models import Project, ProjectUpload, Endpoint
from projects.services.endpoint_extractor import EndpointExtractor


# Property-based test generators for preservation scenarios
@st.composite
def first_time_upload_scenarios(draw):
    """Generate first-time upload scenarios (no existing endpoints)."""
    # Generate 1-5 endpoints for first-time upload
    num_endpoints = draw(st.integers(min_value=1, max_value=5))
    
    endpoints = []
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    for i in range(num_endpoints):
        method = draw(st.sampled_from(methods))
        path = f"/api/resource{i}"
        name = f"{method} {path}"
        
        endpoint_data = {
            'method': method,
            'path': path,
            'name': name,
            'description': f'First-time endpoint {i}',
            'file': f'src/routes/resource{i}.py',
            'line': draw(st.integers(min_value=1, max_value=200)),
            'path_parameters': [],
            'query_parameters': [],
            'auth_required': draw(st.booleans()),
            'auth_type': draw(st.sampled_from(['', 'Bearer', 'Basic', 'API-Key'])),
            'request_schema': {},
            'response_schema': {}
        }
        
        endpoints.append(endpoint_data)
    
    return endpoints


@st.composite
def manual_endpoint_scenarios(draw):
    """Generate scenarios with only manual endpoints (no auto-detected ones)."""
    # Generate 1-3 manual endpoints
    num_manual = draw(st.integers(min_value=1, max_value=3))
    
    manual_endpoints = []
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    for i in range(num_manual):
        method = draw(st.sampled_from(methods))
        url = f"http://example.com/manual{i}"
        name = f"Manual {method} {i}"
        
        manual_endpoint = {
            'name': name,
            'method': method,
            'url': url,
            'description': f'Manually created endpoint {i}',
            'auto_detected': False
        }
        
        manual_endpoints.append(manual_endpoint)
    
    # Generate new endpoints to upload
    new_endpoints = draw(first_time_upload_scenarios())
    
    return {
        'manual_endpoints': manual_endpoints,
        'new_endpoints': new_endpoints
    }


@st.composite
def different_project_scenarios(draw):
    """Generate scenarios with multiple different projects."""
    # Generate endpoints for project 1
    project1_endpoints = draw(first_time_upload_scenarios())
    
    # Generate endpoints for project 2
    project2_endpoints = draw(first_time_upload_scenarios())
    
    return {
        'project1_endpoints': project1_endpoints,
        'project2_endpoints': project2_endpoints
    }


@st.composite
def session_deduplication_scenarios(draw):
    """Generate scenarios to test within-session deduplication."""
    # Generate base endpoints
    base_endpoints = draw(first_time_upload_scenarios())
    
    # Create duplicates within the same session
    duplicated_endpoints = base_endpoints.copy()
    
    # Add some of the same endpoints again (simulating duplicates in AI analysis)
    if len(base_endpoints) > 1:
        num_duplicates = draw(st.integers(min_value=1, max_value=len(base_endpoints)))
        for i in range(num_duplicates):
            duplicated_endpoints.append(base_endpoints[i].copy())
    
    return {
        'endpoints_with_duplicates': duplicated_endpoints,
        'expected_unique_count': len(base_endpoints)
    }


class TestEndpointExtractorPreservation(HypothesisTestCase):
    """
    **Property 2: Preservation** - First-upload and Manual Endpoint Behavior
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    
    IMPORTANT: Follow observation-first methodology.
    These tests observe behavior on UNFIXED code for non-buggy inputs and should PASS.
    This confirms baseline behavior to preserve during the fix.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        self.user = User.objects.create_user(username=username, email=f'{username}@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            title=f'Test Project {uuid.uuid4().hex[:8]}',
            short_description='Test project for preservation testing'
        )
    
    def _create_upload_instance(self, project=None):
        """Helper to create a ProjectUpload instance."""
        if project is None:
            project = self.project
            
        return ProjectUpload.objects.create(
            project=project,
            user=self.user,
            upload_method='files',
            status='analyzing'
        )
    
    def _create_manual_endpoint(self, project, endpoint_data):
        """Helper to create a manual endpoint."""
        return Endpoint.objects.create(
            project=project,
            name=endpoint_data['name'],
            method=endpoint_data['method'],
            url=endpoint_data['url'],
            description=endpoint_data['description'],
            auto_detected=endpoint_data['auto_detected']
        )
    
    @given(endpoints_data=first_time_upload_scenarios())
    @settings(max_examples=10, deadline=5000)
    def test_preservation_first_time_uploads_detect_normally(self, endpoints_data):
        """
        **Requirement 3.1**: First-time uploads detect and save endpoints normally.
        
        For any first-time project upload (no existing endpoints), the system SHALL 
        continue to detect and save endpoints exactly as before the fix.
        
        This test should PASS on unfixed code, confirming baseline behavior.
        """
        # Arrange - Clean project with no existing endpoints
        self.assertEqual(self.project.endpoints.count(), 0, "Project should start with no endpoints")
        
        upload = self._create_upload_instance()
        extractor = EndpointExtractor(upload)
        
        # Act - First-time upload
        saved_count = extractor.extract_endpoint_details(endpoints_data)
        
        # Assert - Baseline behavior should work correctly
        expected_count = len(endpoints_data)
        
        # Verify correct number of endpoints saved
        self.assertEqual(
            saved_count, 
            expected_count,
            f"Expected {expected_count} endpoints to be saved, but got {saved_count}"
        )
        
        # Verify endpoints exist in database
        actual_count = self.project.endpoints.filter(auto_detected=True).count()
        self.assertEqual(
            actual_count,
            expected_count,
            f"Expected {expected_count} auto-detected endpoints in database, but found {actual_count}"
        )
        
        # Verify no manual endpoints were created
        manual_count = self.project.endpoints.filter(auto_detected=False).count()
        self.assertEqual(
            manual_count,
            0,
            "No manual endpoints should exist after first-time upload"
        )
        
        # Verify total count matches
        total_count = self.project.endpoints.count()
        self.assertEqual(
            total_count,
            expected_count,
            f"Total endpoint count should be {expected_count}, but found {total_count}"
        )
    
    @given(scenario=manual_endpoint_scenarios())
    @settings(max_examples=10, deadline=5000)
    def test_preservation_manual_endpoints_during_operations(self, scenario):
        """
        **Requirement 3.2**: Manual endpoints preserved during re-upload operations.
        
        For any project with existing manual endpoints, when new auto-detected endpoints 
        are added, the system SHALL continue to preserve all manually created endpoints.
        
        This test should PASS on unfixed code, confirming baseline behavior.
        """
        # Arrange - Create manual endpoints first
        manual_endpoints_data = scenario['manual_endpoints']
        new_endpoints_data = scenario['new_endpoints']
        
        manual_endpoints = []
        for manual_data in manual_endpoints_data:
            manual_endpoint = self._create_manual_endpoint(self.project, manual_data)
            manual_endpoints.append(manual_endpoint)
        
        initial_manual_count = len(manual_endpoints)
        self.assertEqual(
            self.project.endpoints.filter(auto_detected=False).count(),
            initial_manual_count,
            f"Should have {initial_manual_count} manual endpoints initially"
        )
        
        # Act - Upload new auto-detected endpoints
        upload = self._create_upload_instance()
        extractor = EndpointExtractor(upload)
        
        saved_count = extractor.extract_endpoint_details(new_endpoints_data)
        
        # Assert - Manual endpoints should be preserved
        final_manual_count = self.project.endpoints.filter(auto_detected=False).count()
        self.assertEqual(
            final_manual_count,
            initial_manual_count,
            f"Manual endpoints should be preserved. Expected {initial_manual_count}, found {final_manual_count}"
        )
        
        # Verify all original manual endpoints still exist
        for manual_endpoint in manual_endpoints:
            self.assertTrue(
                Endpoint.objects.filter(id=manual_endpoint.id).exists(),
                f"Manual endpoint {manual_endpoint.name} should still exist"
            )
        
        # Verify new auto-detected endpoints were added
        auto_count = self.project.endpoints.filter(auto_detected=True).count()
        expected_auto_count = len(new_endpoints_data)
        self.assertEqual(
            auto_count,
            expected_auto_count,
            f"Expected {expected_auto_count} auto-detected endpoints, found {auto_count}"
        )
        
        # Verify total count is correct
        total_count = self.project.endpoints.count()
        expected_total = initial_manual_count + expected_auto_count
        self.assertEqual(
            total_count,
            expected_total,
            f"Total endpoints should be {expected_total} (manual + auto), found {total_count}"
        )
    
    @given(scenario=different_project_scenarios())
    @settings(max_examples=8, deadline=5000)
    def test_preservation_different_projects_separate_collections(self, scenario):
        """
        **Requirement 3.4**: Different projects maintain separate endpoint collections.
        
        For any uploads to different projects, the system SHALL continue to maintain 
        completely separate endpoint collections for each project.
        
        This test should PASS on unfixed code, confirming baseline behavior.
        """
        # Arrange - Create second project
        project2 = Project.objects.create(
            owner=self.user,
            title='Test Project 2',
            short_description='Second test project'
        )
        
        project1_endpoints = scenario['project1_endpoints']
        project2_endpoints = scenario['project2_endpoints']
        
        # Act - Upload endpoints to project 1
        upload1 = self._create_upload_instance(self.project)
        extractor1 = EndpointExtractor(upload1)
        count1 = extractor1.extract_endpoint_details(project1_endpoints)
        
        # Act - Upload endpoints to project 2
        upload2 = self._create_upload_instance(project2)
        extractor2 = EndpointExtractor(upload2)
        count2 = extractor2.extract_endpoint_details(project2_endpoints)
        
        # Assert - Projects should have separate endpoint collections
        project1_count = self.project.endpoints.count()
        project2_count = project2.endpoints.count()
        
        expected_project1_count = len(project1_endpoints)
        expected_project2_count = len(project2_endpoints)
        
        self.assertEqual(
            project1_count,
            expected_project1_count,
            f"Project 1 should have {expected_project1_count} endpoints, found {project1_count}"
        )
        
        self.assertEqual(
            project2_count,
            expected_project2_count,
            f"Project 2 should have {expected_project2_count} endpoints, found {project2_count}"
        )
        
        # Verify no cross-contamination between projects
        project1_endpoint_ids = set(self.project.endpoints.values_list('id', flat=True))
        project2_endpoint_ids = set(project2.endpoints.values_list('id', flat=True))
        
        self.assertEqual(
            len(project1_endpoint_ids.intersection(project2_endpoint_ids)),
            0,
            "Projects should not share any endpoint records"
        )
        
        # Verify total endpoints across both projects
        total_endpoints = Endpoint.objects.filter(
            project__in=[self.project, project2]
        ).count()
        expected_total = expected_project1_count + expected_project2_count
        
        self.assertEqual(
            total_endpoints,
            expected_total,
            f"Total endpoints across both projects should be {expected_total}, found {total_endpoints}"
        )
    
    @given(scenario=session_deduplication_scenarios())
    @settings(max_examples=10, deadline=5000)
    def test_preservation_session_deduplication_works(self, scenario):
        """
        **Requirement 3.3**: Within-session endpoint deduplication continues working.
        
        For any upload session containing duplicate endpoints, the system SHALL continue 
        to deduplicate endpoints within that session as before the fix.
        
        This test should PASS on unfixed code, confirming baseline behavior.
        """
        # Arrange - Endpoints with duplicates within the same session
        endpoints_with_duplicates = scenario['endpoints_with_duplicates']
        expected_unique_count = scenario['expected_unique_count']
        
        upload = self._create_upload_instance()
        extractor = EndpointExtractor(upload)
        
        # Act - Upload endpoints with duplicates
        saved_count = extractor.extract_endpoint_details(endpoints_with_duplicates)
        
        # Assert - Deduplication should work within session
        self.assertEqual(
            saved_count,
            expected_unique_count,
            f"Expected {expected_unique_count} unique endpoints after deduplication, "
            f"but {saved_count} were saved from {len(endpoints_with_duplicates)} input endpoints"
        )
        
        # Verify database contains only unique endpoints
        actual_count = self.project.endpoints.filter(auto_detected=True).count()
        self.assertEqual(
            actual_count,
            expected_unique_count,
            f"Database should contain {expected_unique_count} unique endpoints, found {actual_count}"
        )
        
        # Verify no duplicate method+path combinations exist
        endpoints = self.project.endpoints.filter(auto_detected=True)
        method_path_combinations = set()
        
        for endpoint in endpoints:
            # Extract path from URL for comparison
            url = endpoint.url
            if '/api/' in url:
                # Extract the path part after the domain
                path_part = url.split('/api/', 1)[1].split('?')[0]
                path = '/api/' + path_part
            else:
                # Fallback for other URL formats
                from urllib.parse import urlparse
                parsed = urlparse(url)
                path = parsed.path or '/'
            
            combination = f"{endpoint.method}:{path}"
            
            self.assertNotIn(
                combination,
                method_path_combinations,
                f"Duplicate method+path combination found: {combination}"
            )
            
            method_path_combinations.add(combination)
        
        # Verify the count matches our tracking
        self.assertEqual(
            len(method_path_combinations),
            expected_unique_count,
            f"Expected {expected_unique_count} unique method+path combinations, "
            f"found {len(method_path_combinations)}"
        )


class TestEndpointExtractorPreservationUnits(TestCase):
    """Unit tests for specific preservation scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        import uuid
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        self.user = User.objects.create_user(username=username, email=f'{username}@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            title=f'Test Project {uuid.uuid4().hex[:8]}',
            short_description='Test project for preservation testing'
        )
    
    def _create_upload_instance(self):
        """Helper to create a ProjectUpload instance."""
        return ProjectUpload.objects.create(
            project=self.project,
            user=self.user,
            upload_method='files',
            status='analyzing'
        )
    
    def test_first_time_upload_baseline_behavior(self):
        """
        Test that first-time uploads work correctly (baseline behavior).
        
        This should PASS on unfixed code, confirming the behavior to preserve.
        """
        # Arrange - Clean project
        self.assertEqual(self.project.endpoints.count(), 0)
        
        upload = self._create_upload_instance()
        extractor = EndpointExtractor(upload)
        
        endpoints_data = [
            {'method': 'GET', 'path': '/api/users', 'name': 'GET /api/users', 'description': 'Get users'},
            {'method': 'POST', 'path': '/api/users', 'name': 'POST /api/users', 'description': 'Create user'},
            {'method': 'GET', 'path': '/api/posts', 'name': 'GET /api/posts', 'description': 'Get posts'}
        ]
        
        # Act
        saved_count = extractor.extract_endpoint_details(endpoints_data)
        
        # Assert - Should work normally
        self.assertEqual(saved_count, 3)
        self.assertEqual(self.project.endpoints.filter(auto_detected=True).count(), 3)
        self.assertEqual(self.project.endpoints.count(), 3)
    
    def test_manual_endpoint_preservation_baseline(self):
        """
        Test that manual endpoints are preserved when adding auto-detected ones.
        
        This should PASS on unfixed code, confirming the behavior to preserve.
        """
        # Arrange - Create manual endpoint
        manual_endpoint = Endpoint.objects.create(
            project=self.project,
            name="Manual API",
            method="PUT",
            url="http://example.com/manual",
            description="Manually created endpoint",
            auto_detected=False
        )
        
        self.assertEqual(self.project.endpoints.filter(auto_detected=False).count(), 1)
        
        # Act - Add auto-detected endpoints
        upload = self._create_upload_instance()
        extractor = EndpointExtractor(upload)
        
        endpoints_data = [
            {'method': 'GET', 'path': '/api/data', 'name': 'GET /api/data', 'description': 'Get data'}
        ]
        
        saved_count = extractor.extract_endpoint_details(endpoints_data)
        
        # Assert - Manual endpoint should be preserved
        self.assertEqual(saved_count, 1)
        self.assertEqual(self.project.endpoints.filter(auto_detected=True).count(), 1)
        self.assertEqual(self.project.endpoints.filter(auto_detected=False).count(), 1)
        self.assertEqual(self.project.endpoints.count(), 2)
        
        # Verify manual endpoint still exists
        self.assertTrue(Endpoint.objects.filter(id=manual_endpoint.id).exists())
    
    def test_different_projects_isolation_baseline(self):
        """
        Test that different projects maintain separate endpoint collections.
        
        This should PASS on unfixed code, confirming the behavior to preserve.
        """
        # Arrange - Create second project
        project2 = Project.objects.create(
            owner=self.user,
            title='Test Project 2',
            short_description='Second test project'
        )
        
        # Act - Upload to project 1
        upload1 = self._create_upload_instance()
        extractor1 = EndpointExtractor(upload1)
        
        endpoints1 = [
            {'method': 'GET', 'path': '/api/project1', 'name': 'GET /api/project1', 'description': 'Project 1 endpoint'}
        ]
        
        count1 = extractor1.extract_endpoint_details(endpoints1)
        
        # Act - Upload to project 2
        upload2 = ProjectUpload.objects.create(
            project=project2,
            user=self.user,
            upload_method='files',
            status='analyzing'
        )
        extractor2 = EndpointExtractor(upload2)
        
        endpoints2 = [
            {'method': 'POST', 'path': '/api/project2', 'name': 'POST /api/project2', 'description': 'Project 2 endpoint'}
        ]
        
        count2 = extractor2.extract_endpoint_details(endpoints2)
        
        # Assert - Projects should be isolated
        self.assertEqual(count1, 1)
        self.assertEqual(count2, 1)
        self.assertEqual(self.project.endpoints.count(), 1)
        self.assertEqual(project2.endpoints.count(), 1)
        
        # Verify no cross-contamination
        project1_endpoints = list(self.project.endpoints.values_list('id', flat=True))
        project2_endpoints = list(project2.endpoints.values_list('id', flat=True))
        
        self.assertEqual(len(set(project1_endpoints).intersection(set(project2_endpoints))), 0)
    
    def test_session_deduplication_baseline(self):
        """
        Test that within-session deduplication works correctly.
        
        This should PASS on unfixed code, confirming the behavior to preserve.
        """
        # Arrange - Endpoints with duplicates
        upload = self._create_upload_instance()
        extractor = EndpointExtractor(upload)
        
        endpoints_with_duplicates = [
            {'method': 'GET', 'path': '/api/users', 'name': 'GET /api/users', 'description': 'Get users'},
            {'method': 'POST', 'path': '/api/users', 'name': 'POST /api/users', 'description': 'Create user'},
            {'method': 'GET', 'path': '/api/users', 'name': 'GET /api/users', 'description': 'Get users'},  # Duplicate
        ]
        
        # Act
        saved_count = extractor.extract_endpoint_details(endpoints_with_duplicates)
        
        # Assert - Should deduplicate within session
        self.assertEqual(saved_count, 2, "Should save only 2 unique endpoints, not 3")
        self.assertEqual(self.project.endpoints.count(), 2)
        
        # Verify unique method+path combinations
        endpoints = self.project.endpoints.all()
        method_path_combinations = set()
        
        for endpoint in endpoints:
            # Extract path from URL - the EndpointExtractor creates full URLs
            url = endpoint.url
            if '/api/' in url:
                # Extract the path part after the domain
                path_part = url.split('/api/', 1)[1].split('?')[0]
                path = '/api/' + path_part
            else:
                # Fallback for other URL formats
                from urllib.parse import urlparse
                parsed = urlparse(url)
                path = parsed.path or '/'
            
            combination = f"{endpoint.method}:{path}"
            method_path_combinations.add(combination)
        
        expected_combinations = {'GET:/api/users', 'POST:/api/users'}
        self.assertEqual(method_path_combinations, expected_combinations)