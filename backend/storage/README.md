# Storage App

Provides user-facing file manager with Folders and Files persisted in DB, backed by S3 via django-storages.

- Models: Folder, File
- Upload flow: POST /api/storage/files/presign-upload -> presigned POST + DB record
- Download: GET /api/storage/files/{id}/download -> public URL or signed URL (private)

Visibility
- Public files use PublicMediaStorage (public-read)
- Private files use PrivateMediaStorage (signed URLs)

Security
- Endpoints require authentication; extend with OpenFGA checks if you need cross-user sharing.