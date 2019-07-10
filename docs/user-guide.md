# User Guide

* [Introduction](#introduction)
* [Writing a schema](#writing-a-schema)
  * [Validating types](#validating-types)
  * [Nested fields](#nested-fields)
  * [Lists](#lists)
  * [Unspecified fields](#unspecified-fields)
  * [Custom validation functions](#custom-validation-functions)
  * [Using regular code](#using-regular-code)
  * [Passing parameters](#passing-parameters)
* [Running the validator](#running-the-validator)
  * [Loading documents](#loading-documents)
  * [Identifying documents](#identifying-documents)
  * [Dealing with large files](#dealing-with-large-files)
  * [Validation messages](#validation-messages)

## Introduction

The Okay library allows you to validate documents according to a data schema that you define. Your document should be a Python dictionary, so if it's stored in a different format, you need to convert it first. For example, if you have data in JSON, you need to pass it through `json.loads()` before you can validate it. You write your schema definition in Python.

Here's an example of the whole process.

```python
from okay import validate
from okay.schema import *

def schema():
    required('title', type='string')
    required('author', type='string')
    optional('page_count', type='int', min=1)

book = {
    'title': 'An Equal Music',
    'author': 'Vikram Seth',
    'page_count': 0,
    'language': 'en'
}

validation_messages = validate(schema, book)
for message in validation_messages:
    print(f'{message.field}:\t{message.type}')
```

Output:

```
page_count:     number_too_small
language:       extra_field
```

## Writing a schema

You can define a schema in a function that takes no parameters. (Actually, any parameterless callable will do.) Using the validation functions `required()` and `optional()`, you can specify all the fields in your schema. Both functions take the field name as the first parameter.

```python
from okay.schema import *

def book_schema():
    required('title')
    required('author')
    optional('page_count')
```

As you can see in the example above, you need to import the validation functions before you can use them. Don't worry about `import *`. The module `okay.schema` was specifically designed to only include the validation functions.

### Validating types

Generally, you want to validate the type of a field. You can do this by passing the desired type to the validation function.

```python
from okay.schema import *

def book_schema():
    required('title', type='string')
    required('author', type='string')
    optional('page_count', type='int')
```

Each type has its own parameters to further specify validation options. For example, `int` has a `min` and a `max` parameter that allow you to specify a range, and `string` has the parameter `regex` which you can use to make sure a value matches a specific regular expression.

```python
from okay.schema import *

def book_schema():
    required('title', type='string')
    required('author', type='string', regex=r'[\w \.\-]+')
    optional('page_count', type='int', min=1)
```

You can find a [full list of available types](docs/reference.md#types) in the Reference Guide.

### Nested fields

Fields in a document can be nested, like `author` in the following example.

```python
book = {
    'title': 'An Equal Music',
    'author': {
        'first_name': 'Vikram',
        'last_name': 'Seth'
    }
}
```

In this case `author` is of type `object`. You can refer to nested fields by using the `.`, so `author.first_name` and `author.last_name`. (Because of this, Okay doesn't support fields that have a `.` in their name.)

```python
from okay.schema import *

def book_schema():
    required('title', type='string')
    required('author', type='object')
    optional('author.first_name', type='string', regex=r'[\w\.\-]+')
    required('author.last_name', type='string', regex=r'[\w \-]+')
```

It's possible to make an object optional, but have its children be required. In the following example, the schema states that you don't have to include a publication date, but if you do, it must have at least a year.

```python
from okay.schema import *

def book_schema():
    optional('publication_date', type='object')
    required('publication_date.year', type='int')
    optional('publication_date.month', type='int', min=1, max=12)
    optional('publication_date.day', type='int', min=1, max=31)
```

### Lists

To validate that a field is a list, use the `list` type. The `min` and `max` parameters allow you to specify the expected size of the list.

```python
from okay.schema import *

def book_schema():
    required('authors', type='list', min=1)
```

You can validate elements in the list by appending `[]` to the field name. The validation parameters you specify will be applied to each element individually.

```python
from okay.schema import *

def book_schema():
    optional('genres', type='list')
    optional('genres[]', type='string')
    required('authors', type='list', min=1)
    required('authors[]', type='object')
    optional('authors[].first_name', type='string')
    required('authors[].last_name', type='string')
```

In this example, `genres` is an optional list of strings and `authors` is a required list of authors, where each author has an optional first name and a required last name. `genres` can be an empty list, but `authors` must have at least one element.

There's an oddity with validation rules for list elements: `optional` and `required` don't apply to the list elements. Instead they apply to the list. In other words, `optional('genres[]', type='object')` automatically makes the field `genres` an optional list, so the line `optional('genres', type='list')` is superfluous. You only need to add a validation rule for the list itself if you want to validate more than just its type. In the example above, we need to keep the line `required('authors', type='list', min=1)` to ensure that the list has at least one element.

### Unspecified fields

By default, the validator reports any fields it finds in a document that aren't explicitly specified in your schema.

```python
from okay import validate
from okay.schema import *

def schema():
    pass

book = {
    'title': 'An Equal Music',
    'author': 'Vikram Seth'
}

validation_messages = validate(schema, book)
for message in validation_messages:
    print(f'{message.field}:\t{message.type}')
```

Output:

```
title:  extra_field
author: extra_field
```

If you want to allow unspecified fields in a document, you can do so by calling the validation function `ignore_extra_fields()`. Of course, these extra fields won't be validated in any way. The following example won't produce any validation messages.

```python
from okay import validate
from okay.schema import *

def schema():
    ignore_extra_fields()

book = {
    'title': True,
    'author': [ 'Vikram' , 'Seth' ]
}

validation_messages = validate(schema, book)
for message in validation_messages:
    print(f'{message.field}:\t{message.type}')
```

There are two situations where the validator creates implicit validation rules:

* When you write a validation rule for a nested field.
* When you write a validation rule for list elements.

As soon as you specify a nested field, all its parent will automatically become optional objects. You can, of course, explicitly state that they should be required.

```python
def book_schema():
    optional('publication_date', type='object')     # unnecessary: implied by the rules below
    required('publication_date.year', type='int')
    optional('publication_date.month', type='int')
    optional('publication_date.day', type='int')

    required('author', type='object')       # necessary to make the field required
    required('author.first_name', type='string')
    required('author.last_name', type='string)
```

As soon as you create a validation rule for list elements, the list itself will also get a validation rule. Whether the list is optional or required depends on what you specify for the list elements. In other words, for list elements `optional` and `required` refer to the list, not the elements. The only case where you need to explicitly add a validation rule for the list itself, is when you want to validate more than its type, for example its length.

```python
from okay.schema import *

def book_schema():
    optional('genres', type='list')     # unnecessary: implied by the rule below
    optional('genres[]', type='string')

    required('copyright_years', type='list')    # unnecessary: implied by the rule below
    required('copyright_years[]', type='int')

    required('authors', type='list', min=1)     # necessary to validate the number of elements
    required('authors[]', type='object')
```

### Custom validation functions

If you need validate a field in a way that isn't covered by the types Okay provides, you can write a custom validation function. A custom validation function receives the field's name and value as parameters. If validation fails, you return a `Message`-object to indicate what went wrong. If validation succeeds, you don't return anything.

```python
from okay import Message

def book_schema():
    def is_capitalized(field, value):
        lines = value.split('.')
        for line in lines:
            line = line.strip()
            if len(line) > 0 and not line[0].isupper():
                return Message(
                    type='not_properly_capitalized',
                    field=field
                )

    optional('summary', type='custom', validator=is_capitalized)
```

You can also use custom validation functions to validate fields that depend on each other, as long as they aren't top-level fields.

```python
from okay import Message

def schema():
    def valid_range(field, value):
        if not isinstance(value, dict) or (not 'min' in value) or (not 'max' in value):
            return

        if value['min'] > value['max']:
            return Message(
                type='invalid_range',
                field=field
            )

    optional('range', type='custom', validator=valid_range)
    required('range.min', type='int')
    required('range.max', type='int')
```

Note in the custom validation function above that it doesn't return a message when `range` is not a field or when the fields `min` and `max` are missing. It only validates the range if it is actually there. This is a good approach in general, because it keeps your options open when writing your schema. In this example, you now have the option to allow an open-ended range, i.e. a range with only a minimum or only a maximum. If you don't want to allow an open-ended range, you simply make `min` and `max` required, as shown above, but `valid_range` doesn't have to force this on you.

### Using regular code

Your schema isn't limited to calling validation functions; it's a regular Python function, so you can call regular Python code. This can be useful if you want to base your validation on some calculated data. The following example makes sure a year isn't in the future.

```python
from datetime import date
from okay.schema import *

def schema():
    current_year = date.today().year
    required('year', type='int', max=current_year)
```

### Passing parameters

Since you don't call your schema yourself – the validator does this for you – you can't pass parameters to your schema. However, if that's something you need, you have two options: either create a callable object, or create a closure.

Here's an example of a callable object.

```python
from okay.schema import *

class BookSchema:
    def __init__(self, strict):
        self._strict = strict

    def __call__(self):
        required('title', type='string')
        required('author', type='string')

        page_count_parameters = { 'type': 'int', 'min': 0 }
        if self._strict:
            required('page_count', **page_count_parameters)
        else:
            optional('page_count', **page_count_parameters)

book_schema = BookSchema(strict=True)
```

Here is the same schema, but as a closure.

```python
from okay.schema import *

def create_book_schema(strict):
    def schema():
        required('title', type='string')
        required('author', type='string')

        page_count_parameters = { 'type': 'int', 'min': 0 }
        if strict:
            required('page_count', **page_count_parameters)
        else:
            optional('page_count', **page_count_parameters)

    return schema

book_schema = create_book_schema(strict=True)
```

## Running the validator

You validate a document by calling `validate()` and passing it a schema and a document. The result is a list of validation messages. This isn't all that hard to wrap you head around, but when it comes to writing the main loop of your validator, the devil is in the details.

### Loading documents

Documents typically don't spend their entire life being Python dictionaries. Instead, they are stored somewhere as JSON, or CSV, or XML. This means you have to parse the document first. The following example validates a single JSON document stored on the local file system.

```python
import json
from okay import validate
from okay.schema import *

def book_schema():
    required('title', type='string')
    required('author', type='string')
    optional('page_count', type='int', min=1)

with open('an-equal-music.json') as file:
    document = json.load(file)
    validation_messages = validate(book_schema, document)

for message in validation_messages:
    print(f'{message.field}:\t{message.type}')
```

### Identifying documents

You'll often deal with the situation where a single file contains multiple documents. However, the validator doesn't understand the concept of multiple documents: it deals with documents one by one. As a consequence, validation messages don't include information on exactly which document failed validation. Fortunately, Okay allows you to pass custom fields to the validator, which it will then add to all validation messages. In the following example, we read multiple documents from a JSON file, we number the documents, and we use a custom field to include the document number in all validation messages.

```python
import json
from okay import validate
from okay.schema import *

def book_schema():
    required('title', type='string')
    required('author', type='string')
    optional('page_count', type='int', min=1)

with open('books.json') as file:
    documents = json.load(file)
    for i, document in enumerate(documents):
        message_values = { 'document_number': i }
        validation_messages = validate(book_schema, document, message_values)

        for message in validation_messages:
            print(f'{message.document_number}:{message.field}\t{message.type}')
```

Sample output:

```
2:author        missing_field
2:page_count    number_too_small
7:author        invalid_type
```

If your documents contain some kind of unique ID, you may be tempted to use that instead of the document number, but it's probably better to use both. Even if the ID is required, that's no guarantee all documents have one; that's why you're validating. Also, the IDs that are there may not be unique, even though they should be. It's fine to add the ID to the validation message if it exists, but you should also add the document number, just in case. The following example adds the ISBN (a unique identifier for books) to the validation messages if possible, but it doesn't rely on them.

```python
import json
from okay import validate
from okay.schema import *

def book_schema():
    required('isbn', type='string')
    required('title', type='string')
    required('author', type='string')
    optional('page_count', type='int', min=1)

with open('books.json') as file:
    documents = json.load(file)
    for i, document in enumerate(documents):
        message_values = {
            'document_number': i,
            'isbn': document['isbn'] if 'isbn' in document else ''
        }
        validation_messages = validate(book_schema, document, message_values)

        for message in validation_messages:
            print(f'{message.document_number}:{message.isbn}:{message.field}\t{message.type}')
```

Sample output:

```
0:1-86159-117-9:author      missing_field
0:1-86159-117-9:page_count  number_too_small
1::isbn                     missing_field
1::author                   invalid_type
```

### Dealing with large files

If the file (or whatever you use to store your documents) contains a large number of documents, it might be unfeasible to load the entire file into memory. In that case, you need to stream documents in, so you can process the file in chunks. Exactly how to do that depends on the file format. For line-based formats like CSV and JSON Lines, you can simply read one line at a time. For nested formats like XML and YAML, or binary formats like Avro or Protobuf you need a parser that can read documents one by one.

You will also want to implement robust error handling. If one of the lines in your CSV file is malformed, or if you have a bug in your custom validation function, you'll probably get an exception, which stops all validation. Instead of fixing the problem and rerunning the validator on all that data you already processed, you're probably better off catching the exception and validating as many documents as you can.

The following example reads documents from a JSON Lines file one by one and tries to keep going even if something goes wrong.

```python
import json
import logging
from okay import validate, Message
from okay.schema import *

def book_schema():
    def faulty_validator(field, value):
        return field[value]     # this will raise an exception

    required('title', type='custom', validator=faulty_validator)
    required('author', type='string')
    optional('page_count', type='int', min=1)

with open('books.json') as file:
    for i, line in enumerate(file):
        try:
            document = json.loads(line)
            message_values = { 'document_number': i }
            validation_messages = validate(book_schema, document, message_values)
        except json.JSONDecodeError as e:
            # Treat invalid JSON as a validation error.
            validation_messages = [Message(
                type='invalid_json',
                document_number=i,
                message=e.msg,
                position=e.pos
            )]
        except:
            # Don't know what went wrong. Log and continue.
            validation_messages = []
            logging.exception('An unexpected exception occurred during validation.')

        for message in validation_messages:
            print(message.__dict__)
```

### Validation messages

Validation messages aren't returned as human-readable strings. Instead, they're `Message`-objects that contain all data that's relevant to the validation error. This way, you are completely flexible in how you want to handle validation messages.

A validation message always has a `type` property that indicates why validation failed. It usually also has a `field` property that tells you the name of the field that didn't pass validation. You can create messages without a `field`, though, in case validation of the entire document fails, like in the [example above](#dealing-with-large-files). Whenever possible, a validation message will include an `expected` property to let you know what data in the document should've been. For example, if a field's type is invalid, `expected` contains the type the field should've had, and if a number field's value is too large, `expected` contains the maximum value allowed.

When you return a `Message` object from a [custom validation function](#custom-validation-functions), you can add any properties you like, but it's probably useful to use the ones described above whenever possible. It will make formatting validation messages much easier. Also, if you [add context information to your validation messages](#identifying-documents), you will have to change the code that formats the messages accordingly.