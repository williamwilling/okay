# Reference Manual

* [Functions](#functions)
  * [ignore_extra_fields](#ignore-extra-fields)
  * [optional](#optional)
  * [required](#required)
  * [validate](#validate)
* [Classes](#classes)
  * [Message](#message)
  * [SchemaError](#schema-error)
* [Type validators](#type-validators)
  * [any](#any)
  * [bool](#bool)
  * [custom](#custom)
  * [int](#int)
  * [list](#list)
  * [number](#number)
  * [object](#object)
  * [string](#string)
* [Validaton messages](#validation-messages)
  * [invalid_number_option](#invalid_number_option)
  * [invalid_string_option](#invalid_string_option)
  * [invalid_type](#invalid_type)
  * [no_match](#no_match)
  * [null_value](#null_value)
  * [number_too_large](#number_too_large)
  * [number_too_small](#number_too_small)
  * [too_few_elements](#too_few_elements)
  * [too_many_elements](#too_many_elements)

## Functions

### ignore_extra_fields

You use `ignore_extra_fields()` inside a [schema definition](user-guide.md#writing-a-schema) to tell the validator to accept any field that you didn't explicitly define using [`optional()`](#optional) or [`required()`](#required). By default, the validator will report any such field, so `ignore_extra_fields()` will turn reporting extra fields off.

`ignore_extra_fields()` has no parameters and no return value.

### optional

You use `optional()` inside a [schema definition](user-guide.md#writing-a-schema) to indicate that a field is allowed to be in a document, but it's fine if the field is missing.

`optional()` has no return value.

Parameter   | Description
------------|------------
`field`     | Required. The name of the field you want to validate. You can specify [nested fields](user-guide.md#nested-fields) using the `.` separator, e.g. `author.last_name`. You can specify [list elements](user-guide.md#lists) using the `[]` suffix, e.g. `genres[]`.
`type`      | Optional. The [type](#type-validators) the field should have.

Depending on the [type](#type-validators) you specify, you can pass extra named parameters to `optional()`. For example, if a field is of type `string`, you can pass a `regex` parameter. You should not use parameters that aren't documented for the type validator, because later versions of Okay may introduce new parameters and they won't be considered a breaking change.

### required

You use `required()` inside a [schema definition](user-guide.md#writing-a-schema) to indicate that a field must be in a document.

`required()` has no return value.

Parameter | Description
----------|------------
`field`   | Required. The name of the field you want to validate. You can specify [nested fields](user-guide.md#nested-fields) using the `.` separator, e.g. `author.last_name`. You can specify [list elements](user-guide.md#lists) using the `[]` suffix, e.g. `genres[]`.
`type`    | Optional. The [type](#type-validators) the field should have.

Depending on the [type](#type-validators) you specify, you can pass extra named parameters to `optional()`. For example, if a field is of type `string`, you can pass a `regex` parameter. You should not use parameters that aren't documented for the type validator, because later versions of Okay may introduce new parameters and they won't be considered a breaking change.

### validate

Runs the validator on the specified document using the specified schema.

`validate()` returns a list of `Message` objects, where each object indicates a validation error in the document.

Parameter        | Description
-----------------|------------
`schema`         | Required. The [schema definition](user-guide.md#writing-a-schema). This must be a function that accepts no parameters and returns no value. Okay gives no guarantees about when or how often this function will be called.
`document`       | Required. The document you want to validate. This must be a `dict`.
`message_values` | Optional. A dictionary with key-value pairs that the validator will add to all `Message` objects it produces.

## Classes

### Message

Represents a validation message, giving information about a validation error.

Each `Message` object has a `type` property, but beyond that, the available properties depend on the [validation message type](#validation-messages). The table below lists properties used by Okay, but custom validation messages may contain any property.

Property   | Description
-----------|------------
`type`     | Required. A string indicating why validation failed. Okay uses a limited set of [validation message types](#validation-message), but you are free to create any type you want.
`field`    | Optional. The name of the field that failed validation. This is present in all validation messages Okay produces, but you have the option to create a `Message` object without it, for example to indicate that a document failed to parse.
`expected` | Optional. Contains the original validation parameters. The exact content is different for each type of [validation message]((#validation-message)).

### SchemaError

The exception raised when there's a problem with the [schema definition](user-guide.md#writing-a-schema), for example a bug in a [custom validator](user-guide.md#custom-validators), or an invalid [validation type](#type-validators). If `SchemaError` was raised in response to another exception, that other exception is available from the `__cause__` property of the `SchemaError` instance.

## Type validators

You should not pass parameters that aren't listed here to type validators. Future versions of Okay may introduce new parameters, which is not considered a breaking change.

### any

The value can be of any type. This is the same as not specifying a type, unless you make it nullable.

### bool

The value must be a boolean, i.e. either `True` or `False`.

### custom

The value must pass validation as specified by a [custom validator](user-guide.md#custom-validators). This is useful when Okay's provided type validators don't fit your use case and you want to write your own validation logic.

Parameter   | Description
------------|------------
`validator` | Required. The function that will validate the value. It must accept two parameters: the field name and the field value. Additionally, it can accept any number of keyword arguments. It must return `None` if validation succeeds or a [`Message`](#message) object if validation fails.

### int

The value must be a whole number. In terms of Python types, any `int` will fit the bill, and it's also fine if the value is a `float`, as long as the fractional part is 0.

Parameter  | Description
-----------|------------
`min`      | The smallest allowed value.
`max`      | The largest allowed value.
`options`  | A list of allowed values. The value must exactly match one of the options.

If `min` is larger than `max`, the behavior of the type validator is undefined.

A field is valid if it either is in range according to `min` and `max`, or it matches one of the `options`. If an integer fails validation, it will result in a [`number_too_small`](#number_too_small) or [`number_too_large`](#number_too_large) message if `min` or `max` are present, and otherwise an [`invalid_number_option`](#invalid_number_option) message.

If you want the integer to match both checks, you should add them to your schema as two separate validation rules. For example:

```python
def schema():
  required('root', type='number', options=[x * x for x in range(1, 1000)])
  required('root', type='number', min=100, max=20000)
```

### list

The value must be a list.

Parameter  | Description
-----------|------------
`min`      | The smallest allowed list size.
`max`      | The largest allowed list size.

If `min` is larger than `max`, the behavior of the type validator is undefined.

### number

The value must be a number. In terms of Python types, any `int`, `float`, or `Decimal` will do.

Parameter  | Description
-----------|------------
`min`      | The smallest allowed value.
`max`      | The largest allowed value.
`options`  | A list of allowed values. The value must exactly match one of the options.

If `min` is larger than `max`, the behavior of the type validator is undefined.

A field is valid if it either is in range according to `min` and `max`, or it matches one of the `options`. If a number fails validation, it will result in a [`number_too_small`](#number_too_small) or [`number_too_large`](#number_too_large) message if `min` or `max` are present, and otherwise an [`invalid_number_option`](#invalid_number_option) message.

If you want the number to match both checks, you should add them to your schema as two separate validation rules. For example:

```python
import math

def schema():
  required('square', type='number', options=[math.sqrt(x) for x in range(1, 1000)])
  required('square', type='number', min=10, max=20)
```

### object

The value must be an object, i.e. a Python `dict`.

### string

The value must be a string. It's not good enough if the value can be converted to a string, it must actually be of type `str`.

Parameter        | Description
-----------------|------------
`regex`          | The regular expression pattern that the value must match.
`options`        | A list of allowed values. The value must exactly match one of the options.
`case_sensitive` | `True` if options are case sensitive, `False` otherwise. Default is `True`. Note that `case_sensitive` doesn't apply to regular expressions. If you want your regular expression to be case insensitive, add the [inline flag](https://docs.python.org/3/library/re.html#index-15) `(?i)` to your pattern.
`max`            | The largest allowed length of the string.
`min`            | The smallest allowed length of the string.

If `min` is larger than `max`, the behavior of the type validator is undefined.

A field is valid if it either is in range according to `min` and `max`, or it matches `regex`, or it matches one of the `options`. If a string fails validation, it will result in a [`no_match`](#no_match) message if `regex` is present, otherwise a [`string_too_short`](#string_too_short) or [`string_too_long`](#string_too_long) message if `min` or `max` are present, and otherwise an [`invalid_string_option`](#invalid_string_option) message.

If you want the string to match all three checks, you should add them to your schema as three separate validation rules. For example:

```python
def schema():
  required('color', type='string', options=['red', '#f00', '#ff0000'])  # it must be a pre-approved color
  required('color', type='string', regex=r'#[\da-f]+')                  # it must be in hex format
  required('color', type='string', min=4, max=4)                        # it must be in short format
```

## Validation messages

You should ignore any validation message field that isn't listed here. Future versions of Okay may add new fields to validation messages, which is not considered a breaking change. If you [pass custom validation fields to the validator](user-guide.md#identifying-documents), they'll overwrite a validation message's regular fields, so even if a future version of Okay adds a validation field with the same name as your custom field, this will not break your code.

### invalid_number_option

The field doesn't match any of the allowed numbers.

Property                     | Description
-----------------------------|------------
`type`                       | `invalid_number_option`
`field`                      | The name of the field that failed validation.
`expected['options']`        | The list of acceptable numbers.
`expected['max']`            | Always `None` for this message type.
`expected['min']`            | Always `None` for this message type.

### invalid_string_option

The field doesn't match any of the allowed strings.

Property                     | Description
-----------------------------|------------
`type`                       | `invalid_string_option`
`field`                      | The name of the field that failed validation.
`expected['options']`        | The list of acceptable strings.
`expected['case_sensitive']` | `True` if the options are case-sensitive, `False` if they aren't.
`expected['max']`            | Always `None` for this message type.
`expected['min']`            | Always `None` for this message type.
`expected['regex']`          | Always `None` for this message type.

### invalid_type

The field doesn't match the specified type.

Property           | Description
-------------------|------------
`type`             | `invalid_type`
`field`            | The name of the field that failed validation.
`expected['type']` | The name of the type the field should have.

### no_match

The field doesn't match the required regular expression.

Property                     | Description
-----------------------------|------------
`type`                       | `no_match`
`field`                      | The name of the field that failed validation.
`expected['regex']`          | The regular expression that the string should match.
`expected['max']`            | The maximum number of characters in the string, or `None` if not specified.
`expected['min']`            | The minimum number of characters in the string, or `None` if not specified.
`expected['options']`        | The list of acceptable strings, or `None` if not specified.
`expected['case_sensitive']` | `True` if the options are case-sensitive, `False` if they aren't, or `None` if options weren't specified.

### null_value

The fields contains `null`, even though it's not allowed to.

Property           | Description
-------------------|------------
`type`             | `null_value`
`field`            | The name of the field that failed validation.
`expected['type']` | The expected type of the field. Only present if a type was specified for the field.

### number_too_large

The field contains a number larger than the allowed maximum.

Property              | Description
----------------------|------------
`type`                | `number_too_large`
`field`               | The name of the field that failed validation.
`expected['max']`     | The maximum value allowed.
`expected['min']`     | The minimum value allowed, or `None` if not specified.
`expected['options']` | The list of acceptable numbers, or `None` if not specified.

### number_too_small

The field contains a number smaller than the allowed minimum.

Property              | Description
----------------------|------------
`type`                | `number_too_small`
`field`               | The name of the field that failed validation.
`expected['max']`     | The maximum value allowed, or `None` if not specified.
`expected['min']`     | The minimum value allowed.
`expected['options']` | The list of acceptable numbers, or `None` if not specified.

### string_too_long

The field contains string that consists of too many characters.

Property                     | Description
-----------------------------|------------
`type`                       | `string_too_long`
`field`                      | The name of the field that failed validation.
`expected['max']`            | The maximum number of characters in the string.
`expected['min']`            | The minimum number of characters in the string, or `None` if not specified.
`expected['options']`        | The list of acceptable strings, or `None` if not specified.
`expected['case_sensitive']` | `True` if the options are case-sensitive, `False` if the aren't, or `None` if options weren't specified.
`expected['regex']`          | Always `None` for this message type.

### string_too_short

The field contains a string that consists of too few characters.

Property                     | Description
-----------------------------|------------
`type`                       | `string_too_short`
`field`                      | The name of the field that failed validation.
`expected['min']`            | The minimum number of characters in the string.
`expected['max']`            | The maximum number of characters in the string, or `None` if not specified.
`expected['options']`        | The list of acceptable strings, or `None` if not specified.
`expected['case_sensitive']` | `True` if the options are case-sensitive, `False` if they aren't, or `None` if options weren't specified.
`expected['regex']`          | Always `None` for this message type.

### too_few_elements

The list contains fewer elements than the allowed minimum.

Property          | Description
------------------|------------
`type`            | `too_few_elements`
`field`           | The name of the field that failed validation.
`expected['min']` | The minimum number of elements the list should have.
`expected['max']` | The maximum number of elements the list may have, or `None` if not specified.

### too_many_elements

The list contains more elements than the allowed maximum.

Property          | Description
------------------|------------
`type`            | `too_many_elements`
`field`           | The name of the field that failed validation.
`expected['max']` | The maximum number of elements the list may have.
`expected['min']` | The minimum number of elements the list should have, or `None` if not specified.
