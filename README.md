# MongoMasker

MongoMasker is a tool designed to anonymize specified fields in a MongoDB collection. It uses the `faker` library to generate realistic fake data, processes documents in batches for improved performance, and leverages asynchronous processing with `motor` for efficiency.

## Features

- Anonymizes specified fields with realistic fake data
- Supports nested fields and fields within objects in arrays
- Processes documents in batches for better performance
- Uses asynchronous processing for efficiency
- Allows warnings for missing fields or unsupported structures

## Requirements

- Python 3.6+
- `motor` library
- `pymongo` library
- `faker` library
- `typer` library

## Installation

Install the required libraries using pip:

```bash
poetry install
```

## Usage
Command-Line Example
To anonymize fields in a MongoDB collection, run the following command:

```bash
mongomasker \
    "mongodb://your_username:your_password@your_host:your_port" \
    source_database \
    source_collection \
    target_database \
    target_collection \
    fields_to_anonymize.json \
    --batch-size 100 \
    --show-warnings
```

Arguments
 - `mongo_uri`: MongoDB connection URI (e.g., `"mongodb://localhost:27017"`)
 - `source_db`: Name of the source database
 - `source_collection`: Name of the source collection
 - `target_db`: Name of the target database
 - `target_collection`: Name of the target collection
 - `fields_to_anonymize_file`: Path to the JSON file specifying the fields to anonymize
 - `--batch-size`: (Optional) Number of documents to process in each batch (default: 100)
 - `--show-warnings`: (Optional) Show warnings for missing fields or unsupported structures
Example `fields_to_anonymize.json`
Create a JSON file specifying the fields to anonymize and their corresponding data types. For example:

```json
{
    "name": "name",
    "email": "email",
    "address.street": "address",
    "address.city": "city",
    "address.zipcode": "zipcode",
    "user.stateCode": "statecode",
    "user.lastname": "lastname",
    "user.fullname": "lastnamefirstname",
    "createdAt": "date",
    "updatedAt": "datestr",
    "order.id": "id"
}
```

### Explanation of Transformations

The `fields_to_anonymize.json` file maps field names to the type of fake data to generate. Below are examples of transformations for various data types:


| Field Name | Data Type | Example Transformation |
|------------|-----------|------------------------|
| name | name | "John" → "Alice" |
| email | email | "john.doe@example.com" → "alice@example.com" |
| address.street | address | "123 Main St" → "456 Elm St" |
| address.city | city | "New York" → "Los Angeles" |
| address.zipcode | zipcode | "10001" → "90210" |
| user.stateCode | statecode | "NY" → "CA" |
| user.lastname | lastname | "Doe" → "Smith" |
| user.fullname | lastnamefirstname | "Doe, John" → "Smith, Alice" |
| createdAt | date | "2023-01-01" → "2025-03-22" |
| updatedAt | datestr | "2023-01-01" → "2025-03-22" |
| order.id | id | "1234567890" → "9876543210" |

Sample Workflow
Prepare the fields_to_anonymize.json file: Create a JSON file specifying the fields to anonymize and their corresponding data types.

Run the MongoMasker CLI: Use the command-line tool to anonymize the data in the source collection and copy it to the target collection.

Verify the Results: Check the target collection to ensure the data has been anonymized as expected.

Example
### Input Document (Source Collection)
```json
{
    "_id": "12345",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "zipcode": "10001"
    },
    "user": {
        "stateCode": "NY",
        "lastname": "Doe",
        "fullname": "Doe, John"
    },
    "createdAt": "2023-01-01",
    "updatedAt": "2023-01-02",
    "order": {
        "id": "1234567890"
    }
}
```

### Output Document (Target Collection)

```json
{
    "_id": "12345",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "address": {
        "street": "456 Elm St",
        "city": "Los Angeles",
        "zipcode": "90210"
    },
    "user": {
        "stateCode": "CA",
        "lastname": "Smith",
        "fullname": "Smith, Alice"
    },
    "createdAt": "2025-03-22",
    "updatedAt": "2025-03-22",
    "order": {
        "id": "9876543210"
    }
}
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.
