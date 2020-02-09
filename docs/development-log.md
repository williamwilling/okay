# Development log

In this log, I'll keep a record of what I was thinking during the development of this library. I suspect this will mostly be a stream of consciousness, and I don't really expect a lot of people to read it. It's more an aid for me to reason problems through, to be able to find my previous decisions, and to a have a list of stuff I need to turn into proper documentation.

_Historical note_: When I started this project, I had a design log instead of a development log. It was topic-based, limited to design issues, and intended to be readable. Over time, it became a mess, so I decided to create this development log – which is intended to be messy – and a separate document that describes the design of the library. The start of this development log is copied from the old design log.

* [Background](#background)
* [Basic concept](#basic-concept)
* [Syntax](#syntax)
  * [Function call style](#function-call-style)
  * [Fluent style](#fluent-style)
  * [Dictionary style](#dictionary-style)
  * [Comparison](#comparison)
* [Error reporting](#error-reporting)
  * [Error location](#error-location)
  * [Showing errors](#showing-errors)
* [Data sources](#data-sources)
* [Data sinks](#data-sinks)
* [Parallel processing](#parallel-processing)
* [Default behavior](#default-behavior)
  * [Extra fields](#extra-fields)
  * [Nested fields](#nested-fields)
* [Data types](#data-types)
  * [Lists](#lists)
  * [Multiple types](#multiple-types)
* [Data formats](#data-formats)
  * [Readers and stores](#readers-and-stores)
  * [Detecting the data format](#detecting-the-data-format)
  * [Non-stream-based stores](#non-stream-based-stores)
  * [Error handling](#error-handling)
* [Connecting sources and sinks](#connecting-sources-and-sinks)
* [Sinking a collection of documents](#sinking-a-collection-of-documents)
* [Multiple sources, multiple sinks](#multiple-sources-multiple-sinks)
* [Non-validation errors](#non-validation-errors)
* [Splitting the library](#splitting-the-library)
* [Redesign](#redesign)
  * [Syntax improvements](#syntax-improvements)
  * [Validation messages](#validation-messages)
  * [Validator interface](#validator-interface)
* [No Schema-class](#no-schema-class)
* [Library name](#library-name)
* [Parameterless schema functions](#parameterless-schema-functions)
* [SchemaError)](#schemaerror)
* [Performance optimizations](#performance-optimizations)
* [Nullable fields](#nullable-fields)
  * [Default nullability](#default-nullability)
  * [Specifying nullability](#specifying-nullability)
  * [Reporting null-values](#reporting-null-values)

## Background

Scrapinghub sent us a sample of a thousand accommodations in JSON Lines format. We needed to check if they adhered to the schema we agreed upon with them, so I put together a simple validator and it served it's purpose. It was a fun little project and now I want to expand on it. I have some nice ideas for improvements, but if I'm putting in the effort, I might as well make it useful in the long term. Since the original validator was a quick, one-off project, I didn't bother with things like unit tests or even version control. So, I'm starting from scratch, doing it right (or at least better) this time.

## Basic concept

1. You define your data schema in Python.
2. You obtain a list of data objects.
3. You run the validator, which will check if each of the objects adhere to the schema.

Nothing earth-shattering. The fun part is coming up with a way to define data schemas that is both flexible and easy to use.

## Syntax

Let's say we want to encode the following data schema.

field                         | type            | required | remarks
------------------------------|-----------------|----------|---------
`metadata`                    | object          | yes      |
`metadata.accommodation_id`   | int             | yes      | must be positive
`accommodation`               | object          | yes      |
`accommodation.name`          | string          | yes      |
`accommodation.geo`           | object          | no       |
`accommodation.geo.longitude` | string          | yes      | must be a number (the type is string to prevent rounding issues)
`accommodation.geo.latitude`  | string          | yes      | must be a number (the type is string to prevent rounding issues)
`accommodation.images`        | list of objects | no       |
`accommodation.images[].size` | int             | no       | must be positive
`accommodation.images[].url`  | string          | yes      | must be a URL

* This doesn't cover all possible scenarios, but has enough variation to get a good impression of different syntaxes.
* Nested fields use a `.` as a separator, meaning that field names can't contain a `.`. I think that's a reasonable assumption.
* A nested field can be required, even though it's parent is not. What this means is that the nested field must be present if the parent is.

Here are the basic styles I want to consider for turning this schema into Python. (I considered several variations for each of these styles, but I'm not going to list them all here.) Goals are: flexibility and ease-of-use.

### Function call style

```python
def schema(validator):
    number_pattern = r'\-?\d+\(.\d+)?'
    url_pattern = r'https?://.+'

    validator.required('metadata', type='object')
    validator.required('metadata.accommodation_id', type='int', minimum=1)
    validator.required('accommodation', type='object')
    validator.required('accommodation.name', type='string')
    validator.optional('accommodation.geo', type='object')
    validator.required('accommodation.geo.longitude', type='string', regex=number_pattern)
    validator.required('accommodation.geo.latitude', type='string', regex=number_pattern)
    validator.optional('accommodation.images', type='list of object')
    validator.optional('accommodation.images[].size', type='int', minimum=0)
    validator.optional('accommodation.images[].url', type='string', regex=url_pattern)
```

### Fluent style

```python
def schema(validator):
    number_pattern = r'\-?\d+\(.\d+)?'
    url_pattern = r'https?://.+'

    validator.required('metadata').type('object')
    validator.required('metadata.accommodation_id').type('number').minimum(1)
    validator.required('accommodation').type('object')
    validator.required('accommodation.name').type('string')
    validator.optional('accommodation.geo').type('object')
    validator.required('accommodation.geo.longitude').type('string').regex(number_pattern)
    validator.required('accommodation.geo.latitude').type('string').regex(number_pattern)
    validator.optional('accommodation.images').type('list of object')
    validator.optional('accommodation.images[].size').type('number').minimum(0)
    validator.optional('accommodation.images[].url').type('string').regex(url_pattern)
```

### Dictionary style

```python
def schema(validator):
    number_pattern = r'\-?\d+\(.\d+)?'
    url_pattern = r'https?://.+'

    schema = {
        'metadata': { required=True, type='object' },
        'metadata.accommodation_id': { required=True, type='number', minimum=1 },
        'accommodation': { required=True, type='object' },
        'accommodation.name': { required=True, type='string' },
        'accommodation.geo': { required=False, type='object' },
        'accommodation.geo.longitude': { required=True, type='string', regex=number_pattern },
        'accommodation.geo.latitude': { required=True, type='string', regex=number_pattern },
        'accommodation.images': { required=False, type='list of object' },
        'accommodation.images[].size': { required=False, type='number', minimum=0 },
        'accommodation.images[].url': { required=True, type='string', regex=url_pattern }
    }

    validator.apply(schema)
```

### Comparison

With the fluent style, you can't put common arguments in a variable. For example, longitude and latitude have the same schema definition, so in dictionary style, you can write:

```python
geo_number = { required=True, type='string', regex=number_pattern }
schema = {
    'accommodation.geo.longitude': geo_number,
    'accommodation.geo.latitude': geo_number
}
```

In function call style, it would look like this:

```python
geo_number = { type='string', regex=number_pattern }
validator.required('accommodation.geo.longitude', **geo_number)
validator.required('accommodation.geo.latitude', **geo_number)
```

There is no equivalent for the fluent style. Also, with the fluent style, the validator doesn't have the full context when it does validation; it only gets one argument at a time. This could be relevant for error messages, logging, or complex validations. Say, for example, that you have this schema:

```python
validator.required('hour').type('int').minimum(0).maximum(23)
```

If `hour` is outside of the specified range, you may want to produce an error message like _`hour` must be between 0 and 24_. You can't do that with the fluent style, because neither the call to `minimum()` nor the call to `maximum()` has enough information. Sure, you could solve it by replacing those two functions with a single one called `range()`, but there are bound to be other situations like this where such a solution isn't available. Function call style and dictionary style don't have this problem.

At this point, I'll strike fluent style off the list.

Function call style and dictionary style both look good to me. I'm not too concerned about repeating `validator` each time in function call style; that'll be easy enough to get rid off. My gut feeling is that function call style is a bit more flexible in complex situations, but I can't come up with an example, so maybe I'm just imagining things. (Can you imagine things with your gut?) What I do like about dictionary style, is that each line starts with the field name instead of with `required` or `optional`.

In function call style the order may matter.

```python
validator.required('accommodation.geo.longitude', type='string', regex=number_pattern)
validator.required('accommodation.geo.latitude', type='string', regex=number_pattern)
validator.optional('accommodation.geo', type='object')
```

`accommodation.geo` is optional, so if the field is missing from the data, the validator shouldn't produce an error, but it doesn't find that out until the third line. In dictionary style you don't have this problem, because there the validator receives the entire schema at once. This seems like a minor issue to me.

In both styles, we can make nested fields a bit easier to deal with.

```python
validator.required('accommodation', type='object')
validator.required('.name', type='string')
validator.optional('accommodation.geo', type='object')
validator.required('.longitude', type='string', regex=number_pattern)
validator.required('.latitude', type='string', regex=number_pattern)
validator.optional('accommodation.images', type='list of object')
validator.optional('.size', type='number', minimum=0)
validator.optional('.url', type='string', regex=url_pattern)
```

```python
schema = {
    'metadata': { required=True, type='object' },
    '.accommodation_id': { required=True, type='number', minimum=1 },
    'accommodation': { required=True, type='object' },
    '.name': { required=True, type='string' },
    'accommodation.geo': { required=False, type='object' },
    '.longitude': { required=True, type='string', regex=number_pattern },
    '.latitude': { required=True, type='string', regex=number_pattern },
    'accommodation.images': { required=False, type='list of object' },
    '.size': { required=False, type='number', minimum=0 },
    '.url': { required=True, type='string', regex=url_pattern }
}
```

Let's see what happens if we have a schema that requires a bit more flexibility.

field                      | type   | required | remarks
---------------------------|--------|----------|---------
`accommodation`            | object | yes      |
`accommodation.type`       | string | yes      | Either `hotel` or `alternative`.
`accommodation.name`       | string | yes      |
`accommodation.unit_count` | int    |          | Required when type is `alternative`, not allowed when type is `hotel`.

In function call style:

```python
def schema(validator):
    validator.required('accommodation', type='object')
    validator.required('accommodation.type', type='string', options=['hotel', 'alternative'])
    validator.required('accommodation.name', type='string')

    if validator.document.type == 'alternative':
        validator.required('unit_count', type='int', minimum=0)
    else:
        validator.disallowed('unit_count')
```

In dictionary style:

```python
def schema(validator):
    schema = {
        'accommodation': { required=True, type='object' },
        'accommodation.type': { required=True, type='string', options=['hotel', 'alternative']},
        'accommodation.name': { required=True, type='string' }
    }

    if validator.document.type == 'alternative':
        schema = {
            **schema,
            'accommodation.unit_count': { required=True, type='int', minimum=0 }
        }
    else:
        schema = {
            **schema,
            'accommodation.unit_count': { disallowed=True }
        }

    validator.apply(schema)
```

Function call style looks cleaner to me in this scenario. Actually, these examples aren't entirely correct. What if validation of `accommodation.type` fails?

```python
def schema(validator):
    validator.required('accommodation', type='object')
    validator.required('accommodation.name', type='string')

    if validator.required('accommodation.type', type='string', options=['hotel', 'alternative']):
        if validator.document.type == 'alternative':
            validator.required('unit_count', type='int', minimum=0)
        else:
            validator.disallowed('unit_count')
```

```python
def schema(validator):
    schema = {
        'accommodation': { required=True, type='object' },
        'accommodation.type': { required=True, type='string', options=['hotel', 'alternative']},
        'accommodation.name': { required=True, type='string' }
    }
    validator.apply(schema)

    if validator.is_valid('accommodation.type'):
        if validator.document.type == 'alternative':
            schema = { 'accommodation.unit_count': { required=True, type='int', minimum=0 } }
        else:
            schema = { 'accommodation.unit_count': { disallowed=True } }
        validator.apply(schema)
```

This, too, looks better to me in function call style. Also, it's just too easy to forget to call `apply()`. I also like that function call style looks like code. If you want to define a schema as data, you might as well do it in YAML or something. However, that's not flexible enough to deal with a situation like the one above.

Okay, function call style wins by a nose.

## Error reporting

There are two challenges when it comes to reporting errors.

* How do you report exactly where the error occurred?
* How do you show the errors in a helpful way?

Keep in mind that we may be validating many thousands of documents at once.

### Error location

Suppose we are processing a file in JSON Lines format, containing many documents. Letting the user know which document a message is referring to, is a simple matter of recording the line number.

line | message
-----|--------
   3 | missing field `id`
  18 | value for `hour` is out of range; must be 0 <= hour < 24

This works for line-based formats like JSON Lines and CSV, but not so much for binary formats like Avro. Probably the best thing you can do in that case, is to report the document number, assuming documents are at least stored in sequential order. This works out nicely for line-based formats as well. I have no clue what to do about column-based formats, so I'll just pretend they don't exist.

For line-based formats, it's more intuitive to start counting documents starting at one instead of zero, since that is how text editors do it. Maybe it's more intuitive for other formats to start at zero. We can choose one option for all file formats are do whatever makes most sense for the format. Let's use one-based counting as the default and only use zero-based counting for a file format if there's a very good reason.

document number | message
----------------|--------
  3             | missing field `id`
 18             | value for `hour` is out of range; must be 0 <= hour < 24

If we want to allow validation of multiple files at once, we should also add the file name.

file           | document number | message
---------------|-----------------|--------
./yesterday.jl |               3 | missing field `id`
./today.jl     |              18 | value for `hour` is out of range; must be 0 <= hour < 24

Of course, this only works if the data is stored in files. If you want to validate data in, for example, DynamoDB tables, you need to use the table names instead.

Reporting where in the document an error occurs can't be done by counting characters. It would work for a text-based format like JSON, but it would be useless for a binary format like Avro. I think using the full field names is the best we can do. If we have to report on a list element, we can add the index.

file           | document number | field         | message
---------------|-----------------|---------------|--------
./yesterday.jl |               3 | id            | missing field
./today.jl     |              18 | hour          | out of range; must be 0 <= hour < 24
./today.jl     |              22 | images[4].url | must be of type string

### Showing errors

When you are validating many documents that were all generated by the same process, chances are that some errors occur in all documents. This can make the output a bit unwieldy.

```
./yesterday.jl:1:id  missing field
./yesterday.jl:1:hour  out of range
./yesterday.jl:2:id  missing field
./yesterday.jl:3:id  missing field
./yesterday.jl:3:hour  out of range
./yesterday.jl:3:images[4].url  must be of type string
./yesterday.jl:4:id  missing field
```

Not repeating the file name and document number may already make this a bit easier to read.

```
./yesterday.jl:1
    id  missing field
    hour  out of range
./yesterday.jl:2
    id  missing field
./yesterday.jl:3
    id  missing field
    hour  out of range
    images[4].url  must be of type string
./yesterday.jl:4
    id  missing field
```

If you have a lot of recurring messages, grouping by message might be better.

```
id  missing field
    all documents
hour  out of range
    ./yesterday.jl:1
    ./yesterday.jl:3
images[4].url  must be of type string
    ./yesterday.jl:3
```

The most convenient format probably depends on the user's use case, so the most important takeaway for now is that formatting and grouping of the messages should be flexible.

You could keep the entire document in memory so that you can show it and highlight any validation errors, but if you're validating a lot of documents, it would require a huge amount of memory. Of course, if you display messages as soon as they occur, it wouldn't be a problem (because you don't need to keep the messages and documents in memory), but then you would lose the possibility to group by message. There's also the question of how to keep the document in memory: in it's original format? How would that work for Avro? Or would you keep it as a Python dictionary and let the reporter handle the conversion? This seems like more trouble than it's worth. If you want to see the validation error in context, you will just have to open the file or data store manually. If this is too much hassle, we'll have to write a separate tool that can make it easier.

## Data sources

The validator shouldn't care where the data comes from. This means two things:

* It shouldn't matter where the data is stored (file system, S3, DynamoDB, etc.).
* It shouldn't matter in what format the data is stored (JSON, Avro, CSV, etc.).

Potentially, the amount of documents you want to validate is huge, so reading them all into memory is not a viable strategy. This means that the validator should assume that it will receive documents one-by-one and not all at once.

In order to deal with multiple formats, we need to convert any input format to an intermediate format that the validator can use. The obvious intermediate format here is a Python dictionary.

## Data sinks

It occurs to me that for large datasets, you may want more than just a report of validation errors. If you're processing 10 GB of data, you don't want to read it in once to do validation and then for a second time to filter out the invalid documents. It would be much more convenient if you can direct documents somewhere. Write valid documents to this S3 bucket, write invalid documents to this SQS queue, write logs to Cloudwatch; something like that. If we're already streaming in documents, we might as well also stream them out.

All of this should be separate from the validator proper, of course. There should be a coordinator that you can initialize with some data sources and some data sinks.

## Parallel processing

Given that we may want to run the validator on an a huge set of documents, it would be nice if we could run the validator on subsets in parallel. This adds some requirements.

* The data source reader needs to be able to read subsets.
* We need some way to determine what the subsets should be.
* We need to be able to combine the validation results of the subsets.

I don't want to spend a lot of time at this point on making parallel processing work. As long as the validator doesn't care where its input comes from, it should be possible to add parallelism later by extending the data source readers and the error reporter.

## Default behavior

### Extra fields

When a document contains fields that don't occur in the schema, the validator can do one of two things: ignore the fields or report the fields. The schema author should be able to choose either. The question is, though, what is the default?

If we silently accept extra fields by default, the schema author may never find out that he forgot to turn on reporting for extra fields. However, if we report on extra fields by default, the first test with an extra field will alert the author to the fact that he needs to turn reporting for extra fields off. So, reporting by default is the safer option.

### Nested fields

Suppose you have a schema that says `accommodation.geo.latitude` is required. What should happen if the field is missing? Well, that depends.

```json
{
    "accommodation": {
        "geo": {}
    }
}
```

This is the simple case: validation should fail with a message that `accommodation.geo.latitude` is missing.

```json
{
    "accommodation": {}
}
```

The answer to this case is less obvious: it should pass validation. The reason is that `accommodation.geo` may be optional, in which case it's fine that `accommodation.geo.latitude` is missing. And if `accommodation.geo` is required, it will result in an error message, making a message for `accommodation.geo.latitude` redundant.

To belabor the point, suppose you have the following schema.

```python
validator.optional('accommodation.geo')
validator.required('accommodation.geo.latitude')
```

This means that `accommodation.geo` is optional, but if it does exist, it must have a `latitude`. This would be impossible to express if the second rule in the schema automatically made `accommodation.geo` required.

Note that in the schema above, the first rule doesn't do anything; leave it out and the schema is the same. You would only include it if you want to do additional validation on the field, like checking its type.

```python
validator.optional('accommodation.geo', type='object')
validator.required('accommodation.geo.latitude')
```

Actually, this should also be unnecessary, because the second rule already implies that `accommodation.geo` is an object. I can't come up with a scenario where you would want to explicitly mark the parent as optional if you already have a rule for its child. Still, the option should be there in case someone comes up with a sensible custom validation that I can't think of right now.

Another implicit effect of having a rule for a nested field, should be that all parents are considered expected fields. If your only validation rule is that `accommodation.geo.latitude` is required, you don't want to get messages that `accommodation` and `accommodation.geo` are extra fields.

Here's another interesting case regarding nested fields. Take a look at the following schema and document.

```python
validator.required('accommodation')
validator.required('accommodation.geo')
```

```json
{}
```

Clearly, validation will fail, but what should the output be. The first rule results in a message, because `accommodation` is missing, but what about the second rule? `accommodation.geo` is also missing, but what is the value in reporting that? To keep the output from cluttering up with loads of unnecessary messages, the validator shouldn't report on `accommodation.geo`: if the parent is required and missing, we can stop validating the children.

## Data types

Which data types should we support? JSON already has a defined set of data types, so we could just use those. On the other hand, Avro has a different set of data types, so why not prefer those? It's probably better to pick a set that's format agnostic: the data schema should apply regardless of how the data is represented.

Each data type will need it's own validation parameters. For example, numbers can have a minimum and a maximum, but those parameters make little sense for strings.

```python
validator.required('rating.aspect', type='string')
validator.required('rating.score', type='number', min=0, max=10)
```

Then there's the question of which data types to support. Do we want a generic number data type or will we make the distinction between integers and floating-point numbers? Should we have a separate data type for URLs or is it enough to have a string type with a regular expression? It's hard to get it right from the get-go, so it's useful if adding a new data type is relatively easy. When it comes to picking which data types to implement first, I think it makes sense to start with the generic and work towards the specific. For example, I'll implement the string type before the URL type, because you can validate URLs with the string type, but you can't validate strings with the URL type.

### Lists

Lists are a special case. They don't need a separate implementation; they can reuse their underlying data type. What I mean is: if you have a data type for strings, you don't need a separate data type for a list of strings; you just apply the validation for string to each element of the list. We do need a separate name, though. To me, the two obvious candidates are:

* `[string]`
* `list of string`

I prefer the latter. It's easier to miss the square brackets than to miss the prefix `list of`. Grammatically, it should be `list of strings`, but instead of dealing with the pains of pluralizations, I'll suppress my inner grammar purist.

Note that I'm assuming that lists or homogenous, i.e. all elements in the list are of the same type. My assumption is that this is by far the more common case, so for now, I'm not even going to consider elements of differing data types. If we want to support heterogeneous lists in the future, they'll need a different name, e.g. `collection`.

Even if we limit ourselves to homogeneous lists, there are three variations and they require different ways of specifying validation parameters.

* lists of objects
* lists of scalars
* lists of lists

Lists of objects are easiest to define. Suppose we want to validate something like the following.

```json
{
    "ratings": [{
        "aspect": "cleanliness",
        "score": 8.6
    }, {
        "aspect": "staff",
        "score": 7.2
    }]
}
```

The validation rules would look like this.

```python
validator.required('ratings', type='list of object')
validator.required('ratings[].aspect', type='string')
validator.required('ratings[].score', type='number', min=0, max=10)
```

Note the suffix `[]` for the nested fields. Without it, the validator wouldn't know whether to complain about the fact that `ratings` is not an object, or to just process the list. It's possible to let the validator automatically pick the one it sees in the data. If you want to explicitly state `ratings` is a list, you can do so on separate line (and this is what the above example does). I like the square brackets though, because then there is no room for doubt, even when the rule for `ratings` is missing.

Lists of scalars present a slight problem. Suppose we want to validate something like the following.

```json
{
    "scores": [ 8.6, 7.2 ]
}
```

Where do we put the validation parameters? We could put them on the validation rule for the list.

```python
validator.required('scores', type='list of number', min=0, max=10)
```

This example would mean that each number in the list must be between 0 and 10 (both inclusive). Technically, that's incorrect, because the minimum and maximum don't really apply to `scores`, but they apply to the elements inside `scores`. This may not even be a mere technicality. Suppose we want a way to validate that a list has a minimum number of elements and a maximum number of elements. `min` and `max` would be nice names for those validation parameters. Now we have a conflict. Of course, we could change the names to `min_length` and `max_length`, but sooner or later, you are going to run into another conflict. On top of that, it's now unclear what any given validation parameters applies to: the list or the elements? So, let's try another option.

```python
validator.required('scores', type='list of number', min=1, elements={ min=0, max=10 })
```

It gets rid of the ambiguity, so there's no more conflicts. It's a bit verbose, though. Especially considering that validation parameters for elements will probably be more common than validation parameters for lists. What if we change the default?

```python
validator.required('scores', type='list of number', min=0, max=10, list={ min=1 })
```

That works, but it doesn't sit well with me; technically, it makes more sense if the default applies to the list. Practically, it doesn't though. Let's consider one more alternative.

```python
validator.required('scores', type='list of number', min=1)
validator.required('scores[]', type='number', min=0, max=10)
```

It requires an extra line, but it's unambiguous and technically correct. It's also an extra reason to use square brackets. `scores[]` now means: an element in the list `scores`. Interestingly enough, with this option, if you don't have validation parameters for the list, you don't need to validate the list itself. The following is perfectly clear.

```python
validator.required('scores[]', type='number', min=0, max=10)
```

As stated before, I expect this to be the more common case, so the extra line might not be a big deal. There is another potential problem, though.

```python
validator.required('scores', type='list of number', min=1)
validator.optional('scores[]', type='number', min=0, max=10)
```

Once the list is defined as required, it makes little sense to make the elements optional. The same goes for the inverse: if the list is optional, making the elements required has no meaning. In other words, optional or required always refers to the list, not to its elements. So, what do we do if there's a conflict? I guess we can treat the list as required – as that is the safest option – and issue a warning.

There is still an issue with the validation rule for lists. Let's take another look.

```python
validator.required('scores', type='list of number')
```

The validator can check that `scores` is a list, but what is it supposed to do with the elements? It can't really validate them, because it doesn't have the validation parameters. Perhaps, it can validate only the type of the elements, but if we then add a validation rule for the elements, the validator might report type errors in the elements twice. We might as well leave out the element type from the validation rule for lists altogether.

```python
validator.required('scores', type='list')
validator.required('scores[]', type='number')
```

You only need the first validation rule if you want to specify validation parameters that apply to the list. Again, I suspect that's an uncommon case.

I like the last syntax best, despite the possible required/optional conflict. It's unambiguous, it's technically correct. It makes the most sense, in my opinion.

I didn't think lists of lists all the way through yet, but I'm hoping that just implementing it recursively magically solves the issue. With the syntax I chose for lists, I do expect this to be the case. We'll see.

### Multiple types

What if the type of a field is not restricted to one option? For example, say that a rating can either be a string, like `excellent`, or a score.

```python
validator.required('rating', type='string/number')
```

This is neat, but it doesn't allow us to specify validation parameters, because we wouldn't know which type they'd belong to.

```python
validator.required('rating', type='string/number',
    string={ options=['poor', 'good', 'excellent'] },
    number={ min=0, max=10 })
```

Ugh. This is just unwieldy. I don't even want to think about what happens when lists get involved. Let's try something else.

```python
validator.required('rating', type='string', options=['poor', 'good', 'excellent'])
validator.required('rating', type='number', min=0, max=10)
```

So, in this case, having multiple validation rules for the same field would mean that only one of those rules needs to apply for the validation to succeed. It's clean, but I'm a bit worried about the fact that we can't flag accidental duplicate rules any more. What if we make it explicit?

```python
validator.possible('rating', type='string', options=['poor', 'good', 'excellent'])
validator.possible('rating', type='number', min=0, max=10)
```

Not bad, but how do we indicate whether the field is required or optional? Maybe we can make that explicit as well.

```python
validator.required('rating')
validator.possible('rating', type='string', options=['poor', 'good', 'excellent'])
validator.possible('rating', type='number', min=0, max=10)
```

That might just work. Of course, if you specify a type for the required-rule, then subsequent possible-rules will be ignored and result in a warning.

Coincidentally, this may make heterogeneous lists easier.

```python
validator.possible('ratings[]', type='string')
validator.possible('ratings[]', type='number')
```

I'm not sure it works for lists of objects, though.

```python
validator.possible('ratings[]', type='number')
validator.possible('ratings[]', type='object')
validator.required('ratings[].aspect', type='string')
validator.required('ratings[].score', type='number')
```

Would that work?

## Data formats

### Readers and stores

[As mentioned previously](#data-sources), there's a distinction between where the data is stored and in what format the data is stored, so we need separate components for both. I'll call a component that deals with the format a reader, and a component that deals with where data is stored a store. There's a relationship between readers and stores that warrants a bit of exploration.

The responsibility of a reader is to convert JSON, Avro, CSV, or whatever into a Python dictionary. There's a reader for each file format. The reader doesn't really need to know where the data comes from, so it calls a store to take care of that. This way, you only need one JSON reader (for example), but you can still read JSON files from the file system, or S3, or from an HTTP API. The opposite is also true: if you have an S3 store, it works for JSON, Avro, CSV, etc.

The first complication comes with the distinction between binary data and text data. Typically, a store doesn't know which of the two it's dealing with. Presumably, the reader does know what to expect, so it's best if a store always provides bytes and the reader is responsible for converting it to text if necessary. This leaves the question of how to determine the encoding the text is using. Is it even possible to detect text encoding reliably? If it is, every reader dealing with text needs to do it, so it should be a shared utility. For now, let's keep it simple and assume UTF-8. Some file formats, like Avro, are available in both a text and a binary format. It's up to the reader to determine which one it received from the store and act accordingly. I'm going to assume that's easy enough to do.

Another question is what to do with zipped data. It would be nice if we can handle zipped data transparently. It's easy enough to pipe bytes through an unzip stream. Question is, which component is responsible for detecting the data is zipped: the reader, the store, or a separate component. You could have the unzip stream detect if the data is zipped, if so unzip it, if not just pass it on; you would simply always wrap a store's output in the unzip stream. Another option is to do the detection in the store and only wrap the output in an unzip stream if necessary. Doing the detection in the reader is equally viable, but it feels more like a store issue than a reader issue to me. Letting the unzip stream handle it, seems to be the nicest separation of concerns.

Then there's the question of validating multiple files. It would be nice, for example, if you could validate all files in a folder. Will the store put all the files into the same byte stream? It probably needs to pass the file name to the reader for error reporting, so how do you do that? I guess a store should be able to return multiple byte streams and associate a name with each of them.

### Detecting the data format

It would be nice to be able to detect the data format. Doing it by file extension is cumbersome, because then you need to pass a file name around and not all stores are file based. It's also not very reliable. It's much better to detect the data format from the contents of the file. I suspect that in most cases, you can make a pretty informed guess from the first few bytes, the first line at most. This means that stores should implement a peek method, that returns the requested number of bytes without moving the stream forward, i.e. if you read after a peek (or peek again) you get the same bytes that the peek returned. This is necessary, because the reader needs to consume the same first bytes that the format detector used.

There might be cases where the exact data format is hard to detect from just the contents. For example, text-based Avro is based on JSON, so it's hard to distinguish between text-based Avro and pure JSON. In such a case, the file extension can be a valuable hint, so it's useful to pass the file name and extension, if available, to the format detector.

### Non-stream-based stores

DynamoDB presents an interesting case: is it a store or a reader? In a way it's both: it's where data is stored, but it also uses its own format. I know it's based on JSON, but you can't just convert it straight away, because of all the type information DynamoDB puts in there. You could implement a DynamoDB store and a DynamoDB reader that always work together. Is that overkill? You can also implement everything in the reader. (You can't put everything in the store, because the code that will feed documents to the validator will rely on the interface of the reader, not the interface of the store.)

Are there other cases like DynamoDB? What if you want to validate data that's stored in a MySQL database? (Relational databases have their own schema of course, but the validator potentially validates much more.) It doesn't make too much sense to output a byte stream from MySQL, because database cursors usually work record based. You can turn the records into byte streams and then have the reader turn them into records again, but that seems unnecessary. The same goes for DynamoDB. It might be best to implement all of it in the reader. Or allow different interfaces for different data stores, but that makes them less interchangeable. On the other hand, they're not interchangeable in any case, because passing a DynamoDB store to a CSV reader doesn't make much sense anyway. Alright, let's just say that stores always have an interface that provides a byte stream and that cases where store and format are tightly coupled, they are implemented as a reader only.

### Error handling

What to do when reading from the data source fails? I guess if there's a problem with the store, you can't do much but raise an exception: if the bytes aren't there, the bytes aren't there. But what about problems in the reader? What if one document in a JSON Lines file is not well-formatted, or a record in a CSV file doesn't have enough fields? It would be nice to report these issues as a validation error instead of aborting the process, because you might already be many documents in and you don't what to rerun validation on a multi-gigabyte file just because someone forgot to escape a comma.

It might make it hard to report the [error location](#error-location), though. What if someone puts an actual new line instead of a `\n` into a line-based format like JSON Lines or CSV? The basic assumption is that document number equals line number. Well, that would still hold, so no problem there. It does make it very clear that the reader should be responsible for the document number. In non-line-based formats, like binary Avro, things get more complicated. I guess the way to deal with it is file format specific. Let's make this the responsibility of the reader and hope for the best.

Another potential aspect of the error location, is the file name. The reader may be responsible for the error location, but the file name is something it needs to get from the store and then pass on.

## Connecting sources and sinks

We can't just sink documents using the exact same bytes that were provided by the data source. First of all, because the validator doesn't receive the bytes, just the document, and second because this doesn't work for all file formats. For example, it would work for JSON Lines, but not for regular JSON, because that would need to be a list with brackets and commas, and CSV and Avro require headers. On top of that, you might want to output the document in a different format than it came in, so it would make sense to make a split between sinks (where you write it) and writers (in which format you write it), just as with sources and readers.

The [document numbers](#error-location) in the error report won't match with what's written to the sink. We could add extra information to the error report with an extra document number. That would work for file-based systems, but what about something like SQS or Kinesis? Maybe every sink should figure this out for itself and for some sinks it just doesn't make sense. That's not very satisfying. If you write invalid documents to SQS, you want to be able to figure out what's wrong with them. Should we add a unique identifier to each document? But then we are changing the data. Although, SQS does have the option to add metadata to a message. I guess making it sink-specific is the best way to go. It may also be possible to indicate a field in the document as a unique identifier, especially since the validator (hopefully) already made sure the field exists. That may not work in all situations, though, but when it does, it can be very handy. So handy, in fact, that we may want to add it to the output of the validator proper, not just to the sink.

When data comes from multiple stores, e.g. multiple files in S3, does it also need to be written to multiple stores? I guess, sometimes that's what you want and sometimes it isn't, so it should be configurable. Either you specify that you want to sink all documents to one location or you provide a map from input location to output location. Is the latter always possible? Say that the input comes from the file system and is determined by a glob pattern: you don't know the exact file names beforehand. Now you want to write the output to SQS with a different queue for each file. You would need to provide a mapping function to do the conversion from file name to queue name. It's possible. A bug in the mapping function would lead to a lot of failed writes.

## Sinking a collection of documents

I'm wondering what to do about collecting documents. Suppose we want to output JSON (not JSON Lines). If you write everything to a single file, it's easy: you start with a `[`, put a comma after every document but the last, and end with a `]`. But what if you write to SQS? As far as the writer is concerned, it's the same thing, but with SQS you would typically write every document to the queue on it's own, so you don't want all the documents to be formatted as a big list. The writer doesn't know this, so this means that the sink needs to call the writer, which is different with input, because there the reader calls the source. The writer needs to return the correct bytes for every document, so the sink can stream it out efficiently. So for JSON it would need to include the `[` for the first document and a comma for every subsequent document. Worst case scenario, the writer has to buffer all the documents before they can be written, but from the top of my head, I can't think of a data format where this is necessary.

## Multiple sources, multiple sinks

[I mentioned this before](#connecting-sources-and-sinks): when data comes from multiple stores, e.g. multiple files in S3, does it also need to be written to multiple stores? I want to think this through some more.

Let's first consider the possible scenarios. The simplest one is where you want to write all output to a single place, no matter where it came from. For example, all invalid documents should end up in a single file in S3. The next scenario is when there is a one-to-one mapping between the original store and the output location. For example, the input comes from several files in S3 and for each file there's an SQS queue that collects the invalid documents. The final scenario is where there isn't an obvious mapping, but you still want multiple output stores, for example when you want to limit each output file to 500 documents.

Regardless of the scenario, you can solve the mapping in two place: inside the sink, or in the code that ties all the components (source, validator, sink) together. I'll call the second one a controller. I would prefer to solve the mapping in the sink, because it feels like it belongs there and it I think it would aid reusability, but I'm a bit worried that code for complex mapping scenarios becomes unwieldy. Let's try.

First, here's an example of a controller.

```python
source = FileSystemSource('documents/2019-05/')
reader = JSONLinesReader(source)

writer = JSONLinesWriter()
invalid_documents_sink = FileSystemSink(writer, 'invalid.json')

validator = Validator(schema)
for document in reader.documents():
    if not validator.validate(document):
        invalid_documents_sink.add(document)
```

This controller reads from multiple stores (all the files in the folder `documents/2019-05/`) and writes to a single store (the file `invalid.json`), so this is the first scenario. There's no mapping here.

Let's take the second scenario and make the sink responsible for the mapping. We need to pass the sink some kind of mapping function instead of an explicit name. Other than that, it's the same as the previous controller.

```python
def store_mapper(input_name):
    return os.path.basename(input_name)

source = FileSystemSource('documents/2019-05/')
reader = JSONLinesReader(source)

writer = JSONLinesWriter()
invalid_documents_sink = FileSystemSink(writer, store_mapper)

validator = Validator(schema)
for document in reader.documents():
    if not validator.validate(document):
        invalid_documents_sink.add(document)
```

This example takes the input file name, strips it of directory information and uses that as the output file name. Making the controller responsible for the mapping moves the mapping code a bit, but isn't too different.

```python
source = FileSystemSource('documents/2019-05/')
reader = JSONLinesReader(source)

writer = JSONLinesWriter()
invalid_documents_sink = FileSystemSink(writer, store_mapper)

validator = Validator(schema)
for document in reader.documents():
    if not validator.validate(document):
        output_name = document.store_name.rsplit('/', 1)[1]
        invalid_documents_sink.add(document, output_name)
```

So, what about mappings that aren't one-to-one? Can we solve that with a mapping function, too?

```python
document_count = 0
store_count = 0
def store_mapper(input_name):
    document_count += 1
    if document_count >= 500:
        store_count += 1
        document_count = 0
    return f'invalid_{store_count}.json'

source = FileSystemSource('documents/2019-05/')
reader = JSONLinesReader(source)

writer = JSONLinesWriter()
invalid_documents_sink = FileSystemSink(writer, store_mapper)

validator = Validator(schema)
for document in reader.documents():
    if not validator.validate(document):
        invalid_documents_sink.add(document)
```

Well, that's not too bad, actually. In fact, I like it, because this way, we can write a couple of common mappers that you can reuse. If it turns out there are scenarios where a mapper function isn't flexible enough, we can still add a store name parameter to `sink.add()` to give the option to solve it in the controller, but right now, it seems that won't be necessary.

## Non-validation errors

How should we report errors that don't result from validation? For example, what if the file we're trying to validate is corrupted? Python's default error handling mechanism is exception handling, but exceptions tend to abort the running function and that may not be what we want. For example, if one line in a CSV file contains too few commas, we don't want to stop processing the entire file. How do we set that up if we use exceptions? Also, we still want to report a problem like that, so how do we do that? Python's default for this is it's logging system, but now we have some errors that end up in the logs and some errors that end up in the validation report. Is it possible to combine the two? Let's run through a few examples and see where we end up.

Suppose we try to validate a file format that's unknown to the validator. In that case, there is nothing we can do and it's okay to just abort, so raising an exception would be fine. Except, of course, if we are trying to validate multiple files and only one of them is in an unknown format. In that case, you would just want to skip that one file, report it, and continue with the rest. You can't include this problem in the validation report, because the validation report is document-based and you have no documents here; it's a different class of error. I see no problem with using Python's logging system for this, so let's go with that for now.

Suppose you're reading JSON Lines, but one of the lines isn't valid JSON. Since every line is a document in JSON Lines, you could report this as a problem with a specific document. It also feels like a validation error. Only catch is that this problem doesn't crop up in the validator, it crops up in the [data reader](#readers-and-stores) (the component that translates the data into Python dictionaries). We can give the reader access to the validation report so it can add these kind of errors. The downside is that we're turning the validation report into some global error collection system instead of just the output of the validator. We might as well use Python's logging system then, which is already a global error collection system, but that has downsides which I'll explore in a moment. We could let the reader pass on the error to the validator so the validator can add it to the report. That's weird, to give someone else your problem, even though you know they can't do anything with it. Not sure yet.

Suppose validation went fine and you want to write all valid documents to a [data sink](#data-sinks), but something goes wrong there, say the network is down. You can report this problem per document, since documents are fed to the sink one by one, but in case of a persistent error, you end up with the same error message a lot of times. Also, this doesn't feel like a validation error, it feels like a system's error, so I wouldn't go for adding it to the validation report. Exception, then? Probably, but one we would log and ignore, because you don't want the validation to stop. Well, that depends a bit. If you can't sink your valid documents, you're entire pipeline will stall, so unless the validation report is valuable to you on its own, there's no value in continuing. Of course, the problem may not be permanent and then only a few documents are dropped; that may actually be even worse. Fixing that requires the validation process to be atomic and I'm not going there. (It does give me the idea of sending a signal somewhere, for example SQS, once validation has completed. Later.) If you can't sink your invalid documents, that shouldn't be a showstopper. So? Log it and continue, I say.

Suppose there's a bug in the validator. When dealing with lists, it tries to read an element that isn't there. This will automatically result in an exception. These situations should be rare, so it would be nice if we can just report them and continue with the next document. That does require that we catch the exception, though. We should also log it, but where? In the case of a bug in the validator proper, I do think it makes sense to put it in the validation report, since we are in the context of processing a document. What I don't know, is whether the document should count as valid or invalid; maybe it needs its own class. If the exception occurs in the reader, we're also in the context of processing a document, so I'd say the reader raises an exception, and the validator catches it and adds it to the validation report. I guess this would also cover the previously mentioned example of an invalid line of JSON in a JSON Lines file. If something goes wrong in a data sink, we're talking about the scenario described in the previous paragraph, I would say. Regardless of whether the error ends up in the validation report, a bug should always go to the log, because that's where you expect to find it if you're debugging the system; you don't want to rerun a validation job just to get error messages related to bugs.

So, should we just write all errors – validation and otherwise – to the log and be done with it? I like the simplicity of using a single model. I also like the idea of using the default system, but I don't think it fits perfectly. Python's logging works well for string messages, but it requires a bit of wrangling if we want to log more complex records. It can handle it, but it's an advanced use case and I'm a bit worried it might confuse users of the validator. It's not a dealbreaker, though. If we take some care, users may not notice a thing. If we use Python's logging system, it does mean that our messages will be mixed with the messages produced by other code, like the libraries we use or the code the user wrote. This shouldn't be too much of a problem, since Python has the concept of loggers. We can just create a logger specifically for our own messages. If we want to sink our error report, we now need to extract it from the logging system. Python does allow you to write your logs to a file and you can write custom handlers to send it to other places, too. Again, it requires some wrangling, but the functionality is there.

It seems like Python's logging system gives us all we need, but I'm still not convinced we should use it for everything. What it comes down to, is that we have two types of errors: system errors and validation errors. System errors should use the default logging system, but I think validation errors should be regular output of the validator; that's its entire purpose. I'll go with this rule of thumb: if an error is related to processing a document, it goes in the validation report, if it isn't, it goes to the log.

## Splitting the library

Thinking about the combined problem of I/O and error reporting is blocking my progress, so it's time to simplify. What is I/O doing in a validator library anyway? I think I should split things: one library for validation, one library for I/O; much cleaner. Ah, just thinking about it is a relieve!

So, does that solve the error reporting issue? Not really, but let's only consider error reporting in the context of the validator proper. The validator returns validation messages. Done!

But what if there's a document-related problem during I/O, for example, one line in a JSON Lines file is invalid? That would result in an exception, one that a controller should catch and add to the list of validation messages.

Which brings up the issue of the controller. Where do we put that? It depends on both the validator and the I/O library. Should it be yet another library? That feels a bit superfluous, since the controller on its own can't do anything. Is it part of the validator library? Functionality-wise, that's where it fits best, but it would mean that the entire validation library now has a dependency on the I/O library. What if we just leave it out and make the user responsible for writing the controller? Downside of that is that the code is both repetitive and error-prone, so providing a default controller would be really beneficial.

What if we make the three parts (validator, I/O, controller) separate packages within the same library? The I/O library is valuable on its own and it would be strange if your project gains a validator you don't need just because you import an I/O library.

These are all the options I see and none of them is ideal. I'm torn between three separate libraries and combining the validator and the controller. How often would someone want to use the validator without any kind of I/O? Documents would already have to be in memory and Python dictionaries, so I suppose not that often. How often would someone want to use the validator with a different I/O library? That's a bit more likely. I mean, the validator is designed to be completely independent from I/O, so why undo that by giving the validator package a dependency on a specific I/O library? Okay, three libraries it is.

## Redesign

Now that I've decided to remove the sources and the sinks, and the readers and the writers from the library, it's a good time to reevaluate the design of the validator library.

### Syntax improvements

I'm still happy with the syntax. The only improvement I'd like to make, is to get rid off the need to repeat `validator.` all the time. I've known since the start how to do that; I just haven't written in down yet. We can solve the problem by wrapping the schema in a class that forwards calls to `required` and `optional` to the validator. It will turn a schema like this:

```python
def schema(validator):
    validator.required('metadata', type='object')
    validator.required('metadata.accommodation_id', type='int', minimum=1)
    validator.required('accommodation', type='object')
    validator.required('accommodation.name', type='string')

```

into a schema like this:

```python
class AccommodationSchema(validator.Schema):
    def definition():
        required('metadata', type='object')
        required('metadata.accommodation_id', type='int', minimum=1)
        required('accommodation', type='object')
        required('accommodation.name', type='string')
```

The first option will still be valid; the `Schema`-class is just there for convenience.

### Validation messages

Despite all the thought I put into making sure documents don't need to stay in memory, I always assumed that you would be able to keep all validation messages in memory, but if you are validating a lot of documents, that's not guaranteed at all. So, we need a mechanism to sink each validation message as soon as the validator produces it. I guess that means we need to inject a message sink into the validator. Unless...

The validator operates on one document at a time. The only state it keeps, is a collection of validation messages. What if we push that to the controller? The controller needs access to the validation messages anyway, because it needs to add validation messages for some I/O errors. That would mean that the validator can simply return a list of validation messages. I like that.

It would be useful if the validator can accept some values that it adds to every validation message. Say that you want to add the name of the file that the document came from to each validation message. The validator knows nothing about files, so you need to pass it in.

### Validator interface

With all this in mind, let's rethink the interface of the validator. Since the validator doesn't need to keep state anymore, there's no need for it to be a class. I guess I'd better give an example of what the validator used to look like, so in the future it's still clear what has changed.

Let's assume we have a document, say, something like this.

```python
document = {
    'accommodation': {
        'name': 'Hotel New Hampshire'
    }
}
```

Right now (or by the time you're reading this: in the past) this is how you run a validator:

```python
from validator import Validator

def schema(validator):
    validator.required('accommodation', type='object')
    validator.required('accommodation.name', type='string')

validator = Validator(schema)
if not validator.validate(document):
    for message in validator.messages:
        print(message.type, message.field)
```

After I get rid off the `Validator` class, it would be like this:

```python
from validator import validate

def schema(validator):
    validator.required('accommodation', type='object')
    validator.required('accommodation.name', type='string')

validation_messages = validate(schema, document):
for message in validation_messages:
    print(message.type, message.field)
```

A minor change, but it is a bit cleaner. It also sidesteps the issue that the `Validator` class isn't just the validator, but also the thing that kickstarts the validator, so I don't have to worry about that anymore.

Most people will probably use the `Schema` helper class, in which case, the code looks like this:

```python
from validator import Schema

class AccommodationSchema(Schema):
    def definition():
        required('accommodation', type='object')
        required('accommodation.name', type='string')

validation_messages = validate(AccommodationSchema, document):
for message in validation_messages:
    print(message.type, message.field)
```

That is neat, because `validate()` doesn't even need to know if the schema is a function or a class, but the downside is that the schema class is instantiated for every document. I'm not sure if that has a significant performance impact – I should measure – but let's engage in some premature optimization. What I'm looking for, is something like this:

```python
from validator import Schema

class AccommodationSchema(Schema):
    def definition():
        required('accommodation', type='object')
        required('accommodation.name', type='string')

schema = AccommodationSchema()
validation_messages = schema.validate(document)
for message in validation_messages:
    print(message.type, message.field)
```

Can we implement this? I think so. In order to follow along, you first need to know how I intend to implement `Schema` without this functionality. It will look something like this:

```python
class Schema:
    def __init__(self, validator):
        self._validator = validator
        self.check()    # implemented in derived class

    def required(self, field_name, **kwargs):
        self._validator.required(field_name, **kwargs)

    def optional(self, field_name, **kwargs):
        self._validator.optional(field_name, **kwargs)
```

The validator the constructor receives is the same validator that would be passed if the schema was a function. The nice thing about this, is that `validate()` doesn't need to know whether it's calling a function or a constructor.

Now we want to replace the `validate()` function with a method on the `Schema` class. This is what the regular `validate()` function looks like:

```python
def validate(schema, document):
    _validator.document = document  # _validator is global to avoid repeated instantiation
    schema(validator)
```

The implementation of `Schema.validate()` wouldn't be all that different.

```python
class Schema:
    def validate(self, document):
        self._validator.document(document)
        self.check()
```

There are two related questions. First, where does `self._validator` come from? Second, how do you instatiante a schema? Right now, the constructor for `Schema` expects a validator, but we don't want to pass that in; we want `Schema` to take care of that for us. The solution is to make the constructor understand that it can be called in two different ways: by `validate()` as a normal schema, or by the user as a standalone schema.

```python
class Schema:
    def __init__(self, validator):
        if validator:
            self._validator = validator
            check()
        else:
            self._validator = _validator
```

It's a bit iffy to have one class that can behave in two different ways, but it is oh so convenient. And isn't that what a convenience class is all about?

## No Schema-class

My idea of [improving the syntax of a schema using a convenience class](#syntax-improvements) isn't going to work. I forgot that Python always requires explicit `self`. The upside of this is that it forced me to come up with another way to simplify the syntax and I can do that for the regular schema function by adding functions like `required()` and `optional()` to the schema functions globals. No more `Schema`-class necessary!

The only downside seems to be that my code environment now flags the validator functions as undefined and either I'm stuck with squiggly lines all over my schema, or I have to disable the warning outright. I'll accept this downside, because the schema code is joyfully simple right now.

No, I changed my mind: I can't live with the squiggly lines. Instead of adding the validator functions as globals to the schema function, I'll let the user import the functions into the global namespace, like so:

```python
from validator.schema import required, optional

def schema():
    required('accommodation')
    optional('accommodation.geo')
```

A schema definition should typically be in its own file, so the namespace pollution isn't much of a problem. Manually listing the functions is tedious, so I'll make `from validator.schema import *` work correctly.

## Library name

Until now, I just called the library _validator_. I don't like the name much. Not only is it unimaginative, but it can be confusing in conversation: when someone says _validator_, do they mean the component or the library? So, I wanted to change it. I considered _validation_. It's slighlty better in conversation, because people would refer to the library as _the validation library_. It's still miserably unimaginative, though. After a short brainstorm, I decided on the name _Okay_. Memorable, fitting, and easy to use.

## Parameterless schema functions

With the introduction of the [global validation functions](#no-schema-class) it's no longer necessary to pass a `Validator` object to a schema function. Originally, I wanted to keep both options available – so you could write either `def schema()` or `def schema(validator)` – but no one will use the latter, so why bother? Also, if it turns out that it is useful to have the document available in the schema function, the most natural thing to do is pass it as a parameter, but that's not possible if that parameter already contains the `Validator` object. Instead of changing the meaning of the parameter later on – which would be a breaking change – I decided to remove the parameter for now and keep the option open to add the document as optional parameter later.

## SchemaError

I decided to create a dedicated exception for reporting schema errors. A custom validator must return either a `Message` instance or `None`. If it doesn't, it contains a bug and I want to raise an exception for that. `TypeError` seemed the most fitting. I wrote a unit test for it, ran it, and it passed; that's not supposed to happen. Turns out, the validator chokes on the invalid return value from the custom validator – not surprisingly – and by coincidence it does so in a way that raises a `TypeError`. That's not good enough, though. I want to raise an exception on purpose, right where it happens, with a clear error message. I don't want a change in the validation error to lead to a different exception for the same problem. So, I started thinking: what if I create a separate exception for this?

It actually makes quite a bit of sense, because it allows you to easily report errors the schema writer made. It creates a clear distinction between problems with the document (validation message), problems with the schema (`SchemaError`), and problems with the code (any other type of exception). I guess this also means I need to get more strict with checking the schema for problems, like passing a validation parameter of the wrong type, or making a list optional and its elements required.

## Performance optimizations

After releasing _v1_, I decided to have some fun and try my hand at improving performance. I reimplemented the core algorithm three times – unit tests are amazing! – and ended up with a version that performs about twice as fast as the original. Unfortunately, I didn't bother to update the development log. Now, it's almost a year later, and of course I don't remember all the things I tried or why I tried them. That was stupid, but if I ever had any doubts whether keeping a development log is worth it, I don't anymore.

Currently, I have three open branches: `performance/indexing`, `performance/caching`, and `performance/preprocessing`. The last one is the winner, but I'll keep the other two around for reference. To check if I misremembered which one was fastest, I ran the performance test again. After I found the right script to run and figured out which lines to uncomment, that is. Anyway, I ran the same test on all four versions and here are the results.

version       | running time (lower is better)
--------------|-------------------------------
v1            | 28.5s
indexer       | 21.5s
caching       | 28.3s
preprocessing | 13.1s

Here's the script I used to obtain these numbers.

```python
import timeit
from okay import validate, Message
from okay.schema import *

def schema():
    def score(field, value):
        if not isinstance(value, dict) or 'score' not in value or 'out_of' not in value or not isinstance(value['score'], (int, float)) or not isinstance(value['out_of'], (int, float)):
            return

        if value['score'] > value['out_of']:
            return Message(
                type='score_too_high',
                field=field,
                expected=value['out_of']
            )

    required('metadata', type='object')
    required('metadata.accommodation_id', type='int', min=1)
    required('metadata.external_id', type='string')
    required('metadata.partner', type='string')
    required('metadata.source_type', type='string')
    required('accommodation', type='object')
    required('accommodation.name', type='string')
    required('accommodation.address', type='string')
    required('accommodation.city', type='string')
    required('accommodation.country', type='string')
    optional('accommodation.postal_code', type='string')
    optional('accommodation.phone', type='string', regex=r'[\+\- 0-9]+')
    optional('accommodation.checkin', type='object')
    required('accommodation.checkin.from', type='string', regex=r'[0-2]\d:[0-2]\d')
    required('accommodation.checkin.until', type='string', regex=r'[0-2]\d:[0-2]\d')
    optional('accommodation.checkout', type='object')
    required('accommodation.checkout.from', type='string', regex=r'[0-2]\d:[0-2]\d')
    required('accommodation.checkout.until', type='string', regex=r'[0-2]\d:[0-2]\d')
    optional('accommodation.geo', type='object')
    required('accommodation.geo.longitude', type='string', regex=r'\-?\d+\.\d+')
    required('accommodation.geo.latitude', type='string', regex=r'\-?\d+\.\d+')
    required('accommodation.ratings[].aspect', type='string', options=['general', 'cleanliness', 'staff'])
    required('accommodation.ratings[].score', type='number', min=0)
    required('accommodation.ratings[].out_of', type='number', min=0)
    optional('accommodation.ratings[]', type='custom', validator=score)


documents = \
    5000 * [{ "metadata": { "accommodation_id": 1, "external_id": "id1", "partner": "getaway", "source_type": "direct" }, "accommodation": { "name": "Heartbreak Hotel", "address": "Lonely Street", "city": "Memphis", "country": "United States", "postal_code": "37501", "phone": "+1 901-555-7300", "checkin": { "from": "15:00", "until": "23:00" }, "checkout": { "from": "00:00", "until": "12:00" }, "geo": { "longitude": "35.14", "latitude": "-90.038" }, "ratings": [{ "aspect": "general", "score": 2.5, "out_of": 5 }, { "aspect": "cleanliness", "score": 1.8, "out_of": 5 }, { "aspect": "staff", "score": 3.9, "out_of": 5 } ] } }] + \
    5000 * [{ "metadata": { "accommodation_id": -1, "external_id": 1, "partner": "getaway" }, "accommodation": { "name": "Heartbreak Hotel", "address": "Lonely Street", "country": "United States", "postal_code": "37501", "phone": "+1 901-555-7300", "checkin": { "from": "15:00", "until": "midnight" }, "checkout": { "from": "00:00", "until": "12:00" }, "geo": { "longitude": 35.14, "latitude": "-90" }, "ratings": [ { "aspect": "general", "score": 2.5 }, { "aspect": "loneliness", "score": 1.8, "out_of": 5 }, { "aspect": "staff", "score": 6.9, "out_of": 5 } ] } }]

elapsed_time = timeit.timeit('for document in documents: validate(schema, document)', globals=globals(), number=10)
print(elapsed_time)
```

I should develop a suite of performance tests that are clean enough to commit to the repository and that cover multiple use cases. For example, a schema with only top-level elements, a deeply-nested schema, a schema with a lot of lists, completely valid documents, completely invalid documents, broken schemas, etc. Not only would that be helpful for further performance optimizations, it would also make for a good regression test.

At some point, I should read through the code again and document how it works. The code itself is reasonably clean, but the higher level concepts of the algorithm aren't immediately apparent. If only I had kept a development log...

## Nullable fields

I forgot to add support for nullable fields. What should the result of the following validation be?

```python
from okay import validate, Message
from okay.schema import *

def schema():
    required('accommodation', type='object')
    optional('metadata', type='object')

document = {
    'accommodation': None,
    'metadata': None
}

messages = validate(schema, document)
print(messages)
```

At the moment, validation fails for both fields, because `None` is not of type `object`. Don't let that fool you into thinking that fields are non-nullable by default, though. The following example is similar to the one above, but I removed the types from the schema.

```python
from okay import validate, Message
from okay.schema import *

def schema():
    required('accommodation')
    optional('metadata')

document = {
    'accommodation': None,
    'metadata': None
}

messages = validate(schema, document)
print(messages)
```

In this case, both fields pass validation, because there's no check done against the type of the value. This behavior is not by design; it's just a by-product of the current implementation. It's also not very intuitive. So, time to add proper support for nullable values. I need two questions answered: how do you indicate a field is nullable, and what should the default be?

Before I get to answering those questions, a note about the term _nullable_. Python doesn't have null-values, it has None-values, so maybe we should talk about noneable fields. However, the validator is supposed to be document format agnostic (which is also the reason types don't conform to any specific language or format). `null` is far more common than `None`, so I prefer the term _nullable_ over _noneable_ or any other variant.

### Default nullability

The current defaults make no sense: fields are non-nullable if you specify a type, but nullable if you don't. I don't know yet what the defaults should be, but not this. Unfortunately, changing the defaults means that implementing nullability will be a breaking change. That's unavoidable, I'm afraid.

Without thinking it through, my initial expectation would be that optional fields are nullable by default and required fields are non-nullable by default. It'd be nicer to have one default for all fields, but before I get worked up over that, let's see if my initial expectation makes any sense.

First the default for optional fields. Consider the following schema and document.

```python
def book_schema():
    required('title', type='string')
    optional('author', type='object')
    required('author.name', type='string')
    optional('page_count', type='int')

document = {
    'title': 'Epic of Gilgamesh',
    'author': None,
    'page_count': None
}
```

I don't see a clear-cut solution here. Personally, for an object like `author`, I have no problem with accepting null by default, but for a type like `int` it feels weird. That probably has more to do with years of programming in C and C++ than with any objective argument, though. Also, having the default depend on the type is bound to be confusing.

What is the safer option? Well, by default, don't accept null. You forget to specify nullability, all your documents fail, but you inspect the problem and fix your schema. If, on the other hand, nullable is the default, fields that shouldn't be null but are still pass validation and you'll never know.

A practical consideration: not all formats make the distinction between fields that are absent and fields that are null. Avro and CSV, for example, don't. When you convert documents in these formats to a Python dictionary, you can either leave out the empty fields, or add them with a `None` value. If you leave them out, the nullability doesn't matter. If you make them `None`, they will all fail validation unless they're nullable by default.

So, now we have a good argument that nullable should be the default, and a good argument that non-nullable should be the default. Great. Let's distract ourselves from this conundrum by looking at the default for required fields.

```python
def book_schema():
    required('title', type='string')
    required('author', type='object')
    required('author.name', type='string')
    required('page_count', type='int')

document = {
    'title': None,
    'author': None,
    'page_count': None
}
```

That document doesn't look like a valid book to me. I think the case where a field is required, but you want it to be nullable is rare, so that should not be the default.

What about formats that don't distinguish between absent fields and fields that are null? Again, if the absent fields aren't added to the dictionary, nullability doesn't matter. However, if an absent field is represented by a null-value, you don't want it to be accepted by default, so required fields should be non-nullable unless otherwise indicated.

The default for required fields is clear now: non-nullable. I'm tempted to say that this tips the balance for optional fields in favor of non-nullable, too, because then we have one default for both, but I think the case for formats like Avro and CSV is stronger: by default, an absent field is the same as a field with a null-value.

### Specifying nullability

There are three variations for specifying nullability that come to mind.

* A validation function.

```python
required('accommodation', type='object')
nullable('metadata', type='object')
```

* A modified type specification.

```python
required('accommodation', type='object')
optional('metadata', type='object?')
```

* A parameter.

```python
required('accommodation', type='object', nullable=False)
optional('metadata', type='object', nullable=True)
```

At first, I thought that required fields could never be nullable and that's where the idea of the `nullable()` validation function came from, but I changed my mind: you can have a nullable required field. That rules out the extra validation function, unless I'm willing to add two different validation functions – `required_nullable()` and `optional_nullable()` – which I'm not.

The parameter option seems simple enough. It is a bit verbose for my taste, although that doesn't really matter if you use the default nullability most of the time. That does require that you know what the default nullability is and here it's unfortunate that the default is different for required and optional fields. You might decide to always include the `nullable` argument just for clarity and now things are verbose again.

The modified type is clear and concise. It does violate the idea the optional fields should be nullable by default, but considering that it was a judgment call anyway and that adding a `?` to the type is so easy to do, I don't think it's a big deal.

What might be a big deal, though, is the fact that you can't specify nullability without also specifying a type. In trying to come up with a case where you would want to do that, I remembered the idea I had for [allowing multiple types for a single field](#multiple-types). Say you want to indicate that a field can be either a string or a number. One option I came up with is the use of the `possible()` validation function.

```python
def schema():
    optional('latitude')
    possible('latitude', type='number')
    possible('latitude', type='string', regex='-?\d+(?:\.\d+)?')
```

I never implemented this and maybe there's a better way of dealing with the issue, but let's say we want to go with it. How would you indicate that `latitude` can be nullable? You could do it in one of the possible types, but then really all of them should be nullable or it's just confusing. I mean, what would you expect this schema to do?

```python
def schema():
    optional('latitude')
    possible('latitude', type='number')
    possible('latitude', type='string?', regex='-?\d+(?:\.\d+)?')
```

Using a `nullable` parameter is much clearer.

```python
def schema():
    optional('latitude', nullable=True)
    possible('latitude', type='number')
    possible('latitude', type='string', regex='-?\d+(?:\.\d+)?')
```

Is this enough to drop modified types? I actually like the modified type slightly better than the parameter and right now, the only case against it is a hypothetical feature. Well, the feature isn't hypothetical, the implementation is. But the implementation looks so nice. Maybe we could use the modified type and make the example above the exception. Ugh no, then we have two different ways to do the same thing; that won't do.

I thought of another scenario where you may want to add a field without specifying a type: when you don't care what the field contains. Say you have a JSON document that has a field `custom_data` that allows the user to store anything they want. The schema would look something like this.

```python
def schema():
    required('id', type='number')
    required('title', type='string')
    optional('custom_data', nullable=False)
```

Well, that does it: we need to be able to specify nullability without type, so a parameter it will be.

### Reporting null-values

In the current implementation, when a field is null while it's not allowed to be, you get a message of type `invalid_type`. I don't like this very much, because it doesn't allow you to distinguish between an actual value with the wrong type, and null. Instead, I think it's better to add a new message type `null_value`. This is another reason implementing nullability will be a breaking change, but we passed that point already anyway.