class CheckApiPermissions:

    API_PERMISSIONS = {
        "/tool_master": ["com.platform.assetmanagement.asset.manage"],
        "/breakage_history": ["com.platform.assetmanagement.asset.manage"]
    }

    def __init__(self):
        self.api_permissons = self.API_PERMISSIONS

    def get_permissions(self, key):
        return self.api_permissons.get(key, [])


check_api_permissons = CheckApiPermissions()
