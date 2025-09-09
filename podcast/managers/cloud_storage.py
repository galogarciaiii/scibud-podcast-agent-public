from typing import Optional

from podcast.services.google_auth import GoogleAuthService
from podcast.services.google_cloud import GoogleCloudService
from podcast.utilities.bundle import UtilitiesBundle


class CloudStorageManager:
    def __init__(self, path: str, utilities: UtilitiesBundle, key: Optional[str] = None) -> None:
        self.path: str = path
        self.utilities: UtilitiesBundle = utilities
        self.key: Optional[str] = key or self._get_api_key()
        if self.key:
            self.utilities.logger.info("Cloud API key set successfully.")
        else:
            self.utilities.logger.warning("Cloud API key was not set.")
        self.cloud_service: GoogleCloudService = GoogleCloudService(path=self.path, utilities=self.utilities)

    def _get_api_key(self) -> Optional[str]:
        auth_service: GoogleAuthService = GoogleAuthService(utilities=self.utilities)
        return auth_service.key

    def download_file(self, local_file_name: str, cloud_file_name: str) -> None:
        self.cloud_service.download_file(local_file_name, cloud_file_name)

    def upload_string_to_file(self, string_content: str, cloud_file_name: str) -> None:
        self.cloud_service.upload_string_to_file(string_content=string_content, cloud_file_name=cloud_file_name)

    def upload_file(self, local_file_name: str, cloud_file_name: str) -> None:
        self.cloud_service.upload_file(local_file_name, cloud_file_name)
