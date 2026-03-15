from projects.models import Endpoint


class EndpointExtractor:
    """Service for extracting and saving endpoint details to database."""
    
    def __init__(self, upload_instance, base_url=None):
        """Initialize with a ProjectUpload instance."""
        self.upload = upload_instance
        self.project = upload_instance.project
        self.base_url = base_url or 'https://your-api-domain.com'
    
    def extract_endpoint_details(self, endpoints_data):
        """
        Extract endpoint details from AI analysis and save to database.

        Args:
            endpoints_data: List of endpoint dictionaries from AI

        Returns:
            int: Number of endpoints saved
        """
        from django.db import transaction
        import logging

        logger = logging.getLogger(__name__)

        self.upload.status = 'extracting_endpoints'
        self.upload.current_message = 'Saving detected endpoints...'
        self.upload.progress_percentage = 80
        self.upload.save()

        saved_count = 0
        seen_endpoints = set()  # Track unique endpoints by method + path

        try:
            with transaction.atomic():
                # Pre-cleanup logic: Delete existing auto-detected endpoints for this project
                existing_auto_detected = self.project.endpoints.filter(auto_detected=True)
                deleted_count = existing_auto_detected.count()

                if deleted_count > 0:
                    existing_auto_detected.delete()
                    logger.debug(f"Deleted {deleted_count} existing auto-detected endpoints for project {self.project.id}")
                    print(f"Pre-cleanup: Deleted {deleted_count} existing auto-detected endpoints")
                else:
                    logger.debug(f"No existing auto-detected endpoints found for project {self.project.id}")
                    print("Pre-cleanup: No existing auto-detected endpoints to delete")

                # Process new endpoints
                for endpoint_data in endpoints_data:
                    try:
                        # Extract data with defaults
                        method = endpoint_data.get('method', 'GET').upper()
                        path = endpoint_data.get('path', '')
                        name = endpoint_data.get('name', f"{method} {path}")

                        # Handle both full URLs and relative paths
                        if path.startswith('http://') or path.startswith('https://'):
                            # Path is already a full URL, use it as-is
                            full_url = path
                            # Extract just the path part for the unique key
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(path)
                                path_only = parsed.path or '/'
                            except:
                                path_only = path
                        else:
                            # Path is relative, construct full URL
                            full_url = f"{self.base_url}{path}" if path.startswith('/') else f"{self.base_url}/{path}"
                            path_only = path

                        # Create unique key to detect duplicates
                        unique_key = f"{method}:{path_only}"

                        # Skip if we've already saved this endpoint
                        if unique_key in seen_endpoints:
                            print(f"Skipping duplicate endpoint: {unique_key}")
                            continue

                        seen_endpoints.add(unique_key)

                        # Create endpoint
                        endpoint = Endpoint.objects.create(
                            project=self.project,
                            name=name,
                            method=method,
                            url=full_url,
                            description=endpoint_data.get('description', ''),
                            # Auto-detection fields
                            detected_from_file=endpoint_data.get('file', ''),
                            detected_at_line=endpoint_data.get('line'),
                            path_parameters=endpoint_data.get('path_parameters', []),
                            query_parameters=endpoint_data.get('query_parameters', []),
                            auth_required=endpoint_data.get('auth_required', False),
                            auth_type=endpoint_data.get('auth_type', ''),
                            request_schema=endpoint_data.get('request_schema', {}),
                            response_schema=endpoint_data.get('response_schema', {}),
                            auto_detected=True,
                            # AST Security Analysis fields
                            ast_security_level=endpoint_data.get('ast_security_level', ''),
                            ast_confidence_score=endpoint_data.get('ast_confidence_score'),
                            detected_decorators=endpoint_data.get('detected_decorators', []),
                            security_features=endpoint_data.get('security_features', []),
                            ast_reasoning=endpoint_data.get('ast_reasoning', ''),
                        )

                        saved_count += 1

                    except Exception as e:
                        # Log error but continue with other endpoints
                        logger.error(f"Error saving individual endpoint: {e}")
                        print(f"Error saving endpoint: {e}")
                        continue

                logger.debug(f"Created {saved_count} new auto-detected endpoints for project {self.project.id}")
                print(f"Created {saved_count} new auto-detected endpoints")

        except Exception as e:
            # Handle cleanup/transaction errors
            logger.error(f"Error during endpoint cleanup and creation: {e}")
            print(f"Error during endpoint processing: {e}")
            # Re-raise to ensure upload fails if critical error occurs
            raise

        self.upload.endpoints_found = saved_count
        self.upload.progress_percentage = 90
        self.upload.current_message = f'Saved {saved_count} endpoints'
        self.upload.save()

        return saved_count

