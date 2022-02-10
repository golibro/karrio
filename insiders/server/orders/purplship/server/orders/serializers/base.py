from enum import Enum
from rest_framework import fields
from purplship.server.core.serializers import (
    Address,
    AddressData,
    Commodity,
    CommodityData,
    PlainDictField,
    Serializer,
    EntitySerializer,
    Shipment,
    allow_model_id,
)


class OrderStatus(Enum):
    created = "created"
    cancelled = "cancelled"
    fulfilled = "fulfilled"
    delivered = "delivered"
    partial = "partial"


ORDER_STATUS = [(c.value, c.value) for c in list(OrderStatus)]


@allow_model_id(
    [
        ("shipping_address", "purplship.server.manager.models.Address"),
        ("line_items", "purplship.server.manager.models.Commodity"),
    ]
)
class OrderData(Serializer):
    order_id = fields.CharField(required=True, help_text="The source' order id.")
    source = fields.CharField(
        required=False,
        default="API",
        help_text="""
    The order's source.

    e.g. API, POS, ERP, Shopify, Woocommerce, etc.
    """,
    )
    shipping_address = AddressData(
        required=True,
        help_text="The customer address for the order.",
    )
    line_items = CommodityData(
        many=True, allow_empty=False, help_text="The order line items."
    )
    options = PlainDictField(
        required=False,
        allow_null=True,
        help_text="""
    <details>
    <summary>The options available for the order shipments.</summary>

    ```
    {
        "currency": "USD",
    }
    ```

    Please check the docs for shipment specific options.
    </details>
    """,
    )
    metadata = PlainDictField(
        required=False, default={}, help_text="User metadata for the order."
    )


class Order(EntitySerializer):
    object_type = fields.CharField(
        default="order", help_text="Specifies the object type"
    )
    order_id = fields.CharField(required=True, help_text="The source' order id.")
    source = fields.CharField(required=False, help_text="The order's source.")
    status = fields.ChoiceField(
        choices=ORDER_STATUS,
        default=OrderStatus.created.value,
        help_text="The order status.",
    )
    shipping_address = Address(
        required=True,
        help_text="The customer address for the order.",
    )
    line_items = Commodity(
        many=True, allow_empty=False, help_text="The order line items."
    )
    options = PlainDictField(
        required=False,
        allow_null=True,
        help_text="""
    <details>
    <summary>The options available for the order shipments.</summary>

    ```
    {
        "currency": "USD",
    }
    ```

    Please check the docs for shipment specific options.
    </details>
    """,
    )
    metadata = PlainDictField(
        required=False, default={}, help_text="User metadata for the order."
    )
    shipments = Shipment(
        many=True,
        required=False,
        help_text="The shipments associated with the order.",
    )
    test_mode = fields.BooleanField(
        required=True,
        help_text="Specify whether the order is in test mode or not.",
    )
    created_at = fields.CharField(
        required=True,
        help_text="""
    The shipment creation datetime

    Date Format: `YYYY-MM-DD HH:MM:SS.mmmmmmz`
    """,
    )