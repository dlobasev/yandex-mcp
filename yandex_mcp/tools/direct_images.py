"""Yandex Direct ad image management tools."""

import json

from yandex_mcp.client import api_client
from yandex_mcp.enums import ResponseFormat
from yandex_mcp.errors import handle_api_error
from yandex_mcp.formatters import format_images_markdown
from yandex_mcp.models.direct import DeleteImagesInput, GetImagesInput, UploadImageInput
from yandex_mcp.server import mcp


@mcp.tool(
    name="direct_upload_image",
    annotations={
        "title": "Upload Yandex Direct Ad Image",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_upload_image(params: UploadImageInput) -> str:
    """Upload an ad image to Yandex Direct.

    Uploads a base64-encoded image. Returns the AdImageHash which can be used
    when creating text ads (ad_image_hash parameter in direct_create_text_ad).

    Supported formats: JPG, PNG, GIF.

    Image requirements by type:
    - REGULAR: aspect ratio 1:1 to 3:4, 450-5000px per side, max 10 MB
    - WIDE: aspect ratio 16:9, minimum 1080x607px, max 10 MB
    - FIXED_IMAGE: exact sizes for banner ad formats, max 512 KB

    Args:
        params: Image data, name, and type

    Returns:
        Image hash on success
    """
    try:
        ad_image: dict = {
            "ImageData": params.image_data,
            "Name": params.name,
            "Type": params.image_type.value,
        }

        request_params = {"AdImages": [ad_image]}

        result = await api_client.direct_request("adimages", "add", request_params)
        add_results = result.get("result", {}).get("AddResults", [])

        if add_results and add_results[0].get("AdImageHash"):
            image_hash = add_results[0]["AdImageHash"]
            return (
                f"Image uploaded successfully.\n"
                f"- **Hash**: {image_hash}\n"
                f"- **Name**: {params.name}\n"
                f"- **Type**: {params.image_type.value}\n\n"
                "Use this hash in direct_create_text_ad (ad_image_hash parameter)."
            )

        errors: list[str] = []
        for r in add_results:
            if r.get("Errors"):
                errors.extend([e.get("Message", "Unknown error") for e in r["Errors"]])

        return "Failed to upload image:\n" + "\n".join(f"- {e}" for e in errors)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_get_images",
    annotations={
        "title": "Get Yandex Direct Ad Images",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def direct_get_images(params: GetImagesInput) -> str:
    """Get ad image metadata from Yandex Direct.

    Retrieves images with their hashes, names, types, and preview URLs.
    Can filter by specific hashes or association status.

    Args:
        params: Filter and pagination parameters

    Returns:
        Images list in markdown or JSON format
    """
    try:
        selection_criteria: dict = {}

        if params.ad_image_hashes:
            selection_criteria["AdImageHashes"] = params.ad_image_hashes
        if params.associated is not None:
            selection_criteria["Associated"] = params.associated.value

        request_params = {
            "SelectionCriteria": selection_criteria,
            "FieldNames": [
                "AdImageHash", "Name", "Type", "Subtype",
                "OriginalUrl", "PreviewUrl", "Associated",
            ],
            "Page": {"Limit": params.limit, "Offset": params.offset},
        }

        result = await api_client.direct_request("adimages", "get", request_params)
        images = result.get("result", {}).get("AdImages", [])

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"images": images, "total": len(images)},
                indent=2,
                ensure_ascii=False,
            )

        return format_images_markdown(images)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="direct_delete_images",
    annotations={
        "title": "Delete Yandex Direct Ad Images",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def direct_delete_images(params: DeleteImagesInput) -> str:
    """Delete ad images from Yandex Direct.

    Images that are attached to ads cannot be deleted.
    Detach the image from the ad first, then delete.

    Args:
        params: Image hashes to delete

    Returns:
        Operation result
    """
    try:
        request_params = {
            "SelectionCriteria": {"AdImageHashes": params.ad_image_hashes},
        }

        result = await api_client.direct_request("adimages", "delete", request_params)
        delete_results = result.get("result", {}).get("DeleteResults", [])

        success_count = sum(
            1 for r in delete_results
            if r.get("AdImageHash") and not r.get("Errors")
        )
        errors: list[str] = []
        for r in delete_results:
            if r.get("Errors"):
                errors.extend(
                    f"Hash {r.get('AdImageHash', '?')}: {e.get('Message', 'Unknown error')}"
                    for e in r["Errors"]
                )

        response = f"Successfully deleted {success_count} image(s)."
        if errors:
            response += "\n\nErrors:\n" + "\n".join(f"- {e}" for e in errors)

        return response

    except Exception as e:
        return handle_api_error(e)