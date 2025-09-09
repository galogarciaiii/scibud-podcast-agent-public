import hashlib
import os

from google.cloud import storage  # type: ignore

from podcast.utilities.bundle import UtilitiesBundle


class GoogleCloudService:
    """
    A service class for interacting with Google Cloud Storage. This class
    allows uploading and downloading files, with the ability to check MD5 hashes
    to ensure the integrity of the files. It uses the strategy pattern to handle
    bucket configurations.
    """

    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        """
        Initializes the GoogleCloudService.

        :param strategy: A strategy object that provides information about the bucket
                         and base path for the Google Cloud Storage operations.
        :param logger: A logger for logging information and errors.
        """
        self.path: str = path
        self.utilities: UtilitiesBundle = utilities
        self.storage_client: storage.Client = storage.Client()
        self.bucket_name: str = self.utilities.config["general_info"]["bucket_name"]
        bucket: storage.Bucket = self.storage_client.bucket(self.bucket_name)
        self.bucket: storage.Bucket = bucket

    def calculate_md5(self, file_path: str) -> str:
        """
        Calculate the MD5 hash of a local file.

        :param file_path: The path of the file to calculate the MD5 for.
        :return: The MD5 hash as a hexadecimal string.
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # Read the file in chunks to avoid memory overload with large files
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def download_file(self, local_file_name: str, cloud_file_name: str) -> None:
        """
        Download a file from Google Cloud Storage to a local path, comparing MD5 hashes
        to avoid unnecessary downloads if the file is already up-to-date.

        :param local_file_name: The local name to save the file as.
        :param cloud_file_name: The name of the file in Google Cloud Storage.
        :raises Exception: If the download process fails.
        """
        try:
            blob: storage.Blob = self.bucket.blob(self.path + cloud_file_name)

            # Refreshes the blob's metadata to get the latest MD5 hash from the cloud.
            blob.reload()
            cloud_md5 = blob.md5_hash

            # Determine the full local file path and check if it exists.
            local_file_path = os.path.join(self.path, local_file_name)
            if os.path.exists(local_file_path):
                # Calculate the MD5 hash of the local file for comparison.
                local_md5 = self.calculate_md5(local_file_path)
                if local_md5 == cloud_md5:
                    self.utilities.logger.debug(f"Local file '{local_file_name}' is already up to date.")
                    return

            # If the file does not exist or hashes differ, download the file.
            blob.download_to_filename(local_file_path)
            self.utilities.logger.debug("File downloaded successfully to %s", local_file_name)

        except Exception as e:
            self.utilities.logger.error(f"Failed to download the file: {str(e)}")
            raise

    def upload_file(self, local_file_name: str, cloud_file_name: str) -> None:
        """
        Upload a local file to Google Cloud Storage with cache control set to
        avoid serving cached versions of the file.

        :param local_file_name: The local file to upload.
        :param cloud_file_name: The destination path in Google Cloud Storage.
        :raises Exception: If the upload process fails.
        """
        try:
            blob: storage.Blob = self.bucket.blob(self.path + cloud_file_name)

            # Set cache control metadata to prevent cached versions from being served.
            blob.cache_control = "no-cache"

            # Upload the file to the specified cloud path.
            blob.upload_from_filename(self.path + local_file_name)
            self.utilities.logger.info("File uploaded successfully.")
        except Exception as e:
            self.utilities.logger.error(f"Failed to upload the file: {e}")
            raise

    def upload_string_to_file(self, string_content: str, cloud_file_name: str) -> None:
        """
        Upload string content as a file to Google Cloud Storage, with cache control
        to avoid serving cached versions. After upload, the file's MD5 hash is refreshed.

        :param string_content: The string content to be uploaded as a file.
        :param cloud_file_name: The destination path in Google Cloud Storage.
        :raises Exception: If the upload process fails.
        """
        try:
            blob: storage.Blob = self.bucket.blob(self.path + cloud_file_name)

            # Set cache control to avoid cached downloads of this file.
            blob.cache_control = "no-cache"

            # Upload the string content as a file.
            blob.upload_from_string(string_content)

            # Refresh blob metadata after upload to get the latest MD5 hash.
            blob.reload()
            self.utilities.logger.debug(
                f"String uploaded successfully to file on Google Cloud Storage. MD5 hash: {blob.md5_hash}"
            )

        except Exception as e:
            self.utilities.logger.error(f"An error occurred during the content upload: {e}")
            raise Exception(f"Failed to upload content to cloud storage: {e}")
