# Design Log

Since I don't plan to develop and maintain this project for very long, I'll keep a log of the design considerations that went into this validator, so that anyone interested in taking it over, knows where I'm coming from. If you find yourself asking _what was he thinking?_, you should read this log.

* [Background](#background)
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
* [Validation](#validation)
  * [Extra fields](#extra-fields)
  * [Nested fields](#nested-fields)
* [Data types](#data-types)
  * [Lists](#lists)
  * [Multiple types](#multiple-types)

## Background

Scrapinghub sent us a sample of a thousand accommodations in JSON Lines format. We needed to check if the adhered to the schema we agreed upon with them, so I put together a simple validator and it served it's purpose. It was a fun little project and I now I want to expand on it. I have some nice ideas for improvements, but if I'm putting in the effort, I might as well make it useful in the long term. Since the original validator was a quick, one-off project, I didn't bother with things like unit tests or even version control. So, I'm starting from scratch, doing it right (or at least better) this time.

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
    validator.required('accommodation.geo.latitude').type('string').regex=(number_pattern)
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
validator.required('accommodation').type('object')
validator.required('.name').type('string')
validator.optional('accommodation.geo').type('object')
validator.required('.longitude').type('string').regex(number_pattern)
validator.required('.latitude').type('string').regex=(number_pattern)
validator.optional('accommodation.images').type('list of object')
validator.optional('.size').type('number').minimum(0)
validator.optional('.url').type('string').regex(url_pattern)
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

## Validation

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

Then there's the question of which data types to support. Do we want a generic data type or will we make the distinction between integers and floating-point numbers? Should we have a separate data type for URLs or is it enough to have a string type with a regular expression? It's hard to get it right from the get-go, so it's useful if adding a new data type is relatively easy. When it comes to picking which data types to implement first, I think it makes sense to start with the generic and work towards the specific. For example, I'll implement the string type before the URL type, because you can validate URLs with the string type, but you can't validate strings with the URL type.

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

It requires an extra line, but it's unambiguous and technically correct. It's also an extra reason to use square brackets. `scores[]` now means: an element in the list `score`. Interestingly enough, with this option, if you don't have validation parameters for the list, you don't need to validate the list itself. The following is perfectly clear.

```python
validator.required('scores[]', type='number', min=0, max=10)
```

As stated before, I expect this to be the more common case, so the extra line might not be a big deal. There is another potential problem, though.

```python
validator.required('scores', type='list of number', min=1)
validator.optional('scores[]', type='number', min=0, max=10)
```

Once the list is defined as required, it makes little sense to make the elements optional. The same goes for the inverse: if the list if optional, making the elements required has no meaning. In other words, optional or required always refers to the list, not to its elements. So, what do we do if there's a conflict? I guess we can treat the list as required – as that is the safest option – and issue a warning.

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