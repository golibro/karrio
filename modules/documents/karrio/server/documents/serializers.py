import karrio.lib as lib
import karrio.server.serializers as serializers
import karrio.server.documents.models as models


class TemplateRelatedObject(lib.StrEnum):
    shipment = "shipment"
    order = "order"


@serializers.owned_model_serializer
class DocumentTemplateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentTemplate
        exclude = ["created_at", "updated_at", "created_by"]
