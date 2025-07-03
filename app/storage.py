from cloudinary_storage.storage import MediaCloudinaryStorage

class RawMediaCloudinaryStorage(MediaCloudinaryStorage):
    def get_options(self, name, content):
        options = super().get_options(name, content)
        options['resource_type'] = 'raw'  # ✅ Force raw upload
        return options

