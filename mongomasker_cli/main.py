import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
import typer
from typing import List
from datetime import datetime

app = typer.Typer()
fake = Faker()

def warning(msg):
    typer.secho(f"warning: {msg}", fg=typer.colors.YELLOW, bold=True)


def info(msg):
    typer.secho(msg, fg=typer.colors.GREEN, bold=True)


def error(msg):
    typer.secho(f"error: {msg}", fg=typer.colors.RED, bold=True)


def success(msg):
    typer.secho(msg, fg=typer.colors.GREEN, bold=True)


# Function to generate fake data based on field type
def generate_fake_data(data_type):
    if data_type == "name":
        return fake.first_name()
    elif data_type == "company":
        return fake.company()
    elif data_type == "email":
        return fake.email()
    elif data_type == "address":
        return fake.address()
    elif data_type == "date":
        return datetime.strptime(fake.date(), "%Y-%m-%d")
    elif data_type == "datestr":
        return fake.date()
    elif data_type == "zipcode":
        return fake.zipcode()
    elif data_type == "statecode":
        return fake.state_abbr()
    elif data_type == "lastname":
        return fake.last_name()
    elif data_type == "lastnamefirstname":
        return fake.last_name() + "," + fake.first_name()
    elif data_type == "city":
        return fake.city()
    elif data_type == "id":
        # numeric string
        return str(fake.random_number(digits=10))
    else:
        return fake.word()  # Default fake data


def generate_fake_data_different(data_type, original_val):
    new_value = generate_fake_data(data_type)
    while new_value == original_val:
        new_value = generate_fake_data(data_type)
    return new_value


# Function to anonymize fields
def anonymize_data(document, fields, show_warnings=False):
    doc_id = document.get("_id", "NO_ID")

    # typer.echo(f"Anonymizing document: {document["_id"]}")
    # typer.echo(f"Fields to anonymize: {fields}, document: {document}")
    def _anonymize(doc, keys, data_type):
        # typer.echo(f"keys: {keys} doc: {doc}")
        if len(keys) == 1:
            if isinstance(doc, list):
                for item in doc:
                    if isinstance(item, dict):
                        if keys[0] not in item:
                            if show_warnings:
                                warning(
                                    f"[{doc_id}] key {keys[0]} of type {data_type} not found in document"
                                )
                        else:
                            item[keys[0]] = generate_fake_data_different(
                                data_type, item[keys[0]]
                            )
                    else:
                        if show_warnings:
                            warning(
                                f"[{doc_id}] nested list not supported, {keys[0]} is a list in {doc}"
                            )
            elif keys[0] in doc:
                doc[keys[0]] = generate_fake_data_different(data_type, doc[keys[0]])
            else:
                if show_warnings:
                    warning(
                        f"[{doc_id}] key {keys[0]} of type {data_type} not found in document"
                    )

        else:
            key = keys[0]
            if isinstance(doc, list):
                for item in doc:
                    if isinstance(item, dict):
                        _anonymize(item[key], keys[1:], data_type)
                    else:
                        if show_warnings:
                            warning(f"[{doc_id}] nested list not supported")
            elif key in doc:
                _anonymize(doc[key], keys[1:], data_type)
            elif key == "*":  # means all keys in the document
                for k in doc.keys():
                    _anonymize(doc[k], keys[1:], data_type)

    for field, data_type in fields.items():
        keys = field.split(".")
        _anonymize(document, keys, data_type)
    return document


async def process_batch(batch, target_collection, fields_to_anonymize, show_warnings=False):
    anonymized_batch = [anonymize_data(doc, fields_to_anonymize, show_warnings) for doc in batch]
    # info(f"Anonymized batch of {len(anonymized_batch)} documents")
    await target_collection.insert_many(anonymized_batch)
    # info(f"Inserted batch of {len(anonymized_batch)} documents")


@app.command()
def main(
    mongo_uri: str = typer.Argument(..., help="MongoDB connection URI"),
    source_db: str = typer.Argument(..., help="Source database name"),
    source_collection: str = typer.Argument(..., help="Source collection name"),
    target_db: str = typer.Argument(..., help="Target database name"),
    target_collection: str = typer.Argument(..., help="Target collection name"),
    fields_to_anonymize_file: typer.FileText = typer.Argument(
        ..., help="JSON file with fields to anonymize"
    ),
    batch_size: int = typer.Option(100, help="Batch size for processing"),
    show_warnings: bool = typer.Option(False, help="Show warnings"),
):
    async def run():
        client = AsyncIOMotorClient(mongo_uri)
        source_db_handle = client[source_db]
        target_db_handle = client[target_db]

        source_collection_handle = source_db_handle[source_collection]
        target_collection_handle = target_db_handle[target_collection]

        fields_to_anonymize = json.load(fields_to_anonymize_file)

        cursor = source_collection_handle.find()
        total_documents = await source_collection_handle.count_documents({})
        info(f"Total documents to process: {total_documents}")
        processed_documents = 0

        with typer.progressbar(
            length=total_documents, label="Processing documents"
        ) as progress:
            batch = []
            async for document in cursor:
                batch.append(document)
                if len(batch) >= batch_size:
                    # info(f"Processing batch of {len(batch)} documents")
                    await process_batch(
                        batch, target_collection_handle, fields_to_anonymize, show_warnings
                    )
                    # info(f"Processed {len(batch)} documents")
                    processed_documents += len(batch)
                    progress.update(len(batch))
                    batch = []

            # Process any remaining documents in the last batch
            if batch:
                await process_batch(
                    batch, target_collection_handle, fields_to_anonymize, show_warnings
                )
                processed_documents += len(batch)
                progress.update(len(batch))

        success(f"Data anonymized and copied to {target_db}.{target_collection}")
        success(f"Total documents processed: {processed_documents}")

    asyncio.run(run())


if __name__ == "__main__":
    app()
