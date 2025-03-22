import unittest
from mongomasker_cli.main import (
    anonymize_data,
)
from faker import Faker
import re

uuid_re = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class TestAnonymizeData(unittest.TestCase):

    def setUp(self):
        self.fake = Faker()

    def test_anonymize_simple_fields(self):
        document = {"name": "John Doe", "email": "john.doe@example.com"}
        fields_to_anonymize = {"name": "name", "email": "email"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)

        self.assertNotEqual(anonymized_document["name"], "John Doe")
        self.assertNotEqual(anonymized_document["email"], "john.doe@example.com")

    def test_anonymize_nested_fields(self):
        document = {"user": {"name": "Jane Doe", "email": "jane.doe@example.com"}}
        fields_to_anonymize = {"user.name": "name", "user.email": "email"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)

        self.assertNotEqual(anonymized_document["user"]["name"], "Jane Doe")
        self.assertNotEqual(
            anonymized_document["user"]["email"], "jane.doe@example.com"
        )

    def test_anonymize_array_fields(self):
        document = {"users": [{"name": "John Doe"}, {"name": "Jane Doe"}]}
        fields_to_anonymize = {"users.name": "name"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)

        for user in anonymized_document["users"]:
            self.assertNotEqual(user["name"], "John Doe")
            self.assertNotEqual(user["name"], "Jane Doe")

    def test_anonymize_mixed_fields(self):
        document = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "address": {"city": "New York", "zipcode": "10001"},
            "users": [{"name": "User One"}, {"name": "User Two"}],
        }
        fields_to_anonymize = {
            "name": "name",
            "email": "email",
            "address.city": "city",
            "address.zipcode": "zipcode",
            "users.name": "name",
        }
        anonymized_document = anonymize_data(document, fields_to_anonymize)

        self.assertNotEqual(anonymized_document["name"], "John Doe")
        self.assertNotEqual(anonymized_document["email"], "john.doe@example.com")
        self.assertNotEqual(anonymized_document["address"]["city"], "New York")
        self.assertNotEqual(anonymized_document["address"]["zipcode"], "10001")
        for user in anonymized_document["users"]:
            self.assertNotEqual(user["name"], "User One")
            self.assertNotEqual(user["name"], "User Two")

    def test_anonymize_missing_fields(self):
        document = {"name": "John Doe"}
        fields_to_anonymize = {"email": "email"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        # Ensure missing fields are not added
        self.assertNotIn("email", anonymized_document)

    def test_anonymize_empty_document(self):
        document = {}
        fields_to_anonymize = {"name": "name"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        self.assertEqual(anonymized_document, {})

    def test_anonymize_empty_list(self):
        document = {"users": []}
        fields_to_anonymize = {"users.name": "name"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        self.assertEqual(anonymized_document["users"], [])

    def test_anonymize_nested_lists(self):
        document = {
            "users": [
                {"name": "John Doe", "contacts": [{"email": "john@example.com"}]},
                {"name": "Jane Doe", "contacts": [{"email": "jane@example.com"}]},
            ]
        }
        fields_to_anonymize = {"users.contacts.email": "email"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        for user in anonymized_document["users"]:
            for contact in user["contacts"]:
                self.assertNotEqual(contact["email"], "john@example.com")
                self.assertNotEqual(contact["email"], "jane@example.com")

    def test_anonymize_mixed_types_in_list(self):
        document = {
            "items": [{"name": "Item One"}, "String Item", 12345, {"name": "Item Two"}]
        }
        fields_to_anonymize = {"items.name": "name"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        for item in anonymized_document["items"]:
            if isinstance(item, dict):
                self.assertNotEqual(item["name"], "Item One")
                self.assertNotEqual(item["name"], "Item Two")

    def test_anonymize_deeply_nested_fields(self):
        document = {"level1": {"level2": {"level3": {"name": "Deep Nested Name"}}}}
        fields_to_anonymize = {"level1.level2.level3.name": "name"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        self.assertNotEqual(
            anonymized_document["level1"]["level2"]["level3"]["name"],
            "Deep Nested Name",
        )

    def test_anonymize_start_field(self):
        document = {
            "f1e1b1c4-0b1b-4b1b-8b1b-1b1b1b1b1b1b": {"name": "John Doe"},
            "f1e1b1c4-0b1b-4b1b-8b1b-1b1b1b1b1b1c": {"name": "Jane Doe"},
        }
        fields_to_anonymize = {"*.name": "name"}
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        for key in anonymized_document.keys():
            self.assertNotEqual(anonymized_document[key]["name"], "John Doe")
            self.assertNotEqual(anonymized_document[key]["name"], "Jane Doe")

    def test_anonymize_assessment_data(self):
        assessment = {
            "_id": "7124016",
            "age": 77,
            "amountPaid": 0,
            "amountUnpaid": 403.14,
            "assessmentDate": {"$date": "2024-02-23T00:00:00.000Z"},
            "assessmentId": "7124016",
            "assessmentStatus": "837 Generated",
            "batchId": "20240508",
            "billedDate": {"$date": "2024-05-08T20:16:40.112Z"},
            "billingType": "Claim",
            "claimBilledDate": {"$date": "2024-05-08T20:16:40.112Z"},
            "copay": 0,
            "correlationId": "57a1c00a-2f73-4874-8cf2-581f5eb4b823",
            "createdDate": {"$date": "2024-05-08T20:16:40.112Z"},
            "dateOfServiceFrom": {"$date": "2024-02-23T00:00:00.000Z"},
            "dateOfServiceTo": {"$date": "2024-02-23T00:00:00.000Z"},
            "defaultAmount": 0,
            "defaultAmountPaid": 0,
            "modifiedBy": "Data Sync",
            "modifiedDate": {"$date": "2024-05-10T04:56:18.135Z"},
            "patientAddress": {
                "patientAddressLine": "imvm Y7TB CEpeeE",
                "patientCity": "TZp5QYw",
                "patientZipCode": "3mPvv",
                "patientStateCode": "RL",
            },
            "patientDateOfBirth": {"$date": {"$numberLong": "-714960000000"}},
            "patientFirstName": "NewName",
            "patientGender": "Female",
            "patientId": {
                "idNumber": "imFP3PXN",
                "idType": "Member Identification Number",
            },
            "patientLastName": "KnRUG",
            "payerGroup": "HealthPartners",
            "payerId": "94267",
            "payerMCO": "HealthPartners (HPUPH) - HRA-Home",
            "payerName": "HLTHHPUPH",
            "payerShortName": "HLTHHPUPH",
            "payerSystemId": 153,
            "placeOfService": "Home",
            "providerDetails": {
                "billingProviderName": "COMMUNITY CARE HEALTH NETWORK LLC",
                "billingProviderId": "1619368842",
                "billingProviderTaxId": "061599981",
                "billingProviderTaxonomy": "363L00000X",
                "billingProviderAddress": {
                    "billingProviderCity": "SCOTTSDALE",
                    "billingProviderStateCode": "AZ",
                    "billingProviderZipCode": "852585172",
                    "billingProviderAddressLine": "9201 E MOUNTAIN VIEW RD,SUITE 220",
                },
                "renderingProviders": [
                    {
                        "renderingProviderName": "Schaack,Jessica",
                        "renderingProviderId": "1063567931",
                    }
                ],
            },
            "subscriberDetails": {"subscriberAddress": {}, "subscriberId": {}},
            "totalCharge": 403.14,
        }
        fields_to_anonymize = {
            "patientAddress.patientAddressLine": "address",
            "patientAddress.patientCity": "city",
            "patientAddress.patientZipCode": "zipcode",
            "patientAddress.patientStateCode": "statecode",
            "patientDateOfBirth": "date",
            "patientFirstName": "name",
            "patientId.idNumber": "id",
            "patientLastName": "name",
            "providerDetails.billingProviderName": "name",
            "providerDetails.billingProviderId": "id",
            "providerDetails.billingProviderTaxId": "id",
            "providerDetails.billingProviderTaxonomy": "id",
            "providerDetails.billingProviderAddress.billingProviderCity": "city",
            "providerDetails.billingProviderAddress.billingProviderStateCode": "statecode",
            "providerDetails.billingProviderAddress.billingProviderZipCode": "zipcode",
            "providerDetails.billingProviderAddress.billingProviderAddressLine": "address",
            "providerDetails.renderingProviders.renderingProviderName": "name",
            "providerDetails.renderingProviders.renderingProviderId": "id",
        }
        anonymized_assessment = anonymize_data(assessment, fields_to_anonymize)
        self.assertNotEqual(
            anonymized_assessment["patientAddress"]["patientAddressLine"],
            "imvm Y7TB CEpeeE",
        )
        self.assertNotEqual(
            anonymized_assessment["patientAddress"]["patientCity"], "TZp5QYw"
        )
        self.assertNotEqual(
            anonymized_assessment["patientAddress"]["patientZipCode"], "3mPvv"
        )
        self.assertNotEqual(
            anonymized_assessment["patientAddress"]["patientStateCode"], "RL"
        )
        self.assertNotEqual(anonymized_assessment["patientDateOfBirth"], -714960000000)
        self.assertNotEqual(anonymized_assessment["patientFirstName"], "NewName")
        self.assertNotEqual(anonymized_assessment["patientId"]["idNumber"], "imFP3PXN")
        self.assertNotEqual(anonymized_assessment["patientLastName"], "KnRUG")
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderName"],
            "COMMUNITY CARE HEALTH NETWORK LLC",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderId"], "1619368842"
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderTaxId"],
            "061599981",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderTaxonomy"],
            "363L00000X",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderAddress"][
                "billingProviderCity"
            ],
            "SCOTTSDALE",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderAddress"][
                "billingProviderStateCode"
            ],
            "AZ",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderAddress"][
                "billingProviderZipCode"
            ],
            "852585172",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["billingProviderAddress"][
                "billingProviderAddressLine"
            ],
            "9201 E MOUNTAIN VIEW RD,SUITE 220",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["renderingProviders"][0][
                "renderingProviderName"
            ],
            "Schaack,Jessica",
        )
        self.assertNotEqual(
            anonymized_assessment["providerDetails"]["renderingProviders"][0][
                "renderingProviderId"
            ],
            "1063567931",
        )

    def test_anonymize_history(self):
        document = {
            "_id": "medicalCoding-7728458",
            "0c5e6d4d-cb03-4bfa-959d-b08f8e5ca8e1": {
                "assessmentId": "7728458",
                "diagnoses": [
                    {
                        "claimKey": "1",
                        "order": 4,
                        "code": "E1151",
                        "description": "Type 2 diabetes w diabetic peripheral angiopath w/o gangrene",
                    },
                    {
                        "claimKey": "2",
                        "order": 12,
                        "code": "Z9151",
                        "description": "Personal history of suicidal behavior",
                    },
                ],
                "charges": [
                    {
                        "claimKey": "1",
                        "cptHcpcs": "84999",
                        "description": "FIT Kit Distribution/Mailed",
                        "unit": 1,
                        "amount": 0,
                        "pointers": "2",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "1",
                        "cptHcpcs": "99344",
                        "description": "Comprehensive Health Assessment",
                        "unit": 1,
                        "amount": 475,
                        "pointers": "1,2,3,4,5,6,7,8,9,10,11,12",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "2",
                        "cptHcpcs": "99350",
                        "unit": 1,
                        "amount": 0.01,
                        "pointers": "1,2,3,4,5,6,7,8,9,10,11,12",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "3",
                        "cptHcpcs": "99350",
                        "unit": 1,
                        "amount": 0.01,
                        "pointers": "1,2",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                ],
                "batchId": "20240403",
                "correlationId": "0c5e6d4d-cb03-4bfa-959d-b08f8e5ca8e1",
                "_id": "7728458",
                "createdDate": {"$date": "2024-05-08T00:56:03.057Z"},
                "modifiedDate": {"$date": "2024-05-08T00:56:03.057Z"},
                "modifiedBy": "Data Sync",
            },
            "d5dfc887-acca-4836-93d8-86662f7222cf": {
                "assessmentId": "7728458",
                "diagnoses": [
                    {
                        "claimKey": "1",
                        "order": 4,
                        "code": "E1151",
                        "description": "Type 2 diabetes w diabetic peripheral angiopath w/o gangrene",
                    },
                    {
                        "claimKey": "2",
                        "order": 12,
                        "code": "Z9151",
                        "description": "Personal history of suicidal behavior",
                    },
                ],
                "charges": [
                    {
                        "claimKey": "1",
                        "cptHcpcs": "84999",
                        "unit": 1,
                        "amount": 0,
                        "pointers": "2",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "1",
                        "cptHcpcs": "99344",
                        "unit": 1,
                        "amount": 475,
                        "pointers": "1,2,3,4,5,6,7,8,9,10,11,12",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "2",
                        "cptHcpcs": "99350",
                        "unit": 1,
                        "amount": 0.01,
                        "pointers": "1,2,3,4,5,6,7,8,9,10,11,12",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "3",
                        "cptHcpcs": "99350",
                        "unit": 1,
                        "amount": 0.01,
                        "pointers": "1,2",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                ],
                "batchId": "20240404",
                "correlationId": "d5dfc887-acca-4836-93d8-86662f7222cf",
                "_id": "7728458",
                "createdDate": {"$date": "2024-04-05T20:38:24.089Z"},
                "modifiedDate": {"$date": "2024-04-05T20:38:24.089Z"},
                "modifiedBy": "Data Sync",
            },
            "f9d70f4a-924a-4d03-bdd3-db9fb3417ed8": {
                "assessmentId": "7728458",
                "diagnoses": [
                    {
                        "claimKey": "1",
                        "order": 4,
                        "code": "E1151",
                        "description": "Type 2 diabetes w diabetic peripheral angiopath w/o gangrene",
                    },
                    {
                        "claimKey": "2",
                        "order": 12,
                        "code": "Z9151",
                        "description": "Personal history of suicidal behavior",
                    },
                    {
                        "claimKey": "1",
                        "order": 3,
                        "code": "E1142",
                        "description": "Type 2 diabetes mellitus with diabetic polyneuropathy",
                    },
                ],
                "charges": [
                    {
                        "claimKey": "1",
                        "cptHcpcs": "84999",
                        "unit": 1,
                        "amount": 0,
                        "pointers": "2",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "1",
                        "cptHcpcs": "99344",
                        "unit": 1,
                        "amount": 475,
                        "pointers": "1,2,3,4,5,6,7,8,9,10,11,12",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "2",
                        "cptHcpcs": "99350",
                        "unit": 1,
                        "amount": 0.01,
                        "pointers": "1,2,3,4,5,6,7,8,9,10,11,12",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                    {
                        "claimKey": "3",
                        "cptHcpcs": "99350",
                        "unit": 1,
                        "amount": 0.01,
                        "pointers": "1,2",
                        "serviceDate": {"$date": "2023-09-08T00:00:00.000Z"},
                        "renderingProviderName": "GCBBCA,ZeZZCfeZ",
                        "renderingProviderId": "1780836148",
                        "serviceFacilityName": "COMMUNITY CARE HEALTH NETWORK LLC",
                        "serviceFacilityId": "1619368842",
                    },
                ],
                "batchId": "20240405",
                "correlationId": "f9d70f4a-924a-4d03-bdd3-db9fb3417ed8",
                "_id": "7728458",
                "createdDate": {"$date": "2024-04-05T20:25:05.059Z"},
                "modifiedDate": {"$date": "2024-04-05T20:25:05.059Z"},
                "modifiedBy": "Data Sync",
            },
            "assessmentId": "7728458",
        }

        fields_to_anonymize = {
            "*.charges.renderingProviderName": "lastnamefirstname",
            "*.charges.renderingProviderId": "id",
            "*.charges.serviceFacilityName": "name",
            "*.charges.serviceFacilityId": "id",
            "*.charges.serviceFacilityState": "statecode",
            "*.charges.serviceFacilityZipCode": "zipcode",
            "*.charges.serviceFacilityAddress": "address",
        }
        anonymized_document = anonymize_data(document, fields_to_anonymize)
        for key in anonymized_document.keys():
            if uuid_re.match(key):
                for charge in anonymized_document[key]["charges"]:
                    self.assertNotEqual(
                        charge["renderingProviderName"], "GCBBCA,ZeZZCfeZ"
                    )
                    self.assertNotEqual(charge["renderingProviderId"], "1780836148")
                    self.assertNotEqual(
                        charge["serviceFacilityName"],
                        "COMMUNITY CARE HEALTH NETWORK LLC",
                    )
                    self.assertNotEqual(charge["serviceFacilityId"], "1619368842")


if __name__ == "__main__":
    unittest.main()
