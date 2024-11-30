import zipfile
import tarfile
import os
import tempfile
import logging
import errors


def unpack_archive(file_path, temp_dir):
    extracted_files = []

    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        elif file_path.endswith(('.tar', '.tar.gz', '.tgz')):
            with tarfile.open(file_path, 'r:*') as tar_ref:
                tar_ref.extractall(temp_dir)
        else:
            logging.error("Unsupported archive format.")
            raise errors.unable_to_process_file()

        # Collect the list of extracted files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Get the relative path from the temp_dir
                relative_path = os.path.relpath(file_path, temp_dir)
                temp_file = tempfile.TemporaryFile(dir=temp_dir)
                with open(file_path, "rb") as rf:
                    temp_file.write(rf.read())
                extracted_files.append((relative_path, temp_file))
    except (zipfile.BadZipFile, tarfile.ReadError):
        logging.error("The file is not a valid archive or is corrupted.")
        raise errors.unable_to_process_file()
    except PermissionError:
        logging.error("Permission denied to extract files.")
        raise errors.unable_to_process_file()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise errors.unable_to_process_file()

    return extracted_files
