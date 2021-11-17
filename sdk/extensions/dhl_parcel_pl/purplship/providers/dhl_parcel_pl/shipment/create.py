import time
from functools import partial
from typing import List, Tuple, Optional
from dhl_parcel_pl_lib.services import (
    Address,
    Addressat,
    ArrayOfCustomsitemdata,
    ArrayOfPackage,
    ArrayOfService,
    Billing,
    CreateShipmentRequest,
    CustomsData,
    CustomsItemData,
    Package,
    PreavisoContact,
    ReceiverAddress,
    ReceiverAddressat,
    Ship,
    ShipmentInfo,
    ShipmentTime,
    createShipment,
    Service as DhlService,
)
from purplship.core.models import (
    Message,
    Payment,
    ShipmentRequest,
    ShipmentDetails,
)
from purplship.core.utils import (
    Serializable,
    Element,
    create_envelope,
    XP,
    DF,
)
from purplship.core.units import CompleteAddress, Packages, Options, Weight, WeightUnit
from purplship.providers.dhl_parcel_pl.error import parse_error_response
from purplship.providers.dhl_parcel_pl.utils import Settings
from purplship.providers.dhl_parcel_pl.units import (
    PackagingType,
    Option,
    Service,
    LabelType,
    PaymentType,
)


def parse_shipment_response(
    response: Element, settings: Settings
) -> Tuple[ShipmentDetails, List[Message]]:
    pass


def _extract_details(response: Element, settings: Settings) -> ShipmentDetails:
    pass


def shipment_request(payload: ShipmentRequest, settings: Settings) -> Serializable[str]:
    packages = Packages(payload.parcels, required=["weight"])
    shipper = CompleteAddress.map(payload.shipper)
    recipient = CompleteAddress.map(payload.recipient)
    options = Options(payload.options)

    is_international = shipper.country_code != recipient.country_code
    service_type = Service.map(payload.service).value_or_key or (
        Service.dhl_parcel_pl_polska.value
        if is_international
        else Service.dhl_parcel_pl_09.value
    )
    label_type = LabelType.map(payload.label_type or "PDF").value
    payment = payload.payment or Payment()
    customs = payload.customs
    duty = getattr(customs, "duty", None)

    request = create_envelope(
        body_content=createShipment(
            authData=settings.auth_data,
            shipment=CreateShipmentRequest(
                shipmentInfo=ShipmentInfo(
                    wayBill=None,
                    dropOffType="REGULAR_PICKUP",
                    serviceType=service_type,
                    billing=Billing(
                        shippingPaymentType=PaymentType[payment.paid_by],
                        billingAccountNumber=(
                            payment.account_number or settings.account_number
                        ),
                        paymentType="BANK_TRANSFER",
                        costsCenter=None,
                    ),
                    specialServices=(
                        ArrayOfService(
                            item=[
                                DhlService(
                                    serviceType=getattr(option, "key", option),
                                    serviceValue=getattr(option, "value", None),
                                    textInstruction=None,
                                    collectOnDeliveryForm=None,
                                )
                                for option in options
                            ]
                        )
                        if any(options)
                        else None
                    ),
                    shipmentTime=(
                        ShipmentTime(
                            shipmentDate=options.shipment_date,
                            shipmentStartHour="10:00",
                            shipmentEndHour="10:00",
                        )
                        if options.shipment_date
                        else None
                    ),
                    labelType=label_type,
                ),
                content="N/A",
                comment=None,
                reference=payload.reference,
                ship=Ship(
                    shipper=Addressat(
                        preaviso=(
                            PreavisoContact(
                                personName=shipper.person_name,
                                phoneNumber=shipper.phone_number,
                                emailAddress=shipper.email,
                            )
                            if any(
                                [
                                    shipper.person_name,
                                    shipper.phone_number,
                                    shipper.email,
                                ]
                            )
                            else None
                        ),
                        contact=(
                            PreavisoContact(
                                personName=shipper.person_name,
                                phoneNumber=shipper.phone_number,
                                emailAddress=shipper.email,
                            )
                            if any(
                                [
                                    shipper.person_name,
                                    shipper.phone_number,
                                    shipper.email,
                                ]
                            )
                            else None
                        ),
                        address=Address(
                            name=(shipper.company_name or shipper.person_name),
                            postalCode=shipper.postal_code,
                            city=shipper.city,
                            street=shipper.address_line,
                            houseNumber=(shipper.address_line2 or ""),
                            apartmentNumber=None,
                        ),
                    ),
                    receiver=ReceiverAddressat(
                        preaviso=(
                            PreavisoContact(
                                personName=recipient.person_name,
                                phoneNumber=recipient.phone_number,
                                emailAddress=recipient.email,
                            )
                            if any(
                                [
                                    recipient.person_name,
                                    recipient.phone_number,
                                    recipient.email,
                                ]
                            )
                            else None
                        ),
                        contact=(
                            PreavisoContact(
                                personName=recipient.person_name,
                                phoneNumber=recipient.phone_number,
                                emailAddress=recipient.email,
                            )
                            if any(
                                [
                                    recipient.person_name,
                                    recipient.phone_number,
                                    recipient.email,
                                ]
                            )
                            else None
                        ),
                        address=ReceiverAddress(
                            country=recipient.country_code,
                            isPackstation=None,
                            isPostfiliale=None,
                            postnummer=None,
                            addressType=("C" if recipient.residential else "B"),
                            name=(recipient.company_name or recipient.person_name),
                            postalCode=recipient.postal_code,
                            city=recipient.city,
                            street=recipient.address_line,
                            houseNumber=(recipient.address_line2 or ""),
                            apartmentNumber=None,
                        ),
                    ),
                    neighbour=None,
                ),
                pieceList=ArrayOfPackage(
                    item=[
                        Package(
                            type_=PackagingType[
                                package.package_type or "your_packaging"
                            ].value,
                            euroReturn=None,
                            weight=package.weight.KG,
                            width=package.width.CM,
                            height=package.height.CM,
                            length=package.length.CM,
                            quantity=None,
                            nonStandard=None,
                            blpPieceId=None,
                        )
                        for package in packages
                    ]
                ),
                customs=(
                    CustomsData(
                        customsType="U",
                        firstName=getattr(
                            getattr(duty, "bil_to", None), "company_name", "N/A"
                        ),
                        secondaryName=getattr(
                            getattr(duty, "bil_to", None), "person_name", "N/A"
                        ),
                        costsOfShipment=getattr(
                            duty or options, "declared_value", None
                        ),
                        currency=getattr(duty or options, "currency", "EUR"),
                        nipNr=None,
                        eoriNr=None,
                        vatRegistrationNumber=None,
                        categoryOfItem=None,
                        invoiceNr=customs.invoice,
                        invoice=None,
                        invoiceDate=customs.invoice_date,
                        countryOfOrigin=shipper.country_code,
                        additionalInfo=None,
                        grossWeight=packages.weight.KG,
                        CustomsItem=(
                            ArrayOfCustomsitemdata(
                                item=[
                                    CustomsItemData(
                                        nameEn=item.description or "N/A",
                                        namePl="N/A",
                                        quantity=item.quantity,
                                        weight=Weight(
                                            item.weight,
                                            WeightUnit[item.weight_unit or "KG"],
                                        ).KG,
                                        value=item.value_amount,
                                        tariffCode=item.sku,
                                    )
                                    for item in customs.commodities
                                ]
                            )
                            if any(customs.commodities)
                            else None
                        ),
                        customAgreements=None,
                    )
                    if customs is not None
                    else None
                ),
            ),
        )
    )

    return Serializable(
        request, lambda req: settings.serialize(req, request_name="createShipment")
    )
