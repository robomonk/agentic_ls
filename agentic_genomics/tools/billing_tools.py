from google.adk.tools import BaseTool, tool_code

# In a real implementation, this would use the google-api-python-client
# to call the Cloud Billing Catalog API.
# from googleapiclient.discovery import build
# billing_service = build('cloudbilling', 'v1', credentials=credentials)
# request = billing_service.services().skus().list(parent=f"services/{service_id}")

HOURS_IN_MONTH_APPROX = 730.0 # Average hours in a month (365.25 days * 24 hours / 12 months)

MOCK_SKU_PRICES_USD_PER_HOUR = {
    "n2_standard_cpu": 0.033174,
    "n2_standard_ram_gb": 0.004446,
    "pd_standard_gb_per_month": 0.04,
}

class GetSkuPriceTool(BaseTool):
    """
    A tool to get the price of a specific Google Cloud SKU.
    """

    def _get_declaration(self):
        return tool_code(
            name="get_sku_price",
            description="Retrieves the price for a given Google Cloud billable SKU.",
            parameters={
                "sku_description": {
                    "type": "string",
                    "description": "A simplified description of the SKU, e.g., 'n2_standard_cpu', 'n2_standard_ram_gb', 'pd_standard_gb_per_month'.",
                }
            },
        )

    def _run(self, sku_description: str) -> dict:
        """
        Returns the price for a SKU. In a real implementation, this would query
        the Cloud Billing Catalog API.
        """
        price = MOCK_SKU_PRICES_USD_PER_HOUR.get(sku_description)
        if price is not None:
            # Monthly prices need to be converted to hourly for consistent calculation
            if "per_month" in sku_description:
                price = price / HOURS_IN_MONTH_APPROX
            return {"sku": sku_description, "price_usd_per_hour": price}
        else:
            return {"error": f"Price for SKU '{sku_description}' not found."}