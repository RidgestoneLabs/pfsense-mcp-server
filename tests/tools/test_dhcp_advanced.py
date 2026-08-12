"""Unit tests for DHCP advanced tools (src/tools/dhcp_advanced.py)."""

from src.tools.dhcp_advanced import (
    create_dhcp_custom_option,
    delete_dhcp_address_pool,
    delete_dhcp_custom_option,
    update_dhcp_address_pool,
    update_dhcp_custom_option,
)

_create_dhcp_custom_option = create_dhcp_custom_option
_update_dhcp_custom_option = update_dhcp_custom_option
_delete_dhcp_custom_option = delete_dhcp_custom_option
_update_dhcp_address_pool = update_dhcp_address_pool
_delete_dhcp_address_pool = delete_dhcp_address_pool


def _sent_data(mock_make_request):
    """Payload of the most recent _make_request call."""
    call = mock_make_request.call_args
    return call.kwargs.get("data") or call[1].get("data")


# ---------------------------------------------------------------------------
# custom options: parent_id is required on every write, the endpoint 500s
# with MODEL_CANNOT_GET_CONFIG_PATH_WITHOUT_PARENT_MODEL without it
# ---------------------------------------------------------------------------

class TestCreateDhcpCustomOption:
    async def test_sends_parent_id(self, mock_client, mock_make_request):
        mock_make_request.return_value = {"data": {"id": 0}}
        result = await _create_dhcp_custom_option(
            parent_id="opt16", number=43, type="string", value="01:04:0a:09:fe:15"
        )
        assert result["success"] is True
        data = _sent_data(mock_make_request)
        assert data["parent_id"] == "opt16"
        assert data["number"] == 43


class TestUpdateDhcpCustomOption:
    async def test_sends_parent_id_and_id(self, mock_client, mock_make_request):
        mock_make_request.return_value = {"data": {"id": 0}}
        result = await _update_dhcp_custom_option(
            parent_id="opt16", option_id=0, value="01:04:0a:0a:fe:15"
        )
        assert result["success"] is True
        assert result["parent_id"] == "opt16"
        data = _sent_data(mock_make_request)
        assert data["parent_id"] == "opt16"
        assert data["id"] == 0
        assert data["value"] == "01:04:0a:0a:fe:15"

    async def test_parent_id_is_not_a_field_update(self, mock_client, mock_make_request):
        """parent_id addresses the object, so it must not count as a changed field."""
        mock_make_request.return_value = {"data": {}}
        result = await _update_dhcp_custom_option(parent_id="opt16", option_id=0, number=43)
        assert result["fields_updated"] == ["number"]

    async def test_requires_at_least_one_field(self, mock_client, mock_make_request):
        result = await _update_dhcp_custom_option(parent_id="opt16", option_id=0)
        assert result["success"] is False
        assert "No fields to update" in result["error"]
        mock_make_request.assert_not_called()

    async def test_error(self, mock_client, mock_make_request):
        mock_make_request.side_effect = Exception("update failed")
        result = await _update_dhcp_custom_option(parent_id="opt16", option_id=0, number=43)
        assert result["success"] is False
        assert "update failed" in result["error"]


class TestDeleteDhcpCustomOption:
    async def test_sends_parent_id_and_id(self, mock_client, mock_make_request):
        mock_make_request.return_value = {"data": {}}
        result = await _delete_dhcp_custom_option(parent_id="opt16", option_id=0, confirm=True)
        assert result["success"] is True
        assert result["parent_id"] == "opt16"
        assert "note" in result  # ID shift warning
        data = _sent_data(mock_make_request)
        assert data["parent_id"] == "opt16"
        assert data["id"] == 0

    async def test_confirm_required(self, mock_client, mock_make_request):
        result = await _delete_dhcp_custom_option(parent_id="opt16", option_id=0)
        assert result["success"] is False
        assert "confirm" in result["error"].lower()

    async def test_error(self, mock_client, mock_make_request):
        mock_make_request.side_effect = Exception("delete failed")
        result = await _delete_dhcp_custom_option(parent_id="opt16", option_id=0, confirm=True)
        assert result["success"] is False
        assert "delete failed" in result["error"]


# ---------------------------------------------------------------------------
# address pools: same nested-model requirement as custom options
# ---------------------------------------------------------------------------

class TestUpdateDhcpAddressPool:
    async def test_sends_parent_id_and_id(self, mock_client, mock_make_request):
        mock_make_request.return_value = {"data": {"id": 1}}
        result = await _update_dhcp_address_pool(
            parent_id="lan", pool_id=1, range_from="192.168.1.50"
        )
        assert result["success"] is True
        assert result["parent_id"] == "lan"
        assert result["fields_updated"] == ["range_from"]
        data = _sent_data(mock_make_request)
        assert data["parent_id"] == "lan"
        assert data["id"] == 1
        assert data["range_from"] == "192.168.1.50"

    async def test_requires_at_least_one_field(self, mock_client, mock_make_request):
        result = await _update_dhcp_address_pool(parent_id="lan", pool_id=1)
        assert result["success"] is False
        assert "No fields to update" in result["error"]
        mock_make_request.assert_not_called()


class TestDeleteDhcpAddressPool:
    async def test_sends_parent_id_and_id(self, mock_client, mock_make_request):
        mock_make_request.return_value = {"data": {}}
        result = await _delete_dhcp_address_pool(parent_id="lan", pool_id=1, confirm=True)
        assert result["success"] is True
        assert result["parent_id"] == "lan"
        data = _sent_data(mock_make_request)
        assert data["parent_id"] == "lan"
        assert data["id"] == 1

    async def test_confirm_required(self, mock_client, mock_make_request):
        result = await _delete_dhcp_address_pool(parent_id="lan", pool_id=1)
        assert result["success"] is False
        assert "confirm" in result["error"].lower()
